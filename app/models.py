from typing import Optional

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field


class ItemBase(SQLModel):              # 공통 필드 (상속 베이스, table 아님)
    name: str
    price: float
    in_stock: bool = True


class Item(ItemBase, table=True):      # 테이블
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")    # 소유자 (어느 유저 것인지)


class ItemCreate(ItemBase):            # 입력: id 없음 (클라가 id 못 보냄)
    model_config = ConfigDict(extra="forbid")   # 정의 안 된 필드 오면 거절


class ItemPublic(ItemBase):            # 응답: id + 소유자
    id: int
    user_id: int


class ItemUpdate(SQLModel):            # 부분수정: 전부 Optional
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    model_config = ConfigDict(extra="forbid")


# ── User ──────────────────────────────────
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str               # 평문 아니라 "해시"만 저장


class UserCreate(SQLModel):            # 입력: 평문 password 받음 (받기만)
    username: str
    password: str
    model_config = ConfigDict(extra="forbid")


class UserPublic(SQLModel):            # 응답: 비번 필드 아예 없음
    id: int
    username: str


class LoginRequest(SQLModel):          # 로그인 입력
    username: str
    password: str
    model_config = ConfigDict(extra="forbid")


class Token(SQLModel):                 # 로그인 응답: 발급된 토큰
    access_token: str
    token_type: str = "bearer"
