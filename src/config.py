from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    This class defines the settings for the app
    """
    POSTGRES_URL: str
    API_PATH_PREFIX: str
    API_VERSION: str
    API_TITLE: str
    API_DESCRIPTION: str
    SECRET_KEY: str
    ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    API_BASE_URL: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
