import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from werkzeug.utils import secure_filename

from models import db
from models.cliente import Cliente
from models.configuracao import ConfiguracaoEscritorio
from models.documento_gerado import DocumentoGerado
from models.documento_modelo import DocumentoModelo
from models.processo import Processo

from utils.storage import storage_path, caminho_storage_relativo

from services.gerador_documentos_service import (
    gerar_documento_docx,
    montar_contexto_documento,
    nome_arquivo_seguro
)


gerador_documentos_bp = Blueprint(
    "gerador_documentos",
    __name__,
    url_prefix="/gerador-documentos"
)


EXTENSOES_PERMITIDAS = {
    ".docx"
}


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def caminho_absoluto(caminho):
    """
    Converte um caminho relativo do projeto
    em um caminho absoluto.
    """

    if not caminho:
        return ""

    if os.path.isabs(caminho):
        return caminho

    if str(caminho).replace("\\", "/").lstrip("/").startswith("uploads/"):
        return str(
            caminho_storage_relativo(caminho)
        )

    return os.path.join(
        current_app.root_path,
        caminho
    )


def extensao_permitida(nome_arquivo):
    extensao = os.path.splitext(
        nome_arquivo or ""
    )[1].lower()

    return extensao in EXTENSOES_PERMITIDAS


# =====================================
# LISTAGEM DOS MODELOS
# =====================================
@gerador_documentos_bp.route("/")
@login_required
def listar():
    termo = request.args.get(
        "q",
        ""
    ).strip()

    consulta = DocumentoModelo.query

    if termo:
        pesquisa = f"%{termo}%"

        consulta = consulta.filter(
            db.or_(
                DocumentoModelo.nome.ilike(
                    pesquisa
                ),
                DocumentoModelo.categoria.ilike(
                    pesquisa
                ),
                DocumentoModelo.area_juridica.ilike(
                    pesquisa
                )
            )
        )

    modelos = (
        consulta
        .order_by(
            DocumentoModelo.nome.asc()
        )
        .all()
    )

    return render_template(
        "gerador_documentos/listar.html",
        modelos=modelos,
        termo=termo
    )


# =====================================
# HISTÓRICO DE DOCUMENTOS GERADOS
# =====================================
@gerador_documentos_bp.route("/historico")
@login_required
def historico():
    termo = request.args.get(
        "q",
        ""
    ).strip()

    consulta = (
        DocumentoGerado.query
        .join(
            Cliente,
            DocumentoGerado.cliente_id
            == Cliente.id
        )
    )

    if termo:
        pesquisa = f"%{termo}%"

        consulta = consulta.filter(
            db.or_(
                DocumentoGerado.nome_documento.ilike(
                    pesquisa
                ),
                DocumentoGerado.nome_arquivo.ilike(
                    pesquisa
                ),
                Cliente.nome.ilike(
                    pesquisa
                ),
                Cliente.cpf.ilike(
                    pesquisa
                )
            )
        )

    documentos = (
        consulta
        .order_by(
            DocumentoGerado.gerado_em.desc()
        )
        .all()
    )

    return render_template(
        "gerador_documentos/historico.html",
        documentos=documentos,
        termo=termo
    )


