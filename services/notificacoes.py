from datetime import date, datetime, timedelta

from flask_login import current_user

from models.agenda import EventoAgenda
from models.cliente import Cliente
from models.financeiro import LancamentoFinanceiro
from models.processo import Processo


# =====================================
# CONFIGURAÇÕES
# =====================================
DIAS_PROXIMOS = 7


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def criar_notificacao(
    categoria,
    titulo,
    descricao,
    data_referencia,
    prioridade,
    icone,
    url,
    identificador=None
):
    return {
        "categoria": categoria,
        "titulo": titulo,
        "descricao": descricao,
        "data_referencia": data_referencia,
        "prioridade": prioridade,
        "icone": icone,
        "url": url,
        "identificador": identificador
    }


def texto_data(data_referencia):
    hoje = date.today()

    if not data_referencia:
        return ""

    diferenca = (
        data_referencia
        - hoje
    ).days

    if diferenca < 0:
        quantidade = abs(
            diferenca
        )

        if quantidade == 1:
            return "Vencido há 1 dia"

        return f"Vencido há {quantidade} dias"

    if diferenca == 0:
        return "Hoje"

    if diferenca == 1:
        return "Amanhã"

    return (
        data_referencia
        .strftime(
            "%d/%m/%Y"
        )
    )


def prioridade_ordenacao(prioridade):
    prioridades = {
        "alta": 1,
        "media": 2,
        "baixa": 3
    }

    return prioridades.get(
        prioridade,
        4
    )


# =====================================
# ALERTAS DA AGENDA
# =====================================
def obter_alertas_agenda():
    hoje = date.today()

    limite = hoje + timedelta(
        days=DIAS_PROXIMOS
    )

    eventos = (
        EventoAgenda.query
        .filter(
            EventoAgenda.concluido.is_(False),
            EventoAgenda.data <= limite
        )
        .order_by(
            EventoAgenda.data.asc(),
            EventoAgenda.horario.asc()
        )
        .all()
    )

    notificacoes = []

    for evento in eventos:
        if evento.data < hoje:
            prioridade = "alta"

        elif evento.data == hoje:
            prioridade = "alta"

        elif evento.data == hoje + timedelta(days=1):
            prioridade = "media"

        else:
            prioridade = "baixa"

        tipo_evento = (
            evento.tipo
            or "Evento"
        )

        descricao_partes = [
            tipo_evento,
            texto_data(
                evento.data
            )
        ]

        if evento.horario:
            descricao_partes.append(
                evento.horario.strftime(
                    "%H:%M"
                )
            )

        if evento.cliente:
            descricao_partes.append(
                evento.cliente.nome
            )

        notificacoes.append(
            criar_notificacao(
                categoria="agenda",
                titulo=evento.titulo,
                descricao=" • ".join(
                    descricao_partes
                ),
                data_referencia=evento.data,
                prioridade=prioridade,
                icone="📅",
                url="/agenda",
                identificador=evento.id
            )
        )

    return notificacoes


# =====================================
# PRAZOS DE PROCESSOS
# =====================================
def obter_alertas_processos():
    hoje = date.today()

    limite = hoje + timedelta(
        days=DIAS_PROXIMOS
    )

    processos = (
        Processo.query
        .filter(
            Processo.proximo_prazo.isnot(None),
            Processo.proximo_prazo <= limite
        )
        .order_by(
            Processo.proximo_prazo.asc()
        )
        .all()
    )

    notificacoes = []

    for processo in processos:
        if processo.proximo_prazo < hoje:
            prioridade = "alta"

        elif processo.proximo_prazo == hoje:
            prioridade = "alta"

        elif processo.proximo_prazo == hoje + timedelta(days=1):
            prioridade = "media"

        else:
            prioridade = "baixa"

        cliente_nome = (
            processo.cliente.nome
            if processo.cliente
            else "Cliente não informado"
        )

        descricao = (
            f"Processo {processo.numero}"
            f" • {cliente_nome}"
            f" • {texto_data(processo.proximo_prazo)}"
        )

        url = (
            f"/clientes/{processo.cliente_id}"
            if processo.cliente_id
            else "/processos"
        )

        notificacoes.append(
            criar_notificacao(
                categoria="processo",
                titulo="Prazo processual",
                descricao=descricao,
                data_referencia=processo.proximo_prazo,
                prioridade=prioridade,
                icone="⚖️",
                url=url,
                identificador=processo.id
            )
        )

    return notificacoes


