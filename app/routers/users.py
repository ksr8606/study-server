from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import User, UserCreate, UserPublic
from app.security import hash_password
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserPublic)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),   # 평문 → 해시로 변환해서 저장
    )
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"이미 있는 username: {user.username}")
    session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user        # get_current_user 가 토큰 검증 → User 주입 (없으면 401)
