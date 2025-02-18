from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import JWTError, jwt
import os
import base64
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import load_pem_private_key

router = APIRouter()

# Load keys from environment variables
PRIVATE_KEY_PEM = os.environ['JWT_PRIVATE_KEY'].encode('utf-8')
PUBLIC_KEY_PEM = os.environ['JWT_PUBLIC_KEY'].encode('utf-8')

# Load the private key
private_key = load_pem_private_key(PRIVATE_KEY_PEM, password=None)

# Load the public key from the certificate
cert = load_pem_x509_certificate(PUBLIC_KEY_PEM)
public_key = cert.public_key()

ALGORITHM = "RS256"
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
