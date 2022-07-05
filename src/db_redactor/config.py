from pydantic import BaseSettings


class Settings(BaseSettings):
    api_key: str = "unsecure_default"
    cb_request_url: str = "http://www.cbr.ru/scripts/XML_daily.asp"

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
