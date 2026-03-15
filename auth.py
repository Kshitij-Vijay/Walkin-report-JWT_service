import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import *

def hash_password(password: str):
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode("utf-8")

def verify_password(password: str, hashed: str):
    password = password.encode("utf-8")
    return bcrypt.checkpw(password, hashed.encode("utf-8"))

def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token