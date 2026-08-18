import sqlite3

from config import Config


def obter_caminho_banco():
    uri = Config.SQLALCHEMY_DATABASE_URI
    prefixo = "sqlite:///"

    if not uri.startswith(prefixo):
        raise ValueError(
            "Este script foi preparado apenas para SQLite."
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
            f"Coluna '{nome_coluna}' já existe."
        )

        return

    cursor.execute(
        f"""
        ALTER TABLE {tabela}
        ADD COLUMN {nome_coluna} {definicao}
        """
    )

    print(
        f"Coluna '{nome_coluna}' adicionada."
    )


def atualizar_preferencias():
    caminho_banco = obter_caminho_banco()

    conexao = sqlite3.connect(
        caminho_banco
    )

    cursor = conexao.cursor()

    try:
        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "itens_por_pagina",
            "INTEGER NOT NULL DEFAULT 10"
        )

        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "dias_notificacoes",
            "INTEGER NOT NULL DEFAULT 7"
        )

        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "exibir_notificacoes_baixa",
            "BOOLEAN NOT NULL DEFAULT 1"
        )

        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "modo_compacto_tabelas",
            "BOOLEAN NOT NULL DEFAULT 0"
        )

        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "pagina_inicial",
            "VARCHAR(50) NOT NULL DEFAULT 'dashboard'"
        )

        adicionar_coluna(
            cursor,
            "configuracoes_escritorio",
            "formato_data",
            "VARCHAR(20) NOT NULL DEFAULT 'DD/MM/AAAA'"
        )

        conexao.commit()

        print(
            "Preferências adicionadas com sucesso."
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    atualizar_preferencias()