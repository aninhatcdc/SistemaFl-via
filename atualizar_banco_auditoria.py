import sqlite3

from config import Config


def obter_caminho_banco():
    uri = Config.SQLALCHEMY_DATABASE_URI

    prefixo = "sqlite:///"

    if not uri.startswith(prefixo):
        raise ValueError(
            "Este script foi preparado apenas para banco SQLite."
        )

    return uri.replace(
        prefixo,
        "",
        1
    )


def obter_colunas(cursor, tabela):
    cursor.execute(
        f"PRAGMA table_info({tabela})"
    )

    return {
        linha[1]
        for linha in cursor.fetchall()
    }


def adicionar_coluna(
    cursor,
    tabela,
    nome_coluna,
    definicao
):
    colunas = obter_colunas(
        cursor,
        tabela
    )

    if nome_coluna in colunas:
        print(
            f"Coluna '{nome_coluna}' já existe "
            f"na tabela '{tabela}'."
        )

        return

    cursor.execute(
        f"""
        ALTER TABLE {tabela}
        ADD COLUMN {nome_coluna} {definicao}
        """
    )

    print(
        f"Coluna '{nome_coluna}' adicionada "
        f"à tabela '{tabela}'."
    )


def atualizar_clientes():
    caminho_banco = obter_caminho_banco()

    conexao = sqlite3.connect(
        caminho_banco
    )

    cursor = conexao.cursor()

    try:
        adicionar_coluna(
            cursor,
            "clientes",
            "atualizado_em",
            "DATETIME"
        )

        adicionar_coluna(
            cursor,
            "clientes",
            "criado_por_id",
            "INTEGER REFERENCES usuarios(id)"
        )

        adicionar_coluna(
            cursor,
            "clientes",
            "atualizado_por_id",
            "INTEGER REFERENCES usuarios(id)"
        )

        cursor.execute(
            """
            UPDATE clientes
            SET atualizado_em = criado_em
            WHERE atualizado_em IS NULL
            """
        )

        conexao.commit()

        print(
            "Auditoria da tabela clientes "
            "atualizada com sucesso."
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    atualizar_clientes()