# COMMANDS — 자주 쓰는 명령어 모음

> 까먹으면 여기서 찾으면 됨. (전제: `~/study/server` 에서, `.venv` 활성화 상태)

## 🚀 서버 실행 (로컬 개발 — venv, 코드 즉시 반영)
```bash
source .venv/bin/activate            # 가상환경 켜기 (프롬프트에 (.venv) 뜸)
uvicorn app.main:app --reload        # 서버 실행 (app.main = app/main.py, 점 표기!)
# → http://127.0.0.1:8000/docs
# ※ 컨테이너로 띄우려면 ↓ "컨테이너 (Docker Compose)" 섹션
```

## 🐳 컨테이너 (Docker Compose) — 앱 + DB
```bash
docker compose up -d --build         # 앱 빌드 + 앱·DB 둘 다 띄우기 (코드 바꿨을 때)
docker compose up -d                 # 빌드 없이 띄우기
docker compose down                  # 끄기 (볼륨=데이터 유지)
docker compose down -v               # 끄기 + 데이터 완전 삭제
docker compose ps                    # 컨테이너 상태 (db, app 둘 다 Up 확인)
docker compose logs -f app           # 앱 로그 실시간 (-f=follow; curl 날리면 요청 찍힘)
docker compose logs db               # DB 로그
docker compose top app               # 앱 컨테이너 안 프로세스 (uvicorn)
docker compose exec app sh           # 앱 컨테이너 안 셸 진입
docker compose exec app alembic upgrade head   # 컨테이너 안에서 마이그레이션
docker ps -a                         # (전체) 멈춘 것까지 모든 컨테이너
```

## 🔍 어디서 도는지 확인 (로컬 vs 컨테이너)
```bash
lsof -i :8000                        # 8000 주인: docker-proxy=컨테이너 / python=로컬
ps aux | grep "[u]vicorn"            # 로컬 uvicorn 직접 떠있나 (없어야=컨테이너만)
```

## 🗄️ DB 내부 (psql)

접속해서 작업:
```bash
docker exec -it study-postgres psql -U postgres -d studydb
```
접속 후 메타명령 (`\` 로 시작):
```
\l            데이터베이스 목록
\dt           테이블 목록
\d item       테이블 구조 (컬럼·타입·제약)
\d+ item      위 + 인덱스·상세
\di           인덱스 목록
\du           유저(role) 목록
\q            나가기
```

한 줄로 (접속 안 하고 `-c` 뒤에 명령):
```bash
# 테이블 목록
docker exec -it study-postgres psql -U postgres -d studydb -c "\dt"

# 데이터 조회
docker exec -it study-postgres psql -U postgres -d studydb -c "SELECT * FROM item;"
docker exec -it study-postgres psql -U postgres -d studydb -c 'SELECT * FROM "user";'   # user=예약어→따옴표

# 테이블 구조 / 개수
docker exec -it study-postgres psql -U postgres -d studydb -c "\d item"
docker exec -it study-postgres psql -U postgres -d studydb -c "SELECT count(*) FROM item;"
```

## 🔀 마이그레이션 (Alembic)
```bash
alembic current                              # 지금 DB가 어느 버전까지 적용됐나
alembic history                              # 마이그레이션 이력 (사슬 순서)
alembic heads                                # 최신 리비전
alembic revision --autogenerate -m "메시지"  # 모델 바꾼 뒤 → 마이그레이션 생성
alembic upgrade head                         # DB에 적용 (최신까지)
alembic downgrade -1                         # 한 단계 되돌리기
```
마이그레이션 파일 보기:
```bash
ls migrations/versions/                       # 목록
cat $(ls -t migrations/versions/*.py | head -1)   # 최신 파일 내용
```

## 🌐 API 호출 (curl) — 인증 & 조회
```bash
# 로그인 → 토큰 (python3로 access_token 추출)
TOKEN=$(curl -s -X POST localhost:8000/login -H "Content-Type: application/json" \
  -d '{"username":"chris","password":"..."}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 보호된 API — 토큰 첨부 (Bearer 접두어 필수)
curl localhost:8000/users/me -H "Authorization: Bearer $TOKEN"
curl -X POST localhost:8000/items -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"name":"coffee","price":4500}'

# 조회 (검색·필터·페이지네이션)
curl "localhost:8000/items?q=coffee"                 # 이름 검색(부분일치)
curl "localhost:8000/items?in_stock=false"           # 재고 필터
curl "localhost:8000/items?min_price=3000&limit=5"   # 가격 필터 + 개수 제한
curl "localhost:8000/items?skip=5&limit=5"           # 페이지네이션(다음 5개)
curl -G localhost:8000/items --data-urlencode "q=커피"   # 한글은 인코딩 필요
```

## 🧪 테스트 (pytest)
```bash
pip install pytest httpx      # 최초 1회
pytest -v                     # tests/ 의 test_*.py 자동 실행 (-v=자세히)
pytest tests/test_users.py    # 특정 파일만
pytest -k "create_user"       # 이름에 create_user 든 테스트만
```

## 📦 환경 / 패키지
```bash
python3 -m venv .venv                 # 가상환경 생성
source .venv/bin/activate             # 켜기
deactivate                            # 끄기
pip install <패키지>                   # 설치
pip install -r requirements.txt       # 목록대로 복원
pip freeze > requirements.txt         # 현재 설치된 거 기록 (패키지 추가했으면 갱신!)
```

## 🌳 Git
```bash
git status                            # 변경 상태
git add . && git commit -m "메시지"    # 커밋
git push                              # 원격 반영
git pull                              # 원격 변경 받기
```

## ♻️ 처음부터 재구축
→ `README.md` 의 "처음부터 세우기" 6줄 참고
