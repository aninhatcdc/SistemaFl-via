from datetime import datetime, date, timedelta
from flask_login import login_required

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models import db
from models.agenda import EventoAgenda
from models.cliente import Cliente
from models.processo import Processo


agenda_bp = Blueprint("agenda", __name__)


# ==========================
# LISTAR EVENTOS
# ==========================
@agenda_bp.route("/agenda")
@login_required
def listar_eventos():
    hoje = date.today()
    amanha = hoje + timedelta(days=1)
    limite_semana = hoje + timedelta(days=7)

    eventos_pendentes = (
        EventoAgenda.query
        .filter_by(concluido=False)
        .order_by(
            EventoAgenda.data.asc(),
            EventoAgenda.horario.asc()
        )
        .all()
    )

    eventos_concluidos = (
        EventoAgenda.query
        .filter_by(concluido=True)
        .order_by(
            EventoAgenda.data.desc(),
            EventoAgenda.horario.desc()
        )
        .limit(10)
        .all()
    )

    eventos_atrasados = []
    eventos_hoje = []
    eventos_amanha = []
    eventos_semana = []
    eventos_futuros = []

    for evento in eventos_pendentes:

        if evento.data < hoje:
            eventos_atrasados.append(evento)

        elif evento.data == hoje:
            eventos_hoje.append(evento)

        elif evento.data == amanha:
            eventos_amanha.append(evento)

        elif evento.data <= limite_semana:
            eventos_semana.append(evento)

        else:
            eventos_futuros.append(evento)

    return render_template(
        "agenda/listar.html",
        eventos_atrasados=eventos_atrasados,
        eventos_hoje=eventos_hoje,
        eventos_amanha=eventos_amanha,
        eventos_semana=eventos_semana,
        eventos_futuros=eventos_futuros,
        eventos_concluidos=eventos_concluidos
    )


# ==========================
# NOVO EVENTO
# ==========================
@agenda_bp.route("/agenda/novo", methods=["GET", "POST"])
@login_required
def novo_evento():
    clientes = Cliente.query.order_by(Cliente.nome.asc()).all()
    processos = Processo.query.order_by(Processo.numero.asc()).all()

    if request.method == "POST":
        evento = EventoAgenda(
            titulo=request.form["titulo"],
            tipo=request.form["tipo"],
            descricao=request.form.get("descricao", ""),
            local=request.form.get("local", "")
        )

        data = request.form["data"]
        horario = request.form.get("horario", "")
        cliente_id = request.form.get("cliente_id", "")
        processo_id = request.form.get("processo_id", "")

        evento.data = datetime.strptime(
            data,
            "%Y-%m-%d"
        ).date()

        if horario:
            evento.horario = datetime.strptime(
                horario,
                "%H:%M"
            ).time()

        if cliente_id:
            evento.cliente_id = int(cliente_id)

        if processo_id:
            evento.processo_id = int(processo_id)

        db.session.add(evento)
        db.session.commit()

        flash("📅 Evento cadastrado com sucesso!", "success")

        return redirect(
            url_for("agenda.listar_eventos")
        )

    return render_template(
        "agenda/novo.html",
        clientes=clientes,
        processos=processos
    )


# ==========================
# EDITAR EVENTO
# ==========================
@agenda_bp.route("/agenda/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_evento(id):
    evento = EventoAgenda.query.get_or_404(id)

    clientes = Cliente.query.order_by(Cliente.nome.asc()).all()
    processos = Processo.query.order_by(Processo.numero.asc()).all()

    if request.method == "POST":
        evento.titulo = request.form["titulo"]
        evento.tipo = request.form["tipo"]
        evento.descricao = request.form.get("descricao", "")
        evento.local = request.form.get("local", "")

        data = request.form["data"]
        horario = request.form.get("horario", "")
        cliente_id = request.form.get("cliente_id", "")
        processo_id = request.form.get("processo_id", "")

        evento.data = datetime.strptime(
            data,
            "%Y-%m-%d"
        ).date()

        if horario:
            evento.horario = datetime.strptime(
                horario,
                "%H:%M"
            ).time()
        else:
            evento.horario = None

        evento.cliente_id = int(cliente_id) if cliente_id else None
        evento.processo_id = int(processo_id) if processo_id else None

        db.session.commit()

        flash("✏️ Evento atualizado com sucesso!", "warning")

        return redirect(
            url_for("agenda.listar_eventos")
        )

    return render_template(
        "agenda/editar.html",
        evento=evento,
        clientes=clientes,
        processos=processos
    )


# ==========================
# CONCLUIR OU REABRIR EVENTO
# ==========================
@agenda_bp.route("/agenda/<int:id>/concluir", methods=["POST"])
@login_required
def concluir_evento(id):
    evento = EventoAgenda.query.get_or_404(id)

    evento.concluido = not evento.concluido

    db.session.commit()

    if evento.concluido:
        flash("✅ Evento concluído com sucesso!", "success")
    else:
        flash("↩️ Evento reaberto com sucesso!", "info")

    return redirect(
        url_for("agenda.listar_eventos")
    )


# ==========================
# EXCLUIR EVENTO
# ==========================
@agenda_bp.route("/agenda/<int:id>/excluir", methods=["POST"])
@login_required
def excluir_evento(id):
    evento = EventoAgenda.query.get_or_404(id)

    db.session.delete(evento)
    db.session.commit()

    flash("🗑️ Evento excluído com sucesso!", "danger")

    return redirect(
        url_for("agenda.listar_eventos")
    )