import os
from time import time
from typing import Dict

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")



pwd_context = CryptContext(
schemes=["bcrypt"],
deprecated="auto"
)



def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
plain_password: str,
hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
)



def create_token(cust_id: int) -> Dict[str, str]:
    payload = {
        "cust_id": cust_id,
        "exp": int(time()) + 3600  # 1 Hour Expiry
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# JWT Security Scheme

security = HTTPBearer()

# Get Current Logged-In Customer

def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

    return payload["cust_id"]
