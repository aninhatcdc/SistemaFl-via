from flask import Blueprint, render_template
from datetime import date, timedelta
from flask_login import login_required

from models.cliente import Cliente
from models.processo import Processo
from models.documento import Documento
from models.agenda import EventoAgenda

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def dashboard():

    total_clientes = Cliente.query.count()
    total_processos = Processo.query.count()
    total_documentos = Documento.query.count()

    processos_ativos = Processo.query.filter_by(
        situacao="Em andamento"
    ).count()

    ultimos_clientes = (
        Cliente.query
        .order_by(Cliente.id.desc())
        .limit(5)
        .all()
    )

    ultimos_documentos = (
        Documento.query
        .order_by(Documento.id.desc())
        .limit(5)
        .all()
    )

    proximos_prazos = (
        Processo.query
        .filter(Processo.proximo_prazo != None)
        .order_by(Processo.proximo_prazo.asc())
        .limit(5)
        .all()
    )

    # ==========================
    # RESUMO DA AGENDA
    # ==========================

    hoje = date.today()
    amanha = hoje + timedelta(days=1)
    fim_semana = hoje + timedelta(days=7)

    eventos_hoje = EventoAgenda.query.filter(
        EventoAgenda.concluido == False,
        EventoAgenda.data == hoje
    ).count()

    eventos_amanha = EventoAgenda.query.filter(
        EventoAgenda.concluido == False,
        EventoAgenda.data == amanha
    ).count()

    eventos_semana = EventoAgenda.query.filter(
        EventoAgenda.concluido == False,
        EventoAgenda.data > amanha,
        EventoAgenda.data <= fim_semana
    ).count()

    proximos_eventos = (
        EventoAgenda.query
        .filter(
            EventoAgenda.concluido == False,
            EventoAgenda.data >= hoje
        )
        .order_by(
            EventoAgenda.data.asc(),
            EventoAgenda.horario.asc()
        )
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_processos=total_processos,
        total_documentos=total_documentos,
        processos_ativos=processos_ativos,
        ultimos_clientes=ultimos_clientes,
        ultimos_documentos=ultimos_documentos,
        proximos_prazos=proximos_prazos,
        eventos_hoje=eventos_hoje,
        eventos_amanha=eventos_amanha,
        eventos_semana=eventos_semana,
        proximos_eventos=proximos_eventos
    )