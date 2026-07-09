from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


# 비밀번호를 단방향 해시로 변환 (gensalt 으로 매번 다른 salt → 같은 비번도 해시 다름)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# 평문 비번 ↔ 저장된 해시 비교 (해시는 단방향이라 입력을 또 해시해서 맞춰봄)
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# JWT 발급: payload(누구·만료)를 SECRET_KEY 로 서명한 토큰 문자열 반환
def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # sub=누구, exp=만료시각
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


# 토큰 검증 후 username(sub) 반환 — 서명·만료가 안 맞으면 jwt 예외 발생
def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    return payload["sub"]
