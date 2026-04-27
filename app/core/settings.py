from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_",)
    ASYNC_DSN: str = "postgresql+asyncpg://postgres:password@db:5432/postgres"
    ECHO: bool = False
    POOL_SIZE: int = 5
    POOL_OVERFLOW: int = 10

class AgentSettings(BaseSettings):
    MODEL: str = "openai:gpt-4o-mini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    SERVICE_NAME: str = "FastAPI Template"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8000
    NUMBER_OF_WORKERS: int = 1
    DEBUG: bool = False
    TESTING: bool = False
    RELOAD: bool = True

    db: DBSettings = DBSettings()
    agent: AgentSettings = AgentSettings() 
