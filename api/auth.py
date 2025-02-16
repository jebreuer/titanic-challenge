from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import JWTError, jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

router = APIRouter()

# Generate key pair (in production, load from secure storage)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Convert to PEM format
PRIVATE_KEY_PEM = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

PUBLIC_KEY_PEM = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Algorithm changed to RS256
ALGORITHM = "RS256"

# Update issuer to match the RequestAuthentication policy
ISSUER = "http://titanic-api.titanic-challenge.svc.cluster.local:8000"

DEMO_USERS = {
    "analyst": {
        "password": "demo123",
        "role": "data-analyst"
    },
    "viewer": {
        "password": "demo123",
        "role": "viewer"
    }
}

@router.post("/token")
async def login(username: str, password: str):
    user = DEMO_USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {
            "sub": username,
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iss": ISSUER
        },
        PRIVATE_KEY_PEM,
        algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/.well-known/jwks.json")
async def jwks():
    # Convert public key to JWKS format
    public_numbers = public_key.public_numbers()
    n = base64.urlsafe_b64encode(public_numbers.n.to_bytes(256, 'big')).rstrip(b'=')
    e = base64.urlsafe_b64encode(public_numbers.e.to_bytes(3, 'big')).rstrip(b'=')
    
    return {
        "keys": [
            {
                "kid": "default-key",
                "kty": "RSA",
                "alg": ALGORITHM,
                "use": "sig",
                "n": n.decode('ascii'),
                "e": e.decode('ascii')
            }
        ]
    }
