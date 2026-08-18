import os
from flask_login import login_required

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from werkzeug.utils import secure_filename

from models import db
from models.cliente import Cliente
from models.documento import Documento
from utils.storage import storage_path, caminho_storage_relativo


documento_bp = Blueprint("documentos", __name__)



# =====================================
# LISTAR ARQUIVOS
# =====================================
@documento_bp.route("/documentos")
@login_required
def listar_documentos():
    termo = request.args.get("q", "")

    documentos = Documento.query

    if termo:
        documentos = documentos.filter(
            (Documento.nome_arquivo.contains(termo)) |
            (Documento.descricao.contains(termo))
        )

    documentos = documentos.order_by(
        Documento.criado_em.desc()
    ).all()

    total = Documento.query.count()

    return render_template(
        "documentos/listar.html",
        documentos=documentos,
        termo=termo,
        total=total
    )


# =====================================
# NOVO ARQUIVO
# =====================================
@documento_bp.route(
    "/clientes/<int:cliente_id>/documentos/novo",
    methods=["GET", "POST"]
)
@login_required
def novo_documento(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == "POST":
        arquivo = request.files.get("arquivo")

        if not arquivo or arquivo.filename == "":
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        nome_seguro = secure_filename(arquivo.filename)

        if not nome_seguro:
            flash("O nome do arquivo é inválido.", "danger")
            return redirect(request.url)

        caminho = storage_path(
            "uploads",
            "documentos",
            f"cliente_{cliente.id}",
            nome_seguro
        )

        arquivo.save(str(caminho))

        documento = Documento(
            nome_arquivo=nome_seguro,
            caminho_arquivo=os.path.relpath(
                caminho,
                storage_path()
            ).replace("\\", "/"),
            tipo=None,
            descricao=request.form.get("descricao", ""),
            cliente_id=cliente.id
        )

        db.session.add(documento)
        db.session.commit()

        flash("📂 Arquivo enviado com sucesso!", "success")

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    return render_template(
        "documentos/novo.html",
        cliente=cliente
    )


# =====================================
# DETALHES DO ARQUIVO
# =====================================
@documento_bp.route("/documentos/<int:id>")
@login_required
def detalhes_documento(id):
    documento = Documento.query.get_or_404(id)

    return render_template(
        "documentos/detalhes.html",
        documento=documento
    )


# =====================================
# VISUALIZAR ARQUIVO
# =====================================
@documento_bp.route("/documentos/<int:id>/visualizar")
@login_required
def visualizar_documento(id):
    documento = Documento.query.get_or_404(id)

    if not caminho_storage_relativo(documento.caminho_arquivo).is_file():
        flash("Arquivo não encontrado no servidor.", "danger")

        return redirect(
            url_for("documentos.listar_documentos")
        )

    return send_file(
        str(
            caminho_storage_relativo(
                documento.caminho_arquivo
            )
        )
    )


# =====================================
# DOWNLOAD DO ARQUIVO
# =====================================
@documento_bp.route("/documentos/<int:id>/download")
@login_required
def download_documento(id):
    documento = Documento.query.get_or_404(id)

    if not caminho_storage_relativo(documento.caminho_arquivo).is_file():
        flash("Arquivo não encontrado no servidor.", "danger")

        return redirect(
            url_for("documentos.listar_documentos")
        )

    return send_file(
        str(
            caminho_storage_relativo(
                documento.caminho_arquivo
            )
        ),
        as_attachment=True,
        download_name=documento.nome_arquivo
    )


# =====================================
# EXCLUIR ARQUIVO
# =====================================
@documento_bp.route(
    "/documentos/<int:id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_documento(id):
    documento = Documento.query.get_or_404(id)
    cliente_id = documento.cliente_id

    if caminho_storage_relativo(documento.caminho_arquivo).is_file():
        caminho_storage_relativo(documento.caminho_arquivo).unlink()

    db.session.delete(documento)
    db.session.commit()

    flash("🗑 Arquivo removido com sucesso!", "danger")

    return redirect(
        url_for(
            "clientes.detalhes_cliente",
            id=cliente_id
        )
    )