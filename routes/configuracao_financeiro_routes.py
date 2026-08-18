from decimal import Decimal, InvalidOperation

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
from models.configuracao_financeiro import ConfiguracaoFinanceiro
from utils.permissoes import financeiro_required


configuracao_financeiro_bp = Blueprint(
    "configuracao_financeiro",
    __name__,
    url_prefix="/configuracoes/financeiro"
)


STATUS_VALIDOS = {
    "Pago",
    "Pendente",
    "Previsto"
}

DIAS_ALERTA_VALIDOS = {
    1,
    3,
    5,
    7,
    10,
    15,
    30
}


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def obter_configuracao_financeiro():
    configuracao = (
        ConfiguracaoFinanceiro.query
        .order_by(
            ConfiguracaoFinanceiro.id.asc()
        )
        .first()
    )

    if configuracao:
        return configuracao

    configuracao = ConfiguracaoFinanceiro(
        categoria_padrao="Outros",
        forma_pagamento_padrao="Pix",
        status_padrao="Pago",
        dias_alerta=7,
        avisar_vencimentos=True,
        destacar_recorrentes=True,
        meta_mensal=Decimal("0.00"),
        meta_anual=Decimal("0.00"),
        mostrar_grafico_categorias=True,
        mostrar_comparativo_anual=True
    )

    db.session.add(
        configuracao
    )

    db.session.commit()

    return configuracao


def converter_valor_monetario(valor_texto):
    if valor_texto is None:
        return Decimal(
            "0.00"
        )

    valor_texto = str(
        valor_texto
    ).strip()

    if not valor_texto:
        return Decimal(
            "0.00"
        )

    valor_texto = (
        valor_texto
        .replace(
            "R$",
            ""
        )
        .replace(
            " ",
            ""
        )
        .replace(
            ".",
            ""
        )
        .replace(
            ",",
            "."
        )
    )

    try:
        valor = Decimal(
            valor_texto
        )

    except InvalidOperation:
        raise ValueError(
            "Informe um valor monetário válido."
        )

    if valor < 0:
        raise ValueError(
            "A meta não pode ser negativa."
        )

    return valor.quantize(
        Decimal(
            "0.01"
        )
    )


# =====================================
# CONFIGURAÇÕES FINANCEIRAS
# =====================================
@configuracao_financeiro_bp.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
@financeiro_required
def configuracoes_financeiras():
    configuracao = obter_configuracao_financeiro()

    if request.method == "POST":
        categoria_padrao = request.form.get(
            "categoria_padrao",
            ""
        ).strip()

        forma_pagamento_padrao = request.form.get(
            "forma_pagamento_padrao",
            ""
        ).strip()

        status_padrao = request.form.get(
            "status_padrao",
            "Pago"
        ).strip()

        dias_alerta = request.form.get(
            "dias_alerta",
            7,
            type=int
        )

        avisar_vencimentos = (
            request.form.get(
                "avisar_vencimentos"
            )
            == "on"
        )

        destacar_recorrentes = (
            request.form.get(
                "destacar_recorrentes"
            )
            == "on"
        )

        mostrar_grafico_categorias = (
            request.form.get(
                "mostrar_grafico_categorias"
            )
            == "on"
        )

        mostrar_comparativo_anual = (
            request.form.get(
                "mostrar_comparativo_anual"
            )
            == "on"
        )

        if not categoria_padrao:
            flash(
                "Informe a categoria padrão.",
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        if not forma_pagamento_padrao:
            flash(
                "Informe a forma de pagamento padrão.",
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        if status_padrao not in STATUS_VALIDOS:
            flash(
                "Selecione um status padrão válido.",
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        if dias_alerta not in DIAS_ALERTA_VALIDOS:
            flash(
                "Selecione um período de alerta válido.",
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        try:
            meta_mensal = converter_valor_monetario(
                request.form.get(
                    "meta_mensal",
                    ""
                )
            )

            meta_anual = converter_valor_monetario(
                request.form.get(
                    "meta_anual",
                    ""
                )
            )

        except ValueError as erro:
            flash(
                str(
                    erro
                ),
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        configuracao.categoria_padrao = (
            categoria_padrao
        )

        configuracao.forma_pagamento_padrao = (
            forma_pagamento_padrao
        )

        configuracao.status_padrao = (
            status_padrao
        )

        configuracao.dias_alerta = (
            dias_alerta
        )

        configuracao.avisar_vencimentos = (
            avisar_vencimentos
        )

        configuracao.destacar_recorrentes = (
            destacar_recorrentes
        )

        configuracao.meta_mensal = (
            meta_mensal
        )

        configuracao.meta_anual = (
            meta_anual
        )

        configuracao.mostrar_grafico_categorias = (
            mostrar_grafico_categorias
        )

        configuracao.mostrar_comparativo_anual = (
            mostrar_comparativo_anual
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar as configurações financeiras.",
                "danger"
            )

            return render_template(
                "configuracoes/financeiro.html",
                configuracao=configuracao
            )

        flash(
            "✅ Configurações financeiras salvas com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "configuracao_financeiro.configuracoes_financeiras"
            )
        )

    return render_template(
        "configuracoes/financeiro.html",
        configuracao=configuracao
    )