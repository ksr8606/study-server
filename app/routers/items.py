from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.dependencies import get_current_user
from app.models import Item, ItemCreate, ItemPublic, ItemUpdate, User

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=ItemPublic)
def create_item(
    item: ItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),     # 로그인 필수
):
    db_item = Item(**item.model_dump(), user_id=current_user.id)   # 소유자 = 나
    session.add(db_item)
    commit_or_409(session, item.name)
    session.refresh(db_item)
    return db_item


@router.get("", response_model=list[ItemPublic])
def list_items(
    session: Session = Depends(get_session),
    q: Optional[str] = None,                    # 이름 검색 (부분 일치)
    in_stock: Optional[bool] = None,            # 재고 필터
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,                              # 건너뛸 개수 (페이지네이션)
    limit: int = Query(default=20, le=100),     # 가져올 개수 (최대 100 제한)
):
    query = select(Item)
    
    if q is not None:
        query = query.where(Item.name.contains(q))  #SQL: name LIKE '%q%'
    if in_stock is not None:
        query = query.where(Item.in_stock == in_stock)
    if min_price is not None:
        query = query.where(Item.price >= min_price)
    if max_price is not None:
        query = query.where(Item.price <= max_price)
    query = query.offset(skip).limit(limit)

    return session.exec(query).all()


@router.get("/{item_id}", response_model=ItemPublic)
def get_item(item_id: int, session: Session = Depends(get_session)):
    return get_item_or_404(item_id, session)


@router.patch("/{item_id}", response_model=ItemPublic)
def update_item(
    item_id: int,
    patch: ItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = get_owned_item_or_404_or_403(item_id, session, current_user)   # 404 + 소유권(403) 확인
    data = patch.model_dump(exclude_unset=True)   # 클라가 실제 보낸 필드만 추출
    for key, value in data.items():
        setattr(item, key, value)
    session.add(item)
    commit_or_409(session, patch.name)
    session.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = get_owned_item_or_404_or_403(item_id, session, current_user)
    session.delete(item)
    session.commit()
    return {"deleted": item_id}


# ── 공통 헬퍼 ──────────────────────────────
def get_item_or_404(item_id: int, session: Session) -> Item:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="해당 item이 없어")
    return item


# 404 + 소유권(403)까지 확인 — 수정·삭제처럼 "내 것만" 허용할 때
def get_owned_item_or_404_or_403(item_id: int, session: Session, current_user: User) -> Item:
    item = get_item_or_404(item_id, session)
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="내 item이 아니야 (수정/삭제 권한 없음)")
    return item


# 커밋하되 unique 충돌이면 409
# rollback 후 ORM 객체는 만료되므로, 메시지엔 입력값(conflict_name)을 받아 씀
def commit_or_409(session: Session, conflict_name: str):
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"이미 존재하는 이름이야: {conflict_name}")
