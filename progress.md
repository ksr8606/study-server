# 서버 공부 진도 노트

> 오랜만에 와서 까먹었으면 **이 파일부터** 읽으면 돼.
> (이젠 까먹어도 돼 — 아래 명령만 따라치면 어디서든 재현됨)

## 📍 작업 위치 / 원격
- 로컬: `~/study/server/`
- GitHub: https://github.com/ksr8606/study-server

## 🆕 완전히 처음부터 (다른 컴퓨터/날렸을 때) — 6줄로 재구축
```bash
git clone https://github.com/ksr8606/study-server.git server && cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
cp .env.example .env       # ※ SECRET_KEY 채우기: openssl rand -hex 32
alembic upgrade head
uvicorn app.main:app --reload
```
※ `docker compose up` 직후 DB 초기화에 몇 초 — `alembic`에서 connection refused 나면 잠깐 뒤 재시도.

## ▶️ 그냥 다시 시작 (이미 셋업된 상태)
```bash
cd ~/study/server
docker compose up -d                 # DB 컨테이너 켜기
source .venv/bin/activate
uvicorn app.main:app --reload
```
확인: http://127.0.0.1:8000/docs

## 🧱 스택
**FastAPI + SQLModel + PostgreSQL(Docker) + Alembic + JWT 인증**

## 🗂️ 파일 구조
```
app/
  main.py          # 앱 생성 + 라우터 등록 (얇게)
  config.py        # Settings (.env)
  database.py      # engine + get_session
  models.py        # SQLModel 모델 (Item*, User*, Token 등)
  security.py      # 비번 해싱 / JWT 발급·검증
  dependencies.py  # get_current_user (인증 가드)
  routers/         # items.py / users.py / auth.py (도메인별)
```

## ✅ 배운 것
- CRUD ↔ HTTP 메서드 ↔ SQL, 상태코드(422·404·405·409·401·403)
- SQLModel: 모델=테이블 / engine(앱당1) / session(요청당1) / Depends 주입
- 모델 분리(입력·테이블·응답), response_model, extra="forbid"
- unique 제약 + IntegrityError→409, rollback 후 ORM 객체 만료 주의(patch.name 사용)
- DB 전환 SQLite→PostgreSQL = 커넥션 문자열만 (ORM 추상화)
- Docker로 DB 운용: 포트매핑·볼륨(영속)·환경변수, docker-compose
- 설정 분리: pydantic-settings + .env (+ .env.example 양식 공유)
- **Alembic 마이그레이션**: 모델 변경 → `revision --autogenerate` → `upgrade head`
- **재현 자산**: requirements.txt / docker-compose.yml / .env.example / README → "기억 대신 파일"
- **Git/GitHub**: .gitignore로 비밀(.env)·.venv 제외, HTTPS 인증은 토큰(PAT)/gh
- **파일 구조 분리**: APIRouter로 도메인별 라우터 + config/database/models/security/dependencies
- **인증(누구냐)**: 비번 bcrypt 해시(평문X) → 로그인 → JWT 토큰 발급/검증 → `get_current_user`
- **인가(권한있냐)**: item에 owner(`user_id`) → 수정·삭제 시 소유권 확인(남의 것 403). 인증≠인가!

## 🛠️ 자주 쓰는 명령
```bash
# DB 컨테이너
docker compose up -d          # 켜기
docker compose down           # 끄기 (볼륨 유지=데이터 보존)
docker compose down -v        # 끄기 + 데이터 완전 삭제

# DB 접속
docker exec -it study-postgres psql -U postgres -d studydb
#   item:  SELECT * FROM item;
#   user:  SELECT * FROM "user";   (user는 예약어→큰따옴표)

# 마이그레이션 (모델 바꾼 뒤)
alembic revision --autogenerate -m "변경 내용"
alembic upgrade head
alembic current               # 현재 버전 확인

# 인증 테스트
curl -X POST localhost:8000/login -H "Content-Type: application/json" -d '{"username":"chris","password":"..."}'   # → access_token
curl localhost:8000/users/me -H "Authorization: Bearer <토큰>"   # 보호된 API (Bearer 접두어 필수)

# 변경 원격 반영
git add . && git commit -m "메시지" && git push
```

## ⏭️ 다음 후보
- [ ] **배포** — localhost → 클라우드, 인터넷에서 접속. HTTPS·운영DB·환경변수 주입  ← **지금 여기**
- [ ] 조회 다듬기 (검색·필터·페이지네이션)
- [ ] 동시성/트랜잭션 깊이 파기
- [ ] (선택) 앱까지 Docker 이미지로 → docker compose 하나로 앱+DB

## 📚 같은 폴더 다른 문서
- `guide.md` — 서버 개발 전체 큰 그림 (개념편)
- `README.md` — 프로젝트 셋업/명령 (위 재구축 6줄의 원본)
- `COMMANDS.md` — 자주 쓰는 명령어 치트시트
