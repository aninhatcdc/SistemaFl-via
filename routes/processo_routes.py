from datetime import datetime, date
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
from models.cliente import Cliente
from models.processo import Processo
from models.agenda import EventoAgenda


processo_bp = Blueprint("processos", __name__)


# ==========================
# SINCRONIZAR PRAZO COM A AGENDA
# ==========================
def sincronizar_prazo_agenda(processo):
    evento_prazo = EventoAgenda.query.filter_by(
        processo_id=processo.id,
        tipo="Prazo"
    ).first()

    if processo.proximo_prazo:
        titulo = f"Prazo do processo {processo.numero}"

        if evento_prazo:
            evento_prazo.titulo = titulo
            evento_prazo.data = processo.proximo_prazo
            evento_prazo.cliente_id = processo.cliente_id
            evento_prazo.descricao = (
                f"Prazo automático vinculado ao processo "
                f"{processo.numero}."
            )
            evento_prazo.concluido = False

        else:
            evento_prazo = EventoAgenda(
                titulo=titulo,
                tipo="Prazo",
                data=processo.proximo_prazo,
                descricao=(
                    f"Prazo automático vinculado ao processo "
                    f"{processo.numero}."
                ),
                cliente_id=processo.cliente_id,
                processo_id=processo.id,
                concluido=False
            )

            db.session.add(evento_prazo)

    elif evento_prazo:
        db.session.delete(evento_prazo)


# ==========================
# LISTAR PROCESSOS
# ==========================
@processo_bp.route("/processos")
@login_required
def listar_processos():
    termo = request.args.get("q", "")
    situacao = request.args.get("situacao", "")

    processos = Processo.query

    if termo:
        processos = processos.filter(
            (Processo.numero.contains(termo)) |
            (Processo.area.contains(termo)) |
            (Processo.situacao.contains(termo)) |
            (Processo.advogado.contains(termo))
        )

    if situacao:
        processos = processos.filter(
            Processo.situacao == situacao
        )

    pagina = request.args.get("pagina", 1, type=int)

    processos = processos.paginate(
        page=pagina,
        per_page=10,
        error_out=False
    )

    total = Processo.query.count()

    em_andamento = Processo.query.filter_by(
        situacao="Em andamento"
    ).count()

    audiencia = Processo.query.filter_by(
        situacao="Aguardando audiência"
    ).count()

    documentos = Processo.query.filter_by(
        situacao="Aguardando documentos"
    ).count()

    arquivados = Processo.query.filter_by(
        situacao="Arquivado"
    ).count()

    suspensos = Processo.query.filter_by(
        situacao="Suspenso"
    ).count()

    return render_template(
        "processos/listar.html",
        processos=processos,
        termo=termo,
        situacao=situacao,
        total=total,
        em_andamento=em_andamento,
        audiencia=audiencia,
        documentos=documentos,
        arquivados=arquivados,
        suspensos=suspensos,
        hoje=date.today()
    )


# ==========================
# NOVO PROCESSO
# ==========================
@processo_bp.route(
    "/clientes/<int:cliente_id>/processos/novo",
    methods=["GET", "POST"]
)
@login_required
def novo_processo(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == "POST":
        processo = Processo(
            numero=request.form["numero"],
            area=request.form["area"],
            tribunal=request.form["tribunal"],
            comarca=request.form["comarca"],
            vara=request.form["vara"],
            situacao=request.form["situacao"],
            advogado=request.form["advogado"],
            observacoes=request.form["observacoes"],
            cliente_id=cliente.id
        )

        data_entrada = request.form["data_entrada"]
        proximo_prazo = request.form["proximo_prazo"]

        if data_entrada:
            processo.data_entrada = datetime.strptime(
                data_entrada,
                "%Y-%m-%d"
            ).date()

        if proximo_prazo:
            processo.proximo_prazo = datetime.strptime(
                proximo_prazo,
                "%Y-%m-%d"
            ).date()

        db.session.add(processo)

        # Gera o ID antes de criar o evento da agenda.
        db.session.flush()

        sincronizar_prazo_agenda(processo)

        db.session.commit()

        flash(
            "⚖ Processo cadastrado com sucesso!",
            "success"
        )

        if processo.proximo_prazo:
            flash(
                "📅 O prazo também foi adicionado à Agenda.",
                "info"
            )

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    return render_template(
        "processos/novo.html",
        cliente=cliente
    )


# ==========================
# DETALHES DO PROCESSO
# ==========================
@processo_bp.route("/processos/<int:id>")
@login_required
def detalhes_processo(id):
    processo = Processo.query.get_or_404(id)
    cliente = processo.cliente

    return render_template(
        "processos/detalhes.html",
        processo=processo,
        cliente=cliente
    )


# ==========================
# EDITAR PROCESSO
# ==========================
@processo_bp.route(
    "/processos/<int:id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar_processo(id):
    processo = Processo.query.get_or_404(id)
    cliente = processo.cliente

    if request.method == "POST":
        prazo_anterior = processo.proximo_prazo

        processo.numero = request.form["numero"]
        processo.area = request.form["area"]
        processo.tribunal = request.form["tribunal"]
        processo.comarca = request.form["comarca"]
        processo.vara = request.form["vara"]
        processo.situacao = request.form["situacao"]
        processo.advogado = request.form["advogado"]
        processo.observacoes = request.form["observacoes"]

        data_entrada = request.form["data_entrada"]
        proximo_prazo = request.form["proximo_prazo"]

        processo.data_entrada = (
            datetime.strptime(
                data_entrada,
                "%Y-%m-%d"
            ).date()
            if data_entrada
            else None
        )

        processo.proximo_prazo = (
            datetime.strptime(
                proximo_prazo,
                "%Y-%m-%d"
            ).date()
            if proximo_prazo
            else None
        )

        sincronizar_prazo_agenda(processo)

        db.session.commit()

        flash(
            "✏️ Processo atualizado com sucesso!",
            "warning"
        )

        if processo.proximo_prazo != prazo_anterior:
            if processo.proximo_prazo:
                flash(
                    "📅 O prazo da Agenda foi atualizado.",
                    "info"
                )
            else:
                flash(
                    "📅 O prazo foi removido da Agenda.",
                    "info"
                )

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    return render_template(
        "processos/editar.html",
        processo=processo,
        cliente=cliente
    )


# ==========================
# EXCLUIR PROCESSO
# ==========================
@processo_bp.route(
    "/processos/<int:id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_processo(id):
    processo = Processo.query.get_or_404(id)
    cliente_id = processo.cliente_id

    eventos_vinculados = EventoAgenda.query.filter_by(
        processo_id=processo.id
    ).all()

    for evento in eventos_vinculados:
        db.session.delete(evento)

    db.session.delete(processo)
    db.session.commit()

    flash(
        "🗑️ Processo e eventos vinculados removidos com sucesso!",
        "danger"
    )

    return redirect(
        url_for(
            "clientes.detalhes_cliente",
            id=cliente_id
        )
    )