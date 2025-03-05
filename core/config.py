from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    GOOGLE_API_KEY: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_AUTH_TOKEN: str
    OPENAI_API_KEY: str
    ZADARMA_API_KEY: str
    ZADARMA_API_SECRET: str
    GROQ_API_KEY: str
    SIP_DOMAIN: str
    SIP_USERNAME: str
    SIP_PASSWORD: str
    MAILGUN_API_KEY: str
    ELEVEN_LABS_API_KEY: str
    COMPOSE_PROJECT_NAME: str
    TEMPORAL_VERSION: str
    TEMPORAL_ADMINTOOLS_VERSION: str
    TEMPORAL_UI_VERSION: str
    POSTGRESQL_VERSION: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DEFAULT_PORT: int
    MYSQL_VERSION: int
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USE_SSL: bool
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    CALLS_HOST: str
    class Config:
        env_file = ".env"

settings = Settings()