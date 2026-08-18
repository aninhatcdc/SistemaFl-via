from flask import (
    Blueprint,
    render_template
)

from flask_login import login_required

from services.notificacoes import (
    obter_resumo_notificacoes
)


notificacao_bp = Blueprint(
    "notificacoes",
    __name__,
    url_prefix="/notificacoes"
)


# =====================================
# CENTRAL DE NOTIFICAÇÕES
# =====================================
@notificacao_bp.route("/")
@login_required
def listar_notificacoes():
    resumo = obter_resumo_notificacoes()

    return render_template(
        "notificacoes/listar.html",
        notificacoes=resumo["notificacoes"],
        total_notificacoes=resumo["total"],
        total_alta=resumo["alta"],
        total_media=resumo["media"],
        total_baixa=resumo["baixa"]
    )