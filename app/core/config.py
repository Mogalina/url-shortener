from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CASSANDRA_HOSTS: str
    REDIS_HOST: str
    REDIS_PORT: int
    BASE_URL: str
    KEYSPACE: str
    CACHE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
