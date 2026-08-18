
"""
Migra o banco SQLite atual para PostgreSQL.
Uso:
    set SQLITE_DATABASE_PATH=instance\sistema.db
    set DATABASE_URL=postgresql://USUARIO:SENHA@HOST:5432/BANCO
    python migrar_sqlite_postgres.py
O destino deve estar vazio.
"""
import os
import sys
from pathlib import Path
from importlib import import_module
from sqlalchemy import create_engine, select, func, text
from models import db

BASE_DIR = Path(__file__).resolve().parent
MODEL_MODULES = [
    "models.agenda", "models.atendimento", "models.cliente",
    "models.configuracao", "models.configuracao_arquivos",
    "models.configuracao_financeiro", "models.documento",
    "models.documento_gerado", "models.documento_modelo",
    "models.ficha_civel", "models.ficha_consumidor",
    "models.ficha_familia", "models.ficha_previdenciaria",
    "models.ficha_trabalhista", "models.financeiro",
    "models.processo", "models.usuario",
]

def normalizar_url(url):
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url

def main():
    sqlite_path = Path(os.environ.get(
        "SQLITE_DATABASE_PATH",
        str(BASE_DIR / "instance" / "sistema.db")
    )).expanduser().resolve()
    database_url = normalizar_url(os.environ.get("DATABASE_URL", "").strip())

    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite não encontrado: {sqlite_path}")
    if not database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise SystemExit("Defina DATABASE_URL com a conexão do PostgreSQL.")

    for modulo in MODEL_MODULES:
        import_module(modulo)

    metadata = db.metadata
    origem = create_engine(f"sqlite:///{sqlite_path}")
    destino = create_engine(database_url, pool_pre_ping=True)

    print("Criando tabelas no PostgreSQL...")
    metadata.create_all(destino)

    with origem.connect() as conn_origem, destino.begin() as conn_destino:
        print("Verificando se o PostgreSQL está vazio...")
        for tabela in metadata.sorted_tables:
            total = conn_destino.execute(
                select(func.count()).select_from(tabela)
            ).scalar_one()
            if total:
                raise SystemExit(
                    f"O destino já possui dados na tabela '{tabela.name}'. "
                    "Use um PostgreSQL vazio."
                )

        print("Copiando dados...")
        for tabela in metadata.sorted_tables:
            linhas = conn_origem.execute(select(tabela)).mappings().all()
            if not linhas:
                print(f"  - {tabela.name}: vazia")
                continue
            conn_destino.execute(tabela.insert(), [dict(linha) for linha in linhas])
            print(f"  - {tabela.name}: {len(linhas)} registros")

        for tabela in metadata.sorted_tables:
            if tabela.c.get("id") is None:
                continue
            nome = tabela.name.replace('"', '""')
            sql = (
                "SELECT setval("
                f"pg_get_serial_sequence('\"{nome}\"', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM \"{nome}\"), 1), true)"
            )
            try:
                conn_destino.execute(text(sql))
            except Exception:
                pass

    origem.dispose()
    destino.dispose()
    print("\nMigração concluída com sucesso.")

if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"\nERRO: {erro}")
        sys.exit(1)
