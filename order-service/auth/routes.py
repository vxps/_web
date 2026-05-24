from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .jwt import create_access_token
import bcrypt

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

USERS = {
    "admin": {
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    user = USERS.get(req.username)
    if not user or not bcrypt.checkpw(req.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": req.username})
    return {"access_token": token, "token_type": "bearer"}