# =====================================
# ANIVERSÁRIOS
# =====================================
def obter_alertas_aniversarios():
    hoje = date.today()

    clientes = (
        Cliente.query
        .filter(
            Cliente.ativo.is_(True),
            Cliente.data_nascimento.isnot(None)
        )
        .order_by(
            Cliente.nome.asc()
        )
        .all()
    )

    notificacoes = []

    for cliente in clientes:
        nascimento = cliente.data_nascimento

        try:
            aniversario_ano = nascimento.replace(
                year=hoje.year
            )

        except ValueError:
            aniversario_ano = date(
                hoje.year,
                2,
                28
            )

        if aniversario_ano < hoje:
            try:
                aniversario_ano = nascimento.replace(
                    year=hoje.year + 1
                )

            except ValueError:
                aniversario_ano = date(
                    hoje.year + 1,
                    2,
                    28
                )

        dias_para_aniversario = (
            aniversario_ano
            - hoje
        ).days

        if dias_para_aniversario > DIAS_PROXIMOS:
            continue

        if dias_para_aniversario == 0:
            prioridade = "media"
            descricao = "Aniversário hoje"

        elif dias_para_aniversario == 1:
            prioridade = "baixa"
            descricao = "Aniversário amanhã"

        else:
            prioridade = "baixa"
            descricao = (
                f"Aniversário em "
                f"{dias_para_aniversario} dias"
            )

        notificacoes.append(
            criar_notificacao(
                categoria="aniversario",
                titulo=cliente.nome,
                descricao=descricao,
                data_referencia=aniversario_ano,
                prioridade=prioridade,
                icone="🎂",
                url=f"/clientes/{cliente.id}",
                identificador=cliente.id
            )
        )

    return notificacoes


# =====================================
# FINANCEIRO
# =====================================
def obter_alertas_financeiros():
    if not current_user.is_authenticated:
        return []

    if not current_user.pode_acessar_financeiro:
        return []

    hoje = date.today()

    lancamentos = (
        LancamentoFinanceiro.query
        .filter(
            LancamentoFinanceiro.status.in_(
                [
                    "Pendente",
                    "Previsto"
                ]
            )
        )
        .order_by(
            LancamentoFinanceiro.competencia_ano.asc(),
            LancamentoFinanceiro.competencia_mes.asc()
        )
        .all()
    )

    notificacoes = []

    for lancamento in lancamentos:
        competencia = date(
            lancamento.competencia_ano,
            lancamento.competencia_mes,
            1
        )

        mes_atual = date(
            hoje.year,
            hoje.month,
            1
        )

        if competencia < mes_atual:
            prioridade = "alta"
            texto_competencia = "Competência vencida"

        elif competencia == mes_atual:
            prioridade = "media"
            texto_competencia = "Competência atual"

        else:
            diferenca_meses = (
                (
                    competencia.year
                    - mes_atual.year
                ) * 12
                + competencia.month
                - mes_atual.month
            )

            if diferenca_meses > 1:
                continue

            prioridade = "baixa"
            texto_competencia = "Próxima competência"

        descricao = (
            f"{texto_competencia}"
            f" • {lancamento.mes_nome}"
            f"/{lancamento.competencia_ano}"
            f" • R$ {lancamento.valor:,.2f}"
        )

        notificacoes.append(
            criar_notificacao(
                categoria="financeiro",
                titulo=lancamento.descricao,
                descricao=descricao,
                data_referencia=competencia,
                prioridade=prioridade,
                icone="💰",
                url=(
                    "/financeiro"
                    f"?ano={lancamento.competencia_ano}"
                ),
                identificador=lancamento.id
            )
        )

    return notificacoes


# =====================================
# CENTRAL DE NOTIFICAÇÕES
# =====================================
def obter_notificacoes():
    notificacoes = []

    notificacoes.extend(
        obter_alertas_agenda()
    )

    notificacoes.extend(
        obter_alertas_processos()
    )

    notificacoes.extend(
        obter_alertas_aniversarios()
    )

    notificacoes.extend(
        obter_alertas_financeiros()
    )

    notificacoes.sort(
        key=lambda item: (
            prioridade_ordenacao(
                item["prioridade"]
            ),
            item["data_referencia"]
            or date.max,
            item["titulo"].lower()
        )
    )

    return notificacoes


def obter_resumo_notificacoes():
    notificacoes = obter_notificacoes()

    quantidade_alta = sum(
        1
        for notificacao in notificacoes
        if notificacao["prioridade"] == "alta"
    )

    quantidade_media = sum(
        1
        for notificacao in notificacoes
        if notificacao["prioridade"] == "media"
    )

    quantidade_baixa = sum(
        1
        for notificacao in notificacoes
        if notificacao["prioridade"] == "baixa"
    )

    return {
        "notificacoes": notificacoes,
        "total": len(
            notificacoes
        ),
        "alta": quantidade_alta,
        "media": quantidade_media,
        "baixa": quantidade_baixa
    }