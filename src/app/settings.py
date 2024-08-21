from pydantic import AnyUrl, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: AnyUrl
    redis_url: RedisDsn
    telegram_session: str
    s3_url: str
    s3_access_key: str
    s3_secret_key: str
