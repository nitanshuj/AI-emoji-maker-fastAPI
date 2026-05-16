from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any


class UserSignUpRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's secure password (min 6 chars)")



class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User details metadata")


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
