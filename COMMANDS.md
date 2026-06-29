# COMMANDS — 자주 쓰는 명령어 모음

> 까먹으면 여기서 찾으면 됨. (전제: `~/study/server` 에서, `.venv` 활성화 상태)

## 🚀 서버 실행
```bash
source .venv/bin/activate            # 가상환경 켜기 (프롬프트에 (.venv) 뜸)
uvicorn app.main:app --reload        # 서버 실행 (app.main = app/main.py, 점 표기!)
# → http://127.0.0.1:8000/docs
```

## 🐳 DB 컨테이너 (Docker)
```bash
docker compose up -d                 # DB 켜기
docker compose down                  # 끄기 (볼륨=데이터 유지)
docker compose down -v               # 끄기 + 데이터 완전 삭제
docker compose ps                    # 이 프로젝트 컨테이너 상태
docker ps                            # 실행 중 컨테이너 전부
docker ps -a                         # 멈춘 것까지
docker logs study-postgres           # DB 로그 (에러 확인)
docker start study-postgres          # (compose 안 쓰고) 그냥 켜기
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