# =====================================
# CADASTRAR NOVO MODELO
# =====================================
@gerador_documentos_bp.route(
    "/novo",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def novo():
    if request.method == "POST":
        nome = request.form.get(
            "nome",
            ""
        ).strip()

        categoria = request.form.get(
            "categoria",
            DocumentoModelo.CATEGORIA_OUTRO
        ).strip()

        area_juridica = request.form.get(
            "area_juridica",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        arquivo = request.files.get(
            "arquivo"
        )

        if not nome:
            flash(
                "Informe o nome do modelo.",
                "warning"
            )

            return render_template(
                "gerador_documentos/novo.html",
                categorias=DocumentoModelo.CATEGORIAS
            )

        if not arquivo or not arquivo.filename:
            flash(
                "Selecione um arquivo DOCX.",
                "warning"
            )

            return render_template(
                "gerador_documentos/novo.html",
                categorias=DocumentoModelo.CATEGORIAS
            )

        if not extensao_permitida(
            arquivo.filename
        ):
            flash(
                "O modelo precisa estar no formato DOCX.",
                "danger"
            )

            return render_template(
                "gerador_documentos/novo.html",
                categorias=DocumentoModelo.CATEGORIAS
            )

        nome_original = secure_filename(
            arquivo.filename
        )

        extensao = os.path.splitext(
            nome_original
        )[1].lower()

        nome_salvo = (
            f"{uuid.uuid4().hex}"
            f"{extensao}"
        )

        pasta_relativa = os.path.join(
            "uploads",
            "modelos_documentos"
        )

        pasta_absoluta = caminho_absoluto(
            pasta_relativa
        )

        os.makedirs(
            pasta_absoluta,
            exist_ok=True
        )

        caminho_relativo = os.path.join(
            pasta_relativa,
            nome_salvo
        )

        arquivo.save(
            caminho_absoluto(
                caminho_relativo
            )
        )

        modelo = DocumentoModelo(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            area_juridica=area_juridica,
            nome_arquivo_original=nome_original,
            nome_arquivo_salvo=nome_salvo,
            caminho_arquivo=caminho_relativo,
            tipo_arquivo=DocumentoModelo.TIPO_DOCX,
            ativo=True,
            exige_cliente=(
                request.form.get(
                    "exige_cliente"
                )
                == "on"
            ),
            exige_processo=(
                request.form.get(
                    "exige_processo"
                )
                == "on"
            ),
            exige_honorario=(
                request.form.get(
                    "exige_honorario"
                )
                == "on"
            ),
            observacoes=observacoes,
            criado_por_id=current_user.id,
            atualizado_por_id=current_user.id
        )

        try:
            db.session.add(
                modelo
            )

            db.session.commit()

            flash(
                "Modelo cadastrado com sucesso.",
                "success"
            )

            return redirect(
                url_for(
                    "gerador_documentos.listar"
                )
            )

        except Exception as erro:
            db.session.rollback()

            caminho_arquivo = caminho_absoluto(
                caminho_relativo
            )

            if os.path.isfile(
                caminho_arquivo
            ):
                os.remove(
                    caminho_arquivo
                )

            flash(
                "Não foi possível cadastrar o modelo.",
                "danger"
            )

            current_app.logger.exception(
                erro
            )

    return render_template(
        "gerador_documentos/novo.html",
        categorias=DocumentoModelo.CATEGORIAS
    )


# =====================================
# SELECIONAR CLIENTE
# =====================================
@gerador_documentos_bp.route(
    "/<int:modelo_id>/cliente"
)
@login_required
def selecionar_cliente(
    modelo_id
):
    modelo = DocumentoModelo.query.get_or_404(
        modelo_id
    )

    if not modelo.ativo:
        flash(
            "Esse modelo está desativado.",
            "warning"
        )

        return redirect(
            url_for(
                "gerador_documentos.listar"
            )
        )

    clientes = (
        Cliente.query
        .filter_by(
            ativo=True
        )
        .order_by(
            Cliente.nome.asc()
        )
        .all()
    )

    return render_template(
        "gerador_documentos/selecionar_cliente.html",
        modelo=modelo,
        clientes=clientes
    )


# =====================================
# PREPARAR GERAÇÃO
# =====================================
@gerador_documentos_bp.route(
    "/<int:modelo_id>/cliente/<int:cliente_id>",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def preparar_documento(
    modelo_id,
    cliente_id
):
    modelo = DocumentoModelo.query.get_or_404(
        modelo_id
    )

    cliente = Cliente.query.get_or_404(
        cliente_id
    )

    processos = (
        Processo.query
        .filter_by(
            cliente_id=cliente.id
        )
        .order_by(
            Processo.criado_em.desc()
        )
        .all()
    )

    if request.method == "POST":
        processo = None

        processo_id = request.form.get(
            "processo_id",
            type=int
        )

        if processo_id:
            processo = Processo.query.filter_by(
                id=processo_id,
                cliente_id=cliente.id
            ).first()

            if not processo:
                flash(
                    "O processo selecionado não pertence "
                    "ao cliente informado.",
                    "danger"
                )

                return redirect(
                    request.url
                )

        if modelo.exige_processo and not processo:
            flash(
                "Selecione um processo para gerar "
                "este documento.",
                "warning"
            )

            return redirect(
                request.url
            )

        observacoes = request.form.get(
            "observacoes",
            ""
        ).strip()

        configuracao = (
            ConfiguracaoEscritorio.query
            .order_by(
                ConfiguracaoEscritorio.id.asc()
            )
            .first()
        )

        contexto = montar_contexto_documento(
            cliente=cliente,
            processo=processo,
            usuario=current_user,
            configuracao=configuracao
        )

        nome_base = nome_arquivo_seguro(
            f"{modelo.nome} - {cliente.nome}"
        )

        identificador = uuid.uuid4().hex[:8]

        nome_arquivo = (
            f"{nome_base} - {identificador}.docx"
        )

        pasta_relativa = os.path.join(
            "uploads",
            "documentos_gerados",
            f"cliente_{cliente.id}"
        )

        pasta_absoluta = caminho_absoluto(
            pasta_relativa
        )

        os.makedirs(
            pasta_absoluta,
            exist_ok=True
        )

        caminho_relativo = os.path.join(
            pasta_relativa,
            nome_arquivo
        )

        caminho_destino = caminho_absoluto(
            caminho_relativo
        )

        caminho_modelo = caminho_absoluto(
            modelo.caminho_arquivo
        )

        try:
            gerar_documento_docx(
                caminho_modelo=caminho_modelo,
                caminho_destino=caminho_destino,
                contexto=contexto
            )

            documento = DocumentoGerado(
                modelo_id=modelo.id,
                cliente_id=cliente.id,
                processo_id=(
                    processo.id
                    if processo
                    else None
                ),
                usuario_id=current_user.id,
                nome_documento=modelo.nome,
                nome_arquivo=nome_arquivo,
                caminho_arquivo=caminho_relativo,
                observacoes=observacoes
            )

            db.session.add(
                documento
            )

            db.session.commit()

            flash(
                "Documento gerado com sucesso.",
                "success"
            )

            return redirect(
                url_for(
                    "gerador_documentos.visualizar_documento",
                    documento_id=documento.id
                )
            )

        except Exception as erro:
            db.session.rollback()

            if os.path.isfile(
                caminho_destino
            ):
                os.remove(
                    caminho_destino
                )

            current_app.logger.exception(
                erro
            )

            flash(
                "Não foi possível gerar o documento. "
                "Verifique o modelo e as variáveis.",
                "danger"
            )

    return render_template(
        "gerador_documentos/preparar.html",
        modelo=modelo,
        cliente=cliente,
        processos=processos
    )


# =====================================
# VISUALIZAR REGISTRO
# =====================================
@gerador_documentos_bp.route(
    "/documento/<int:documento_id>"
)
@login_required
def visualizar_documento(
    documento_id
):
    documento = DocumentoGerado.query.get_or_404(
        documento_id
    )

    return render_template(
        "gerador_documentos/visualizar.html",
        documento=documento
    )


# =====================================
# BAIXAR DOCUMENTO
# =====================================
@gerador_documentos_bp.route(
    "/documento/<int:documento_id>/baixar"
)
@login_required
def baixar_documento(
    documento_id
):
    documento = DocumentoGerado.query.get_or_404(
        documento_id
    )

    caminho = caminho_absoluto(
        documento.caminho_arquivo
    )

    if not os.path.isfile(
        caminho
    ):
        flash(
            "O arquivo não foi encontrado.",
            "danger"
        )

        return redirect(
            url_for(
                "gerador_documentos.visualizar_documento",
                documento_id=documento.id
            )
        )

    return send_file(
        caminho,
        as_attachment=True,
        download_name=documento.nome_arquivo
    )