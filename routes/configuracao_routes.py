import os
import sqlite3
import tempfile

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    after_this_request,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)

from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from models import db
from models.configuracao import ConfiguracaoEscritorio
from utils.permissoes import admin_required


configuracao_bp = Blueprint(
    "configuracoes",
    __name__,
    url_prefix="/configuracoes"
)


EXTENSOES_LOGO = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


# =====================================
# FUNÇÕES AUXILIARES — LOGO
# =====================================
def extensao_logo_permitida(nome_arquivo):
    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(
            ".",
            1
        )[1].lower() in EXTENSOES_LOGO
    )


def pasta_logos():
    pasta = os.path.join(
        current_app.static_folder,
        "uploads",
        "logos"
    )

    os.makedirs(
        pasta,
        exist_ok=True
    )

    return pasta


# =====================================
# FUNÇÕES AUXILIARES — CONFIGURAÇÃO
# =====================================
def obter_configuracao():
    configuracao = (
        ConfiguracaoEscritorio.query
        .order_by(
            ConfiguracaoEscritorio.id.asc()
        )
        .first()
    )

    if configuracao:
        return configuracao

    configuracao = ConfiguracaoEscritorio(
        nome_escritorio="Sistema Jurídico",
        cor_principal="#212529",
        cor_secundaria="#0d6efd"
    )

    db.session.add(
        configuracao
    )

    db.session.commit()

    return configuracao


# =====================================
# FUNÇÕES AUXILIARES — BACKUP
# =====================================
def obter_caminho_banco():
    """
    Obtém o caminho real do arquivo SQLite
    utilizado pela aplicação.
    """

    caminho = db.engine.url.database

    if not caminho:
        raise RuntimeError(
            "Não foi possível identificar o banco de dados."
        )

    return Path(
        caminho
    ).resolve()


def obter_informacoes_banco():
    caminho_banco = obter_caminho_banco()

    if not caminho_banco.is_file():
        return {
            "existe": False,
            "caminho": str(caminho_banco),
            "tamanho": 0,
            "tamanho_formatado": "0 KB",
            "modificado_em": None
        }

    tamanho = caminho_banco.stat().st_size

    if tamanho >= 1024 * 1024:
        tamanho_formatado = (
            f"{tamanho / (1024 * 1024):.2f} MB"
        )
    else:
        tamanho_formatado = (
            f"{tamanho / 1024:.2f} KB"
        )

    modificado_em = datetime.fromtimestamp(
        caminho_banco.stat().st_mtime
    )

    return {
        "existe": True,
        "caminho": str(caminho_banco),
        "tamanho": tamanho,
        "tamanho_formatado": tamanho_formatado,
        "modificado_em": modificado_em
    }


def criar_backup_temporario():
    """
    Cria uma cópia consistente do banco usando
    a API oficial de backup do SQLite.
    """

    caminho_origem = obter_caminho_banco()

    if not caminho_origem.is_file():
        raise FileNotFoundError(
            "O arquivo do banco de dados não foi encontrado."
        )

    arquivo_temporario = tempfile.NamedTemporaryFile(
        prefix="backup_sistema_",
        suffix=".db",
        delete=False
    )

    caminho_backup = Path(
        arquivo_temporario.name
    )

    arquivo_temporario.close()

    conexao_origem = None
    conexao_destino = None

    try:
        conexao_origem = sqlite3.connect(
            str(caminho_origem)
        )

        conexao_destino = sqlite3.connect(
            str(caminho_backup)
        )

        with conexao_destino:
            conexao_origem.backup(
                conexao_destino
            )

    except Exception:
        if caminho_backup.exists():
            caminho_backup.unlink()

        raise

    finally:
        if conexao_destino:
            conexao_destino.close()

        if conexao_origem:
            conexao_origem.close()

    return caminho_backup


# =====================================
# CENTRAL DE CONFIGURAÇÕES
# =====================================
@configuracao_bp.route("/")
@login_required
def pagina_configuracoes():
    configuracao = obter_configuracao()

    return render_template(
        "configuracoes/index.html",
        configuracao=configuracao
    )


