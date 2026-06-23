from typing import Optional
from contextlib import asynccontextmanager

from pydantic import ConfigDict

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy.exc import IntegrityError


# ── 1. 모델 = 테이블 ──────────────────────────────
# table=True 가 붙으면 "이건 DB 테이블"이라는 뜻. (안 붙으면 그냥 Pydantic 모델)
class ItemBase(SQLModel):              # 공통 필드 (상속 베이스, table 아님)
    name: str
    price: float
    in_stock: bool = True

class Item(ItemBase, table=True):      # ← 테이블. id만 추가
    id: Optional[int] = Field(default=None, primary_key=True)
    

class ItemCreate(ItemBase):            # ← 입력: id 없음 (클라가 id 못 보냄)
    pass
    model_config = ConfigDict(extra="forbid")   # 정의 안 된 필드 오면 거절

class ItemPublic(ItemBase):            # ← 응답: id 포함해서 내보냄
    id: int

class ItemUpdate(SQLModel):            # ← 부분수정: 전부 Optional
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    model_config = ConfigDict(extra="forbid")   # 정의 안 된 필드 오면 거절

# ── 2. engine = 앱당 1개, 커넥션 풀 본체 ──────────
# check_same_thread=False : SQLite는 기본적으로 "만든 스레드에서만 써라"고 막는데,
#   FastAPI는 여러 스레드로 요청을 처리해서 이 빗장을 풀어줘야 함 (SQLite + 서버 특유 설정)
# engine = create_engine(
#     "sqlite:///app.db",
#     connect_args={"check_same_thread": False},
# )

# DATABASE_URL = "postgresql+psycopg://postgres:studypass@localhost:5432/studydb"
# engine = create_engine(DATABASE_URL)



# 스키마(테이블) 생성·변경은 이제 Alembic 마이그레이션이 담당 — create_all 은퇴
app = FastAPI()


# ── 4. 세션 의존성 = 요청마다 1개, 자동 정리 ──────
def get_session():
    with Session(engine) as session:   # with 블록 끝나면 세션 자동 close
        yield session                  # yield = "이걸 핸들러한테 빌려주고, 끝나면 회수"


# ── 5. 핸들러 = items_db 딕셔너리 → 세션(DB)로 교체 ──
@app.post("/items", response_model=ItemPublic)        # ← 응답은 이 스키마로 강제
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item.model_validate(item)               # ItemCreate → Item(테이블) 변환
    session.add(db_item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()                 # ★ 반드시 롤백 (안 하면 세션 오염)
        raise HTTPException(
            status_code=409,
            detail=f"add - 이미 존재하는 이름이야: {item.name}",
        )
    session.refresh(db_item)
    return db_item                                    # Item 통째로 줘도 ItemPublic만 통과

@app.get("/items", response_model=list[ItemPublic])
def list_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()   # SELECT * FROM item

@app.get("/items/{item_id}", response_model=list[ItemPublic])
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)         # PK로 단건 조회
    if not item:
        raise HTTPException(status_code=404, detail="해당 item이 없어")
    return item

@app.patch("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, patch: ItemUpdate, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="해당 item이 없어")
    data = patch.model_dump(exclude_unset=True)   # ★ 클라가 실제 보낸 필드만 추출
    for key, value in data.items():
        setattr(item, key, value)
    session.add(item)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()                 # ★ 반드시 롤백 (안 하면 세션 오염)
        raise HTTPException(
            status_code=409,
            detail=f"update - 이미 존재하는 이름이야: {patch.name}",
        )
    session.refresh(item)
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="해당 item이 없어")
    session.delete(item)
    session.commit()
    return {"deleted": item_id}


from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str                                    # 타입 명시 = 자동 검증
    model_config = SettingsConfigDict(env_file=".env")   # .env에서 읽어라

settings = Settings()
engine = create_engine(settings.database_url)