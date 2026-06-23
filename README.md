# study-server

서버 개발 학습용 프로젝트 — **FastAPI + SQLModel + PostgreSQL + Alembic**.

간단한 item CRUD API. 앱 개발에서 서버 개발로 넘어오며 단계별로 구축.

## 스택
- **FastAPI** — 웹 프레임워크
- **SQLModel** — ORM (Pydantic + SQLAlchemy)
- **PostgreSQL** — DB (Docker 컨테이너로 실행)
- **Alembic** — DB 마이그레이션

## 처음부터 세우기 (재구축)

전제: Python 3.9+, Docker 설치돼 있어야 함.

```bash
# 1. 가상환경 + 패키지 복원
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. DB 띄우기 (PostgreSQL 컨테이너)
docker compose up -d

# 3. 설정 파일 준비
cp .env.example .env          # 필요하면 값 수정

# 4. DB 스키마 적용 (마이그레이션)
alembic upgrade head

# 5. 서버 실행
uvicorn app.main:app --reload
```

→ http://127.0.0.1:8000/docs 에서 API 문서 확인

## 자주 쓰는 명령

```bash
# DB 컨테이너 제어
docker compose up -d          # 띄우기
docker compose down           # 내리기 (볼륨은 유지 → 데이터 보존)
docker compose down -v        # 내리기 + 볼륨 삭제 (데이터까지 완전 삭제)

# DB 직접 접속 (psql)
docker exec -it study-postgres psql -U postgres -d studydb

# 마이그레이션 (모델 바꾼 뒤)
alembic revision --autogenerate -m "변경 내용"   # 마이그레이션 생성
alembic upgrade head                            # DB에 적용
alembic current                                 # 현재 적용된 버전 확인
```

## 구조

```
app/main.py            # FastAPI 앱 + 모델 + 핸들러
migrations/            # Alembic 마이그레이션 (스키마 변경 이력)
docker-compose.yml     # PostgreSQL 컨테이너 정의
requirements.txt       # 패키지 목록
.env.example           # 설정 양식 (.env 로 복사해서 사용)
```
