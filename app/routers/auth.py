from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.services import auth_service
from app.schemas.user import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db=db, user_data=user)



@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    from app.schemas.user import UserLogin
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return auth_service.authenticate_user(db=db, user_data=user_data)