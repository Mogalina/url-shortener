from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CASSANDRA_HOSTS: str
    REDIS_HOST: str
    REDIS_PORT: int
    BASE_URL: str
    KEYSPACE: str

    class Config:
        env_file = ".env"

settings = Settings()
