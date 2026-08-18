import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def obter_database_url():
    """Retorna a URL do banco. Em produção, use DATABASE_URL do Render."""
    url = os.environ.get("DATABASE_URL", "").strip()

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    if url:
        return url

    return "sqlite:///" + os.path.join(
        BASE_DIR,
        "instance",
        "sistema.db"
    )


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "troque_essa_chave_depois"
    )

    SQLALCHEMY_DATABASE_URI = obter_database_url()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Evita problemas de conexões ociosas no PostgreSQL.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