# =====================================
# DADOS DO ESCRITÓRIO
# =====================================
@configuracao_bp.route(
    "/dados-escritorio",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def dados_escritorio():
    configuracao = obter_configuracao()

    if request.method == "POST":
        configuracao.nome_escritorio = request.form.get(
            "nome_escritorio",
            ""
        ).strip() or "Sistema Jurídico"

        configuracao.nome_fantasia = request.form.get(
            "nome_fantasia",
            ""
        ).strip()

        configuracao.cnpj = request.form.get(
            "cnpj",
            ""
        ).strip()

        configuracao.oab = request.form.get(
            "oab",
            ""
        ).strip()

        configuracao.telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        configuracao.whatsapp = request.form.get(
            "whatsapp",
            ""
        ).strip()

        configuracao.email = request.form.get(
            "email",
            ""
        ).strip().lower()

        configuracao.site = request.form.get(
            "site",
            ""
        ).strip()

        configuracao.cep = request.form.get(
            "cep",
            ""
        ).strip()

        configuracao.rua = request.form.get(
            "rua",
            ""
        ).strip()

        configuracao.numero = request.form.get(
            "numero",
            ""
        ).strip()

        configuracao.complemento = request.form.get(
            "complemento",
            ""
        ).strip()

        configuracao.bairro = request.form.get(
            "bairro",
            ""
        ).strip()

        configuracao.cidade = request.form.get(
            "cidade",
            ""
        ).strip()

        configuracao.estado = request.form.get(
            "estado",
            ""
        ).strip().upper()[:2]

        configuracao.cor_principal = request.form.get(
            "cor_principal",
            "#212529"
        ).strip() or "#212529"

        configuracao.cor_secundaria = request.form.get(
            "cor_secundaria",
            "#0d6efd"
        ).strip() or "#0d6efd"

        configuracao.texto_rodape = request.form.get(
            "texto_rodape",
            ""
        ).strip()

        arquivo_logo = request.files.get(
            "logo"
        )

        if arquivo_logo and arquivo_logo.filename:
            if not extensao_logo_permitida(
                arquivo_logo.filename
            ):
                flash(
                    (
                        "A logo deve estar nos formatos "
                        "PNG, JPG, JPEG ou WEBP."
                    ),
                    "danger"
                )

                return redirect(
                    url_for(
                        "configuracoes.dados_escritorio"
                    )
                )

            nome_seguro = secure_filename(
                arquivo_logo.filename
            )

            extensao = nome_seguro.rsplit(
                ".",
                1
            )[1].lower()

            novo_nome = (
                f"logo_{uuid4().hex}.{extensao}"
            )

            caminho_logo = os.path.join(
                pasta_logos(),
                novo_nome
            )

            arquivo_logo.save(
                caminho_logo
            )

            if configuracao.logo:
                caminho_antigo = os.path.join(
                    current_app.static_folder,
                    configuracao.logo
                )

                if os.path.isfile(
                    caminho_antigo
                ):
                    try:
                        os.remove(
                            caminho_antigo
                        )
                    except OSError:
                        pass

            configuracao.logo = os.path.join(
                "uploads",
                "logos",
                novo_nome
            ).replace(
                "\\",
                "/"
            )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do escritório.",
                "danger"
            )

            return render_template(
                "configuracoes/dados_escritorio.html",
                configuracao=configuracao
            )

        flash(
            "✅ Dados do escritório salvos com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "configuracoes.dados_escritorio"
            )
        )

    return render_template(
        "configuracoes/dados_escritorio.html",
        configuracao=configuracao
    )


# =====================================
# REMOVER LOGO
# =====================================
@configuracao_bp.route(
    "/dados-escritorio/remover-logo",
    methods=[
        "POST"
    ]
)
@login_required
def remover_logo():
    configuracao = obter_configuracao()

    if configuracao.logo:
        caminho_logo = os.path.join(
            current_app.static_folder,
            configuracao.logo
        )

        if os.path.isfile(
            caminho_logo
        ):
            try:
                os.remove(
                    caminho_logo
                )
            except OSError:
                pass

        configuracao.logo = None

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível remover a logo.",
                "danger"
            )

            return redirect(
                url_for(
                    "configuracoes.dados_escritorio"
                )
            )

        flash(
            "🗑 Logo removida com sucesso!",
            "success"
        )

    else:
        flash(
            "Nenhuma logo cadastrada.",
            "warning"
        )

    return redirect(
        url_for(
            "configuracoes.dados_escritorio"
        )
    )


# =====================================
# CENTRAL DE BACKUP
# =====================================
@configuracao_bp.route(
    "/backup"
)
@admin_required
def pagina_backup():
    informacoes_banco = obter_informacoes_banco()

    return render_template(
        "configuracoes/backup.html",
        informacoes_banco=informacoes_banco
    )


# =====================================
# BAIXAR BACKUP
# =====================================
@configuracao_bp.route(
    "/backup/download",
    methods=[
        "POST"
    ]
)
@admin_required
def baixar_backup():
    try:
        caminho_backup = criar_backup_temporario()

    except FileNotFoundError:
        flash(
            "O banco de dados não foi encontrado.",
            "danger"
        )

        return redirect(
            url_for(
                "configuracoes.pagina_backup"
            )
        )

    except Exception as erro:
        current_app.logger.exception(
            "Erro ao criar backup: %s",
            erro
        )

        flash(
            "Não foi possível criar o backup do sistema.",
            "danger"
        )

        return redirect(
            url_for(
                "configuracoes.pagina_backup"
            )
        )

    nome_download = datetime.now().strftime(
        "backup_sistema_%Y-%m-%d_%H-%M-%S.db"
    )

    @after_this_request
    def remover_arquivo_temporario(resposta):
        try:
            if caminho_backup.exists():
                caminho_backup.unlink()
        except OSError:
            current_app.logger.warning(
                "Não foi possível remover o backup temporário."
            )

        return resposta

    return send_file(
        caminho_backup,
        as_attachment=True,
        download_name=nome_download,
        mimetype="application/octet-stream"
    )