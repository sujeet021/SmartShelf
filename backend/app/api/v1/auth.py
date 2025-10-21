from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Simple in-memory fake user database (for testing only)
fake_users_db = {
    "admin": {
        "username": "admin",
        "password_hash": get_password_hash("admin123"),  # keep password short for bcrypt
        "role": "admin"
    }
}

class LoginIn(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginIn):
    user = fake_users_db.get(data.username)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user["username"])
    return {"access_token": token, "token_type": "bearer"}
