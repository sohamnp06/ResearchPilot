from datetime import datetime, timedelta, timezone
import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.core.dependencies import get_current_user

from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    LoginRequest,
    LoginResponse,
    CurrentUserResponse
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.core.email import send_verification_email


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# SIGNUP
# =========================

@router.post(
    "/signup",
    response_model=SignupResponse
)
async def signup(
    user_data: SignupRequest,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate 6-digit verification code
    verification_code = str(
        random.randint(100000, 999999)
    )

    # OTP expires after 10 minutes
    verification_expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    # Hash password
    hashed_password = hash_password(
        user_data.password
    )

    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        email_verified=False,
        verification_code=verification_code,
        verification_expires=verification_expires
    )

    # Save user
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    await send_verification_email(
        new_user.email,
        verification_code,
        verification_expires
    )

    return new_user


# =========================
# VERIFY EMAIL
# =========================

@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse
)
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    # Find user by email
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Check if verification code exists
    if not user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found"
        )

    # Check if expiry exists
    if not user.verification_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired"
        )

    # Current UTC time
    now = datetime.now(timezone.utc)

    # Handle a naive datetime returned by the database
    expiry = user.verification_expires

    if expiry.tzinfo is None:
        expiry = expiry.replace(
            tzinfo=timezone.utc
        )

    # Check OTP expiry
    if now > expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired"
        )

    # Check OTP
    if user.verification_code != data.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    # Email successfully verified
    user.email_verified = True

    # Remove OTP after successful verification
    user.verification_code = None
    user.verification_expires = None

    db.commit()

    return {
        "message": "Email verified successfully"
    }

@router.post(
    "/resend-otp",
    response_model=ResendOTPResponse
)
async def resend_otp(
    data: ResendOTPRequest,
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Don't send OTP if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Generate new OTP
    verification_code = str(
        random.randint(100000, 999999)
    )

    # New OTP expires after 10 minutes
    verification_expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    # Update user
    user.verification_code = verification_code
    user.verification_expires = verification_expires

    db.commit()
    db.refresh(user)

    # Send new OTP
    await send_verification_email(
        user.email,
        verification_code,
        verification_expires
    )

    return {
        "message": "A new verification code has been sent to your email"
    }

@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check password
    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check email verification
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )

    # Generate JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=CurrentUserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user