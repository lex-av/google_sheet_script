from pydantic import BaseSettings


class Settings(BaseSettings):
    api_key: str = "unsecure_default"
    cb_request_url: str = "http://www.cbr.ru/scripts/XML_daily.asp"
    creds_filename: str = "creds_google.json"
    spreadsheet_id: str

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
