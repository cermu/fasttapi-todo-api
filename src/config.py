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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()