from pydantic import BaseSettings


class Settings(BaseSettings):
    api_key: str = "unsecure_default"

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
