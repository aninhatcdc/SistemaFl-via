from pathlib import Path
import shutil
import sqlite3
import sys
from datetime import datetime

from sqlalchemy import inspect

from app import app
from models import db
from models.ficha_trabalhista import FichaTrabalhista


TABELA = "fichas_trabalhistas"


# =========================================
# CONFIGURAÇÕES DOS CAMPOS
# =========================================
VALORES_PADRAO = {
    "etapa_atual": "1",
    "etapa_atendimento_concluida": "0",
    "etapa_cliente_concluida": "0",
    "etapa_empresa_concluida": "0",
    "etapa_admissao_concluida": "0",
    "etapa_contrato_concluida": "0",
    "etapa_local_concluida": "0",
    "etapa_salario_concluida": "0",
    "etapa_ferias_concluida": "0",
    "etapa_decimo_terceiro_concluida": "0",
    "etapa_rescisao_concluida": "0",
    "avaliacao_google_solicitada": "0"
}


def localizar_banco_sqlite():
    """
    Localiza o arquivo SQLite configurado no Flask.
    """

    uri = app.config.get(
        "SQLALCHEMY_DATABASE_URI",
        ""
    )

    if not uri.startswith("sqlite:///"):
        return None

    caminho_configurado = uri.replace(
        "sqlite:///",
        "",
        1
    )

    caminho = Path(
        caminho_configurado
    )

    if not caminho.is_absolute():
        caminho = Path(
            app.root_path
        ) / caminho

    return caminho.resolve()


def criar_backup():
    """
    Cria uma cópia de segurança antes da migração.
    """

    caminho_banco = localizar_banco_sqlite()

    if caminho_banco is None:
        print(
            "ℹ️ O banco configurado não é SQLite."
        )
        print(
            "A migração continuará sem criar "
            "backup manual do arquivo."
        )

        return None

    if not caminho_banco.exists():
        print(
            "ℹ️ O arquivo do banco ainda não existe:"
        )
        print(
            caminho_banco
        )

        return None

    pasta_backup = (
        caminho_banco.parent
        / "backups"
    )

    pasta_backup.mkdir(
        parents=True,
        exist_ok=True
    )

    momento = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    caminho_backup = (
        pasta_backup
        / (
            f"{caminho_banco.stem}"
            f"_antes_ficha_trabalhista_"
            f"{momento}"
            f"{caminho_banco.suffix}"
        )
    )

    shutil.copy2(
        caminho_banco,
        caminho_backup
    )

    print(
        "✅ Backup criado:"
    )
    print(
        caminho_backup
    )

    return caminho_backup


def tabela_existe():
    """
    Verifica se a tabela já existe no banco.
    """

    inspetor = inspect(
        db.engine
    )

    return inspetor.has_table(
        TABELA
    )


def nomes_colunas_existentes():
    """
    Retorna os nomes das colunas que já existem.
    """

    inspetor = inspect(
        db.engine
    )

    colunas = inspetor.get_columns(
        TABELA
    )

    return {
        coluna["name"]
        for coluna in colunas
    }


def compilar_tipo_coluna(coluna):
    """
    Converte o tipo SQLAlchemy para o tipo usado
    pelo banco atual.
    """

    return coluna.type.compile(
        dialect=db.engine.dialect
    )


def montar_definicao_coluna(coluna):
    """
    Monta a definição SQL usada no ALTER TABLE.
    """

    partes = [
        f'"{coluna.name}"',
        compilar_tipo_coluna(
            coluna
        )
    ]

    valor_padrao = VALORES_PADRAO.get(
        coluna.name
    )

    if valor_padrao is not None:
        partes.append(
            f"DEFAULT {valor_padrao}"
        )

    if not coluna.nullable:
        if valor_padrao is None:
            raise RuntimeError(
                "A coluna obrigatória "
                f"'{coluna.name}' não possui "
                "valor padrão configurado."
            )

        partes.append(
            "NOT NULL"
        )

    return " ".join(
        partes
    )


def adicionar_coluna(conexao, coluna):
    """
    Adiciona uma coluna ausente na tabela.
    """

    definicao = montar_definicao_coluna(
        coluna
    )

    comando = (
        f'ALTER TABLE "{TABELA}" '
        f"ADD COLUMN {definicao}"
    )

    conexao.exec_driver_sql(
        comando
    )


def garantir_valores_padrao(conexao):
    """
    Corrige possíveis valores nulos nos campos
    de controle criados pela migração.
    """

    for nome_coluna, valor in VALORES_PADRAO.items():
        comando = (
            f'UPDATE "{TABELA}" '
            f'SET "{nome_coluna}" = {valor} '
            f'WHERE "{nome_coluna}" IS NULL'
        )

        conexao.exec_driver_sql(
            comando
        )


def executar_migracao():
    """
    Adiciona somente as colunas que ainda não
    existem no banco.
    """

    with app.app_context():

        print(
            "\n========================================="
        )
        print(
            " MIGRAÇÃO DA FICHA TRABALHISTA"
        )
        print(
            "=========================================\n"
        )

        criar_backup()

        if not tabela_existe():
            print(
                "ℹ️ A tabela ainda não existe."
            )
            print(
                "Criando as tabelas pelo SQLAlchemy..."
            )

            db.create_all()

            print(
                "✅ Tabelas criadas com sucesso."
            )

            return

        existentes = nomes_colunas_existentes()

        colunas_modelo = list(
            FichaTrabalhista.__table__.columns
        )

        colunas_faltantes = [
            coluna
            for coluna in colunas_modelo
            if coluna.name not in existentes
        ]

        if not colunas_faltantes:
            print(
                "✅ O banco já está atualizado."
            )

            return

        print(
            f"Colunas encontradas no modelo: "
            f"{len(colunas_modelo)}"
        )

        print(
            f"Colunas que serão adicionadas: "
            f"{len(colunas_faltantes)}\n"
        )

        adicionadas = 0

        try:
            with db.engine.begin() as conexao:

                for coluna in colunas_faltantes:
                    print(
                        f"➕ Adicionando: {coluna.name}"
                    )

                    adicionar_coluna(
                        conexao,
                        coluna
                    )

                    adicionadas += 1

                garantir_valores_padrao(
                    conexao
                )

        except Exception as erro:
            print(
                "\n❌ A migração não foi concluída."
            )

            print(
                f"Erro: {erro}"
            )

            print(
                "\nNenhum arquivo deve ser apagado."
            )

            print(
                "Use o backup criado antes da migração "
                "caso seja necessário."
            )

            raise

        print(
            "\n========================================="
        )

        print(
            f"✅ Migração concluída."
        )

        print(
            f"✅ {adicionadas} colunas adicionadas."
        )

        print(
            "✅ Dados antigos preservados."
        )

        print(
            "=========================================\n"
        )


if __name__ == "__main__":
    try:
        executar_migracao()

    except ImportError as erro:
        print(
            "\n❌ Não foi possível importar o sistema."
        )

        print(
            "Confirme que este arquivo está na mesma "
            "pasta do app.py."
        )

        print(
            f"\nDetalhes: {erro}"
        )

        sys.exit(
            1
        )

    except sqlite3.Error as erro:
        print(
            "\n❌ O SQLite retornou um erro:"
        )

        print(
            erro
        )

        sys.exit(
            1
        )

    except Exception as erro:
        print(
            "\n❌ Ocorreu um erro durante a migração:"
        )

        print(
            erro
        )

        sys.exit(
            1
        )