from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


def register_user(db: Session, user_data: UserCreate) -> dict:
    # check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    existing_user = db.scalars(stmt).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # hash password and create user
    hashed = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # create and return token
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(db: Session, user_data: UserLogin) -> dict:
    # find user by email
    stmt = select(User).where(User.email == user_data.email)
    user = db.scalars(stmt).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # create and return token
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}