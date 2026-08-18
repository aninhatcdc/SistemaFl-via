from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from sqlalchemy.exc import SQLAlchemyError

from models import db
from models.configuracao_arquivos import ConfiguracaoArquivos
from utils.permissoes import admin_required


configuracao_arquivos_bp = Blueprint(
    "configuracao_arquivos",
    __name__,
    url_prefix="/configuracoes/arquivos"
)


TAMANHOS_VALIDOS = {
    5,
    10,
    20,
    30,
    50,
    100
}


EXTENSOES_PADRAO = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "txt"
}


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def obter_configuracao_arquivos():
    configuracao = (
        ConfiguracaoArquivos.query
        .order_by(
            ConfiguracaoArquivos.id.asc()
        )
        .first()
    )

    if configuracao:
        return configuracao

    configuracao = ConfiguracaoArquivos(
        tamanho_maximo_mb=20,
        extensoes_permitidas=",".join(
            sorted(
                EXTENSOES_PADRAO
            )
        ),
        organizar_por_cliente=True,
        organizar_por_processo=False,
        permitir_substituir=False,
        renomear_automaticamente=True
    )

    db.session.add(
        configuracao
    )

    db.session.commit()

    return configuracao


def normalizar_extensoes(valor):
    extensoes = set()

    partes = (
        str(
            valor or ""
        )
        .replace(
            ";",
            ","
        )
        .replace(
            "\n",
            ","
        )
        .split(
            ","
        )
    )

    for parte in partes:
        extensao = (
            parte
            .strip()
            .lower()
            .lstrip(
                "."
            )
        )

        if not extensao:
            continue

        if not extensao.isalnum():
            raise ValueError(
                (
                    "As extensões devem conter apenas "
                    "letras e números."
                )
            )

        extensoes.add(
            extensao
        )

    if not extensoes:
        raise ValueError(
            "Informe pelo menos uma extensão permitida."
        )

    return ",".join(
        sorted(
            extensoes
        )
    )


# =====================================
# CONFIGURAÇÕES DE ARQUIVOS
# =====================================
@configuracao_arquivos_bp.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
@admin_required
def configuracoes_arquivos():
    configuracao = obter_configuracao_arquivos()

    if request.method == "POST":
        tamanho_maximo_mb = request.form.get(
            "tamanho_maximo_mb",
            20,
            type=int
        )

        extensoes_texto = request.form.get(
            "extensoes_permitidas",
            ""
        )

        organizar_por_cliente = (
            request.form.get(
                "organizar_por_cliente"
            )
            == "on"
        )

        organizar_por_processo = (
            request.form.get(
                "organizar_por_processo"
            )
            == "on"
        )

        permitir_substituir = (
            request.form.get(
                "permitir_substituir"
            )
            == "on"
        )

        renomear_automaticamente = (
            request.form.get(
                "renomear_automaticamente"
            )
            == "on"
        )

        if tamanho_maximo_mb not in TAMANHOS_VALIDOS:
            flash(
                "Selecione um limite de tamanho válido.",
                "danger"
            )

            return render_template(
                "configuracoes/arquivos.html",
                configuracao=configuracao
            )

        try:
            extensoes_permitidas = normalizar_extensoes(
                extensoes_texto
            )

        except ValueError as erro:
            flash(
                str(
                    erro
                ),
                "danger"
            )

            return render_template(
                "configuracoes/arquivos.html",
                configuracao=configuracao
            )

        if not organizar_por_cliente and not organizar_por_processo:
            flash(
                (
                    "Selecione pelo menos uma forma "
                    "de organização dos arquivos."
                ),
                "danger"
            )

            return render_template(
                "configuracoes/arquivos.html",
                configuracao=configuracao
            )

        configuracao.tamanho_maximo_mb = (
            tamanho_maximo_mb
        )

        configuracao.extensoes_permitidas = (
            extensoes_permitidas
        )

        configuracao.organizar_por_cliente = (
            organizar_por_cliente
        )

        configuracao.organizar_por_processo = (
            organizar_por_processo
        )

        configuracao.permitir_substituir = (
            permitir_substituir
        )

        configuracao.renomear_automaticamente = (
            renomear_automaticamente
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                (
                    "Não foi possível salvar as "
                    "configurações de arquivos."
                ),
                "danger"
            )

            return render_template(
                "configuracoes/arquivos.html",
                configuracao=configuracao
            )

        flash(
            "✅ Configurações de arquivos salvas com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "configuracao_arquivos.configuracoes_arquivos"
            )
        )

    return render_template(
        "configuracoes/arquivos.html",
        configuracao=configuracao
    )