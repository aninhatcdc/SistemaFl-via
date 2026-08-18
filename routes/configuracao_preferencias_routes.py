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
from models.configuracao import ConfiguracaoEscritorio
from utils.permissoes import admin_required


preferencias_bp = Blueprint(
    "preferencias",
    __name__,
    url_prefix="/configuracoes/preferencias"
)


# =====================================
# OPÇÕES PERMITIDAS
# =====================================
ITENS_POR_PAGINA_VALIDOS = {
    5,
    10,
    15,
    20,
    30,
    50
}

DIAS_NOTIFICACOES_VALIDOS = {
    1,
    3,
    5,
    7,
    10,
    15,
    30
}

PAGINAS_INICIAIS_VALIDAS = {
    "dashboard",
    "clientes",
    "processos",
    "agenda",
    "financeiro"
}

FORMATOS_DATA_VALIDOS = {
    "DD/MM/AAAA",
    "AAAA-MM-DD",
    "MM/DD/AAAA"
}


# =====================================
# FUNÇÕES AUXILIARES
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
        cor_secundaria="#0d6efd",
        itens_por_pagina=10,
        dias_notificacoes=7,
        exibir_notificacoes_baixa=True,
        modo_compacto_tabelas=False,
        pagina_inicial="dashboard",
        formato_data="DD/MM/AAAA"
    )

    db.session.add(
        configuracao
    )

    db.session.commit()

    return configuracao


def obter_numero_inteiro(
    nome_campo,
    valor_padrao
):
    try:
        return int(
            request.form.get(
                nome_campo,
                valor_padrao
            )
        )

    except (
        TypeError,
        ValueError
    ):
        return valor_padrao


# =====================================
# PREFERÊNCIAS
# =====================================
@preferencias_bp.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
@admin_required
def preferencias():
    configuracao = obter_configuracao()

    if request.method == "POST":
        itens_por_pagina = obter_numero_inteiro(
            "itens_por_pagina",
            10
        )

        dias_notificacoes = obter_numero_inteiro(
            "dias_notificacoes",
            7
        )

        pagina_inicial = request.form.get(
            "pagina_inicial",
            "dashboard"
        ).strip()

        formato_data = request.form.get(
            "formato_data",
            "DD/MM/AAAA"
        ).strip()

        modo_compacto_tabelas = (
            request.form.get(
                "modo_compacto_tabelas"
            )
            == "on"
        )

        exibir_notificacoes_baixa = (
            request.form.get(
                "exibir_notificacoes_baixa"
            )
            == "on"
        )

        # =====================================
        # VALIDAÇÕES
        # =====================================
        if (
            itens_por_pagina
            not in ITENS_POR_PAGINA_VALIDOS
        ):
            flash(
                "Selecione uma quantidade válida de itens por página.",
                "danger"
            )

            return render_template(
                "configuracoes/preferencias.html",
                configuracao=configuracao
            )

        if (
            dias_notificacoes
            not in DIAS_NOTIFICACOES_VALIDOS
        ):
            flash(
                "Selecione um período válido para as notificações.",
                "danger"
            )

            return render_template(
                "configuracoes/preferencias.html",
                configuracao=configuracao
            )

        if (
            pagina_inicial
            not in PAGINAS_INICIAIS_VALIDAS
        ):
            flash(
                "Selecione uma página inicial válida.",
                "danger"
            )

            return render_template(
                "configuracoes/preferencias.html",
                configuracao=configuracao
            )

        if (
            formato_data
            not in FORMATOS_DATA_VALIDOS
        ):
            flash(
                "Selecione um formato de data válido.",
                "danger"
            )

            return render_template(
                "configuracoes/preferencias.html",
                configuracao=configuracao
            )

        configuracao.itens_por_pagina = (
            itens_por_pagina
        )

        configuracao.dias_notificacoes = (
            dias_notificacoes
        )

        configuracao.exibir_notificacoes_baixa = (
            exibir_notificacoes_baixa
        )

        configuracao.modo_compacto_tabelas = (
            modo_compacto_tabelas
        )

        configuracao.pagina_inicial = (
            pagina_inicial
        )

        configuracao.formato_data = (
            formato_data
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar as preferências.",
                "danger"
            )

            return render_template(
                "configuracoes/preferencias.html",
                configuracao=configuracao
            )

        flash(
            "✅ Preferências salvas com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "preferencias.preferencias"
            )
        )

    return render_template(
        "configuracoes/preferencias.html",
        configuracao=configuracao
    )