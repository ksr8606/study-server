from fastapi import FastAPI

from app.routers import items, users, auth

# 스키마(테이블) 생성·변경은 Alembic 마이그레이션이 담당 (create_all 안 씀)
app = FastAPI()

app.include_router(items.router)
app.include_router(users.router)
app.include_router(auth.router)
