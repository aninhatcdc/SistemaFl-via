import logging
import os
import sqlite3
import sys
import time

from datetime import datetime, timedelta
from pathlib import Path


# =====================================
# CONFIGURAÇÕES
# =====================================

# Quantos dias os backups serão mantidos.
DIAS_RETENCAO = 30

# Deixe vazio para salvar dentro da pasta do projeto.
#
# Na instalação da empresa, poderá ser alterado para algo como:
#
# r"C:\Users\UsuarioEmpresa\OneDrive\Backups Sistema Jurídico"
#
# ou:
#
# r"\\Servidor\Backups\SistemaJuridico"
DESTINO_BACKUP_EXTERNO = ""


# =====================================
# CAMINHOS DO PROJETO
# =====================================

BASE_DIR = Path(
    __file__
).resolve().parent

CAMINHO_BANCO = (
    BASE_DIR
    / "instance"
    / "sistema.db"
)

if DESTINO_BACKUP_EXTERNO.strip():
    PASTA_BACKUPS = Path(
        DESTINO_BACKUP_EXTERNO
    ).expanduser().resolve()
else:
    PASTA_BACKUPS = (
        BASE_DIR
        / "backups_automaticos"
    )

PASTA_LOGS = (
    BASE_DIR
    / "logs"
)

ARQUIVO_LOG = (
    PASTA_LOGS
    / "backup.log"
)


# =====================================
# LOG
# =====================================

def configurar_log():
    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        datefmt="%d/%m/%Y %H:%M:%S",
        handlers=[
            logging.FileHandler(
                ARQUIVO_LOG,
                encoding="utf-8"
            ),
            logging.StreamHandler(
                sys.stdout
            )
        ]
    )


# =====================================
# FUNÇÕES AUXILIARES
# =====================================

def formatar_tamanho(tamanho_bytes):
    if tamanho_bytes >= 1024 * 1024:
        return (
            f"{tamanho_bytes / (1024 * 1024):.2f} MB"
        )

    return (
        f"{tamanho_bytes / 1024:.2f} KB"
    )


def validar_banco():
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(
            (
                "O banco de dados não foi encontrado em: "
                f"{CAMINHO_BANCO}"
            )
        )

    conexao = None

    try:
        conexao = sqlite3.connect(
            str(
                CAMINHO_BANCO
            )
        )

        resultado = conexao.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            not resultado
            or resultado[0].lower() != "ok"
        ):
            raise RuntimeError(
                "O banco de dados não passou na verificação de integridade."
            )

    finally:
        if conexao:
            conexao.close()


def criar_nome_backup():
    agora = datetime.now()

    return agora.strftime(
        "sistema_%Y-%m-%d_%H-%M-%S.db"
    )


def criar_backup():
    PASTA_BACKUPS.mkdir(
        parents=True,
        exist_ok=True
    )

    validar_banco()

    nome_backup = criar_nome_backup()

    caminho_backup = (
        PASTA_BACKUPS
        / nome_backup
    )

    conexao_origem = None
    conexao_destino = None

    try:
        conexao_origem = sqlite3.connect(
            str(
                CAMINHO_BANCO
            )
        )

        conexao_destino = sqlite3.connect(
            str(
                caminho_backup
            )
        )

        with conexao_destino:
            conexao_origem.backup(
                conexao_destino
            )

        resultado = conexao_destino.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if (
            not resultado
            or resultado[0].lower() != "ok"
        ):
            raise RuntimeError(
                "O backup criado não passou na verificação de integridade."
            )

        return caminho_backup

    except Exception:
        if caminho_backup.exists():
            try:
                caminho_backup.unlink()
            except OSError:
                pass

        raise

    finally:
        if conexao_destino:
            conexao_destino.close()

        if conexao_origem:
            conexao_origem.close()


def remover_backups_antigos():
    if not PASTA_BACKUPS.exists():
        return 0

    limite = (
        datetime.now()
        - timedelta(
            days=DIAS_RETENCAO
        )
    )

    quantidade_removida = 0

    for arquivo in PASTA_BACKUPS.glob(
        "sistema_*.db"
    ):
        try:
            data_modificacao = datetime.fromtimestamp(
                arquivo.stat().st_mtime
            )

            if data_modificacao < limite:
                arquivo.unlink()

                quantidade_removida += 1

                logging.info(
                    "Backup antigo removido: %s",
                    arquivo.name
                )

        except OSError as erro:
            logging.warning(
                (
                    "Não foi possível remover "
                    "o backup antigo '%s': %s"
                ),
                arquivo.name,
                erro
            )

    return quantidade_removida


# =====================================
# EXECUÇÃO
# =====================================

def executar_backup():
    configurar_log()

    inicio = time.perf_counter()

    logging.info(
        "Iniciando backup automático."
    )

    logging.info(
        "Banco de origem: %s",
        CAMINHO_BANCO
    )

    logging.info(
        "Pasta de destino: %s",
        PASTA_BACKUPS
    )

    try:
        caminho_backup = criar_backup()

        tamanho = caminho_backup.stat().st_size

        removidos = remover_backups_antigos()

        tempo_decorrido = (
            time.perf_counter()
            - inicio
        )

        logging.info(
            "Backup realizado com sucesso."
        )

        logging.info(
            "Arquivo criado: %s",
            caminho_backup.name
        )

        logging.info(
            "Tamanho: %s",
            formatar_tamanho(
                tamanho
            )
        )

        logging.info(
            "Backups antigos removidos: %s",
            removidos
        )

        logging.info(
            "Tempo de execução: %.2f segundos",
            tempo_decorrido
        )

        return 0

    except Exception as erro:
        logging.exception(
            "Falha ao realizar o backup: %s",
            erro
        )

        return 1


if __name__ == "__main__":
    codigo_saida = executar_backup()

    raise SystemExit(
        codigo_saida
    )