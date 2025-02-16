from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import JWTError, jwt

router = APIRouter()

# In production, use proper secret key management
SECRET_KEY = "demo-secret-key"
ALGORITHM = "HS256"

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
            "exp": datetime.utcnow() + timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/.well-known/jwks.json")
async def jwks():
    return {
        "keys": [
            {
                "kid": "demo-key",
                "kty": "oct",
                "k": SECRET_KEY,
                "alg": ALGORITHM
            }
        ]
    }
