from typing import Optional

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship


# 공통 필드 (상속 베이스, table 아님)
class ItemBase(SQLModel):
    name: str
    price: float
    in_stock: bool = True
    # 재고 수량
    stock: int = 0


# 테이블
class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # 소유자 (어느 유저 것인지)
    user_id: int = Field(foreign_key="user.id")
    # N:1 — 이 아이템의 주인
    owner: Optional["User"] = Relationship(back_populates="items")


# 입력: id 없음 (클라가 id 못 보냄)
class ItemCreate(ItemBase):
    # 정의 안 된 필드 오면 거절
    model_config = ConfigDict(extra="forbid")


# 응답: id + 소유자
class ItemPublic(ItemBase):
    id: int
    user_id: int


# ItemPublic + 주인 정보
class ItemWithOwner(ItemPublic):
    owner: "UserPublic"


# 부분수정: 전부 Optional
class ItemUpdate(SQLModel):
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    model_config = ConfigDict(extra="forbid")


# ── User ──────────────────────────────────
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    # 평문 아니라 "해시"만 저장
    hashed_password: str
    # 1:N — 이 유저의 아이템들
    items: list["Item"] = Relationship(back_populates="owner")


# 입력: 평문 password 받음 (받기만)
class UserCreate(SQLModel):
    username: str
    password: str
    model_config = ConfigDict(extra="forbid")


# 응답: 비번 필드 아예 없음
class UserPublic(SQLModel):
    id: int
    username: str


# 로그인 입력
class LoginRequest(SQLModel):
    username: str
    password: str
    model_config = ConfigDict(extra="forbid")


# 로그인 응답: 발급된 토큰
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
