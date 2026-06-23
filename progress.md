# 서버 공부 진도 노트

> 오랜만에 와서 까먹었으면 **이 파일부터** 읽으면 돼.

## 📍 작업 위치
`~/study/server/`

## ▶️ 다시 시작하는 법 (3단계)
```bash
# 1. DB(PostgreSQL 컨테이너) 켜기 — 꺼져 있으면 앱이 DB 연결 못 함
docker start study-postgres        # docker ps 로 떠있나 확인 (Up 이면 생략)

# 2. 가상환경 켜기
cd ~/study/server
source .venv/bin/activate

# 3. 서버 켜기
uvicorn app.main:app --reload
```
확인: http://127.0.0.1:8000/docs

## 🧱 현재 스택
**FastAPI + SQLModel + PostgreSQL**
- DB는 Docker 컨테이너 `study-postgres` 로 떠 있음 (`localhost:5432`, DB명 `studydb`)
- ※ `app.db`(SQLite)는 이제 안 씀 — PostgreSQL로 갈아탔음

## ✅ 배운 것
- CRUD ↔ HTTP 메서드 (POST/GET/PATCH/DELETE) ↔ SQL
- HTTP 구조(첫줄/헤더/빈줄/바디), 상태코드 422·404·405·409 차이
- SQLModel: 모델=테이블 / engine(앱당 1개) / session(요청당 1개) / Depends 주입
- 모델 분리: ItemBase·Item(table)·ItemCreate(입력)·ItemPublic(응답)·ItemUpdate
- `response_model`(응답 필터), `extra="forbid"`(모르는 필드 거절)
- unique 제약 + IntegrityError → 409, **rollback 후 ORM 객체는 만료됨**(에러 메시지엔 입력값 patch.name 써라)
- DB 전환: SQLite→PostgreSQL은 **커넥션 문자열만** 바꿈 (핸들러 0줄) = ORM 추상화의 힘
- Docker로 DB 운용: 포트매핑(-p), **볼륨(-v, 데이터 영속화)**, 환경변수(-e)

## 🛠️ 자주 쓰는 명령
```bash
# DB 안에 직접 들어가기 (psql)
docker exec -it study-postgres psql -U postgres -d studydb
#   안에서: \dt (테이블목록)  \q (나가기)

# DB 데이터 한 방에 확인
docker exec -it study-postgres psql -U postgres -d studydb -c "SELECT * FROM item;"

# 컨테이너 상태 / 로그
docker ps
docker logs study-postgres
```

## ⏭️ 다음 할 일
- [ ] 비번 하드코딩 → 환경변수로 분리 (pydantic-settings, .env)  ← **지금 여기**
- [ ] 마이그레이션 (Alembic) — 데이터 살린 채 스키마 변경
- [ ] 인증/인가 (로그인, 토큰)
- [ ] 동시성/트랜잭션 깊이 파기

## 📚 같은 폴더 다른 문서
- `서버개발_입문가이드.md` — 서버 개발 전체 큰 그림 (개념편)
