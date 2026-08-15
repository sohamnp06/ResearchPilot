from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    email_verified: bool


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    verification_code: str


class VerifyEmailResponse(BaseModel):
    message: str

class ResendOTPRequest(BaseModel):
    email: EmailStr


class ResendOTPResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    email_verified: bool