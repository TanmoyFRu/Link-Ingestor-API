from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "Link Ingestor"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database
    database_url: str = Field(env="DATABASE_URL", default="postgresql+asyncpg://user:pass@localhost/link_ingestor")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL", default="redis://localhost:6379")
    
    # Celery
    celery_broker_url: str = Field(env="CELERY_BROKER_URL", default="redis://localhost:6379/0")
    celery_result_backend: str = Field(env="CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
    
    # HTTP Client
    http_timeout: int = Field(default=30, env="HTTP_TIMEOUT")
    http_max_retries: int = Field(default=3, env="HTTP_MAX_RETRIES")
    user_agent: str = Field(default="LinkIngestor/1.0", env="USER_AGENT")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # Backlink Settings
    max_backlinks_per_link: int = Field(default=10, env="MAX_BACKLINKS_PER_LINK")
    
    # Search Providers
    bing_api_key: Optional[str] = Field(default=None, env="BING_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

