from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str                                    # 타입 명시 = 자동 검증
    secret_key: str                                      # JWT 서명용 비밀키 (노출 금지)
    jwt_algorithm: str = "HS256"                         # 서명 알고리즘
    access_token_expire_minutes: int = 30               # 토큰 만료 시간(분)
    model_config = SettingsConfigDict(env_file=".env")   # .env 에서 읽어라


settings = Settings()
