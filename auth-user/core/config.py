import os

from dotenv import load_dotenv
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class RunConfig(BaseModel):
    """Настройки для запуска."""

    host: str = "127.0.0.1"
    port: int = 8000


class JWTConfig(BaseModel):
    """Настройки JWT-токена."""

    secret_key: str | None = os.getenv("AUTH_USER__JWT__SECRET_KEY")
    algorithm: str | None = os.getenv("AUTH_USER__JWT__ALGORITHM")
    access_token: str | None = os.getenv("AUTH_USER__JWT__ACCESS_TOKEN")


class RedisConfig(BaseModel):
    """Настройки redis"""

    url: str | None = os.getenv("AUTH_USER__REDIS__URL")


class ApiPrefix(BaseModel):
    """Настройки для префиксов."""

    prefix: str = "/api"
    users: str = "/users"


class DataBaseConfig(BaseModel):
    """Настройки базы данных."""

    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    """Общая конфигурация настроек."""

    model_config = SettingsConfigDict(
        env_file=(".env-sample", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="AUTH_USER__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DataBaseConfig
    jwt: JWTConfig = JWTConfig()
    redis: RedisConfig = RedisConfig()


settings = Settings()
