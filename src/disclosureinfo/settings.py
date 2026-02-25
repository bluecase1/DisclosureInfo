from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")
    rss_url: AnyUrl = Field(..., alias="RSS_URL")
    poll_interval_seconds: int = Field(300, alias="POLL_INTERVAL_SECONDS")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
