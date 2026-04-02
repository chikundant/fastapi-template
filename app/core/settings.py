from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")
    ASYNC_DSN: str = "AsyncDSN"
    ECHO: bool = False
    POOL_SIZE: int = 5
    POOL_OVERFLOW: int = 10
    POOL_RECYCLE: int = 1800


class Settings(BaseSettings):
    SERVICE_NAME: str = "FastAPI Template"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001
    NUMBER_OF_WORKERS: int = 1
    DEBUG: bool = False
    TESTING: bool = False
    RELOAD: bool = True
    SENTRY_DSN: str = "SentryDSN"

    db: DBSettings = DBSettings()
