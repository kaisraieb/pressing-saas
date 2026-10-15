import os

from dotenv import load_dotenv


load_dotenv()


def database_url():
    url = os.getenv("DATABASE_URL", "sqlite:///pressing.db")

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)

    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


class Config:
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    AUTH_JWKS_URL = os.getenv(
        "AUTH_JWKS_URL",
        "https://auth.majd-sassi-dev.workers.dev/api/auth/jwks",
    )
    AUTH_JWT_ISSUER = os.getenv("AUTH_JWT_ISSUER")
    AUTH_JWT_AUDIENCE = os.getenv("AUTH_JWT_AUDIENCE")
    AUTH_MOCK_TENANT_ID = os.getenv("AUTH_MOCK_TENANT_ID")