from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")
    rss_url: AnyUrl = Field(..., alias="RSS_URL")
    poll_interval_seconds: int = Field(300, alias="POLL_INTERVAL_SECONDS")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    detail_fetch_timeout_seconds: int = Field(15, alias="DETAIL_FETCH_TIMEOUT_SECONDS")
    detail_fetch_max_bytes: int = Field(2_000_000, alias="DETAIL_FETCH_MAX_BYTES")
    detail_body_max_chars: int = Field(200_000, alias="DETAIL_BODY_MAX_CHARS")
    detail_save_raw_html: bool = Field(False, alias="DETAIL_SAVE_RAW_HTML")
    detail_update_existing: bool = Field(False, alias="DETAIL_UPDATE_EXISTING")
    request_delay_ms: int = Field(200, alias="REQUEST_DELAY_MS")
    detail_fetch_user_agent: str = Field(
        "DisclosureInfoBot/0.1 (+https://github.com/bluecase1/DisclosureInfo)",
        alias="DETAIL_FETCH_USER_AGENT",
    )
    detail_fetch_accept_language: str = Field("ko-KR,ko;q=0.9,en;q=0.8", alias="DETAIL_FETCH_ACCEPT_LANGUAGE")
    detail_fetch_retry_attempts: int = Field(3, alias="DETAIL_FETCH_RETRY_ATTEMPTS")
    detail_fetch_retry_min_seconds: float = Field(0.5, alias="DETAIL_FETCH_RETRY_MIN_SECONDS")
    detail_fetch_retry_max_seconds: float = Field(5.0, alias="DETAIL_FETCH_RETRY_MAX_SECONDS")
    detail_batch_size: int = Field(50, alias="DETAIL_BATCH_SIZE")
