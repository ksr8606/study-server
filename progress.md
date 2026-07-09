# 서버 공부 진도 노트

> 오랜만에 와서 까먹었으면 **이 파일부터** 읽으면 돼.
> (이젠 까먹어도 돼 — 아래 명령만 따라치면 어디서든 재현됨)

## 📍 작업 위치 / 원격
- 로컬: `~/study/server/`
- GitHub: https://github.com/ksr8606/study-server
- 운영(Render): https://study-server-q81v.onrender.com  (+ Render DB: study_db)

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
**FastAPI + SQLModel + PostgreSQL(Docker) + Alembic + JWT 인증** / 배포: Render

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
Dockerfile           # 앱 이미지 (로컬 compose + Render Docker 배포용)
docker-compose.yml   # 로컬: 앱 + DB 한 방에
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
- **앱 컨테이너화**: Dockerfile + docker-compose 에 app 추가 → `docker compose up`으로 앱+DB 한 방에 (venv 졸업). 컨테이너끼리는 서비스명(`db`)으로 통신
- **배포(PaaS/Render)**: GitHub App 연동 → **main push 시 자동 재배포** / 관리형 PostgreSQL / 환경변수(DATABASE_URL·SECRET_KEY) 주입 / 무료 플랜은 Shell 없어 **Start Command에 `alembic upgrade head &&` 묶어** 마이그레이션
- **Render 빌드 방식**: native Python(requirements.txt + Start Command) vs Docker(Dockerfile) — 둘 중 택. (배포는 "컨테이너 전송"이 아니라 "설계도(코드+Dockerfile)로 클라우드가 빌드")
- **VPS 배포(로컬 VM/Multipass 실습)**: SSH접속(=multipass shell) → apt update → Docker 설치 → git clone → docker compose(앱+DB) → nginx 리버스 프록시(80→8000) → 프로세스 관리(restart: unless-stopped + 재부팅 자동복구). HTTPS는 공인 도메인 필요라 개념만(Render로 실전). ★ 맥과 VM은 별개 서버 — VM 안에 Docker 따로 설치, 실제 VPS와 동일한 명령
- **조회 다듬기**: 쿼리 파라미터로 검색(name LIKE)·필터(in_stock·가격대)·페이지네이션(skip/limit, `limit`은 상한 `le=100`). `select`에 조건부 `.where()` 쌓기. ★ `.contains()`(SQLAlchemy 메서드=SQL LIKE) ≠ `.__contains__()`(파이썬 매직, 쓰면 에러). URL의 한글은 인코딩 필요(curl은 `-G --data-urlencode`)
- **자동배포(CI/CD의 CD)**: git push → GitHub이 webhook으로 Render에 알림 → 자동 빌드·배포. webhook = "서버 간 푸시 알림"
- **DB 관계(Relationship)**: FK(`user_id`, DB 저장) vs Relationship(`owner`/`items`, ORM 편의=FK를 객체로 자동조회). `back_populates`로 양방향. Relationship은 DB 안 바꿔 → 마이그레이션 불필요. 라우트는 `/users/me/items`(정적/변수 경로 충돌 피함)
- **N+1 문제**: 목록(1) + 각 항목 관계 조회를 하나씩(N) = N+1 쿼리 (lazy 로드 = 접근할 때마다 따로). 앱의 "리스트 셀마다 API 호출"과 동일. 해결 `selectinload` = owner를 후행 2단계로 `IN` 한 번에. ★ ORM 자동 아님 → 개발자가 "응답에 관계 목록 들어가면 eager 로드" 판단해야 (실무 성능버그 주범)

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

# 배포: main 에 push 하면 Render 가 자동 재배포
git add . && git commit -m "메시지" && git push
# Render 운영 DB 접속: 대시보드 study_db 의 PSQL Command (External URL)
```

## ⏭️ 다음 후보
- [x] 배포 (PaaS/Render + VPS/Multipass) — 인터넷 공개 완료 ✓ (https://study-server-q81v.onrender.com)
- [x] 조회 다듬기 (검색·필터·페이지네이션) ✓ — Render 자동배포 반영
- [x] DB 관계(Relationship) + N+1 문제 ✓
- [ ] 동시성/트랜잭션 깊이 파기  ← **다음 후보**
- [ ] 에러처리·로깅 (운영 디버깅)
- [ ] 조회 완성 (정렬 `order_by` + 응답에 `total`)
- [ ] 비동기(async) — 중급
- [ ] **테스트** (pytest) — 맨 마지막에 (코드 확정 후)

## 📚 같은 폴더 다른 문서
- `guide.md` — 서버 개발 전체 큰 그림 (개념편)
- `README.md` — 프로젝트 셋업/명령 (위 재구축 6줄의 원본)
- `COMMANDS.md` — 자주 쓰는 명령어 치트시트
