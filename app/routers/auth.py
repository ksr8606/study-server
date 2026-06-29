from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, LoginRequest, Token
from app.security import verify_password, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.username == credentials.username)
    ).first()
    # 아이디 없음 / 비번 틀림을 구분하지 않음 — 공격자에게 "그 아이디는 존재한다" 힌트를 안 줌
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸어")
    return Token(access_token=create_access_token(user.username))
