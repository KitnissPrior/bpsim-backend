from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:p0sTgreS@localhost/bpsim"


settings = Settings()