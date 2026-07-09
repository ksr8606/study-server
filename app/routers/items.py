from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.dependencies import get_current_user
from app.models import User, Item, ItemCreate, ItemPublic, ItemUpdate, ItemWithOwner

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemPublic)
def create_item(
    item: ItemCreate,
    session: Session = Depends(get_session),
    # 로그인 필수
    current_user: User = Depends(get_current_user),
):
    # 소유자 = 나
    db_item = Item(**item.model_dump(), user_id=current_user.id)
    session.add(db_item)
    commit_or_409(session, item.name)
    session.refresh(db_item)
    return db_item


@router.get("", response_model=list[ItemWithOwner])
def list_items(
    session: Session = Depends(get_session),
    # 이름 검색 (부분 일치)
    q: Optional[str] = None,
    # 재고 필터
    in_stock: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    # 건너뛸 개수 (페이지네이션)
    skip: int = 0,
    # 가져올 개수 (최대 100 제한)
    limit: int = Query(default=20, le=100),
):
    # owner를 미리 로드 (N+1 방지)
    query = select(Item).options(selectinload(Item.owner))

    if q is not None:
        # SQL: name LIKE '%q%'
        query = query.where(Item.name.contains(q))
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
    # 404 + 소유권(403) 확인
    item = get_owned_item_or_404_or_403(item_id, session, current_user)
    # 클라가 실제 보낸 필드만 추출
    data = patch.model_dump(exclude_unset=True)
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


@router.post("/{item_id}/purchase")
def purchase_item(item_id: int, session: Session = Depends(get_session)):
    # 1. 읽기
    item = get_item_or_404(item_id, session)
    if item.stock <=0:
        raise HTTPException(status_code=409, detail="품절")
    # 2. 계산 (파이썬 메모리에서)
    item.stock -= 1
    session.add(item)
    # 3. 쓰기
    session.commit()
    return {"item_id": item_id, "stock": item.stock}


@router.post("/{item_id}/purchase/db")
def purchase_item_by_db(item_id: int, session: Session = Depends(get_session)):
    item = get_item_or_404(item_id, session)
    # DB가 "재고>0 확인 + 1 차감"을 한 문장으로 원자적 처리 (읽고-쓰기 틈이 없음)
    stmt = (
        sa_update(Item)
        .where(Item.id == item.id, Item.stock > 0)
        .values(stock=Item.stock - 1)
    )
    result = session.execute(stmt)
    session.commit()
    # 0줄 바뀜 = 재고 0이거나 없는 item
    if result.rowcount == 0:
        raise HTTPException(status_code=409, detail="품절 또는 없는 item")
    return {"item_id": item_id, "ok": True}


@router.post("/{item_id}/purchase/lock")
def purchase_item_by_lock(item_id: int, session: Session = Depends(get_session)):
    item = get_item_or_404(item_id, session)
    # with_for_update() = SELECT ... FOR UPDATE → 이 행을 잠금 (다른 트랜잭션은 대기)
    item = session.exec(
        select(Item)
        .where(Item.id == item.id)
        .with_for_update()
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="없는 item")
    if item.stock <= 0:
        raise HTTPException(status_code=409, detail="품절")
    item.stock -= 1
    session.add(item)
    # 커밋하면서 락 해제 → 대기하던 다음 요청이 진행
    session.commit()
    return {"item_id": item_id, "stock": item.stock}


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
