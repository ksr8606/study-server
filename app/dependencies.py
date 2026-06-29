import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.security import decode_access_token

# Authorization: Bearer <토큰> 헤더에서 토큰을 꺼내주는 스킴
bearer_scheme = HTTPBearer()


# 토큰 → 현재 로그인한 User. 보호할 엔드포인트에 Depends(get_current_user) 로 붙임
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        username = decode_access_token(creds.credentials)
    except jwt.InvalidTokenError:                       # 서명 틀림·만료 등 모두 여기로
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않아")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없어")
    return user
