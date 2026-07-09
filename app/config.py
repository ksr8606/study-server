from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 타입 명시 = 자동 검증
    database_url: str
    # JWT 서명용 비밀키 (노출 금지)
    secret_key: str
    # 서명 알고리즘
    jwt_algorithm: str = "HS256"
    # 토큰 만료 시간(분)
    access_token_expire_minutes: int = 30
    # .env 에서 읽어라
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
