from sqlmodel import Session, create_engine

from app.config import settings


engine = create_engine(settings.database_url)


# 세션 의존성 = 요청마다 1개, 자동 정리
def get_session():
    # with 블록 끝나면 세션 자동 close
    with Session(engine) as session:
        # 핸들러한테 빌려주고, 끝나면 회수
        yield session
