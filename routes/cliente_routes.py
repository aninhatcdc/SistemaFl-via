
from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from sqlalchemy.exc import SQLAlchemyError

from models import db
from models.cliente import Cliente


cliente_bp = Blueprint(
    "clientes",
    __name__
)


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def obter_dados_formulario_cliente():
    """
    Recupera e organiza os dados enviados
    pelos formulários de cliente.
    """

    return {
        "nome": request.form.get(
            "nome",
            ""
        ).strip(),

        "cpf": request.form.get(
            "cpf",
            ""
        ).strip(),

        "rg": request.form.get(
            "rg",
            ""
        ).strip(),

        "telefone": request.form.get(
            "telefone",
            ""
        ).strip(),

        "whatsapp": request.form.get(
            "whatsapp",
            ""
        ).strip(),

        "email": request.form.get(
            "email",
            ""
        ).strip().lower(),

        "profissao": request.form.get(
            "profissao",
            ""
        ).strip(),

        "estado_civil": request.form.get(
            "estado_civil",
            ""
        ).strip(),

        "cep": request.form.get(
            "cep",
            ""
        ).strip(),

        "rua": request.form.get(
            "rua",
            ""
        ).strip(),

        "numero": request.form.get(
            "numero",
            ""
        ).strip(),

        "complemento": request.form.get(
            "complemento",
            ""
        ).strip(),

        "bairro": request.form.get(
            "bairro",
            ""
        ).strip(),

        "cidade": request.form.get(
            "cidade",
            ""
        ).strip(),

        "estado": request.form.get(
            "estado",
            ""
        ).strip().upper(),

        "area_juridica": request.form.get(
            "area_juridica",
            ""
        ).strip(),

        "origem_cliente": request.form.get(
            "origem_cliente",
            ""
        ).strip(),

        "responsavel": request.form.get(
            "responsavel",
            ""
        ).strip(),

        "observacoes": request.form.get(
            "observacoes",
            ""
        ).strip(),

        "data_nascimento": request.form.get(
            "data_nascimento",
            ""
        ).strip()
    }


def converter_data_nascimento(data_texto):
    """
    Converte a data recebida do formulário
    para um objeto date.
    """

    if not data_texto:
        return None

    return datetime.strptime(
        data_texto,
        "%Y-%m-%d"
    ).date()


def email_valido(email):
    if not email:
        return True

    return (
        "@" in email
        and "." in email.split("@")[-1]
    )


# =====================================
# LISTAR CLIENTES
# =====================================
@cliente_bp.route(
    "/clientes"
)
@login_required
def listar_clientes():
    termo = request.args.get(
        "q",
        ""
    ).strip()

    pagina = request.args.get(
        "pagina",
        1,
        type=int
    )

    consulta = Cliente.query

    if termo:
        consulta = consulta.filter(
            db.or_(
                Cliente.nome.contains(
                    termo
                ),
                Cliente.cpf.contains(
                    termo
                ),
                Cliente.whatsapp.contains(
                    termo
                ),
                Cliente.email.contains(
                    termo
                ),
                Cliente.area_juridica.contains(
                    termo
                ),
                Cliente.responsavel.contains(
                    termo
                )
            )
        )

    clientes = (
        consulta
        .order_by(
            Cliente.ativo.desc(),
            Cliente.nome.asc()
        )
        .paginate(
            page=pagina,
            per_page=10,
            error_out=False
        )
    )

    return render_template(
        "clientes/listar.html",
        clientes=clientes,
        termo=termo
    )


# =====================================
# NOVO CLIENTE
# =====================================
@cliente_bp.route(
    "/clientes/novo",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def novo_cliente():
    if request.method == "POST":
        dados = obter_dados_formulario_cliente()

        if not dados["nome"]:
            flash(
                "Informe o nome completo do cliente.",
                "danger"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        if not dados["cpf"]:
            flash(
                "Informe o CPF do cliente.",
                "danger"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        if not email_valido(
            dados["email"]
        ):
            flash(
                "Informe um endereço de e-mail válido.",
                "danger"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        cliente_existente = (
            Cliente.query
            .filter_by(
                cpf=dados["cpf"]
            )
            .first()
        )

        if cliente_existente:
            flash(
                "Já existe um cliente cadastrado com este CPF.",
                "warning"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        try:
            data_nascimento = converter_data_nascimento(
                dados["data_nascimento"]
            )

        except ValueError:
            flash(
                "Informe uma data de nascimento válida.",
                "danger"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        cliente = Cliente(
            nome=dados["nome"],
            cpf=dados["cpf"],
            rg=dados["rg"],
            data_nascimento=data_nascimento,
            telefone=dados["telefone"],
            whatsapp=dados["whatsapp"],
            email=dados["email"],
            profissao=dados["profissao"],
            estado_civil=dados["estado_civil"],
            cep=dados["cep"],
            rua=dados["rua"],
            numero=dados["numero"],
            complemento=dados["complemento"],
            bairro=dados["bairro"],
            cidade=dados["cidade"],
            estado=dados["estado"],
            area_juridica=dados["area_juridica"],
            origem_cliente=dados["origem_cliente"],
            responsavel=dados["responsavel"],
            observacoes=dados["observacoes"],
            ativo=True,

            # Auditoria
            criado_por_id=current_user.id,
            atualizado_por_id=current_user.id
        )

        try:
            db.session.add(
                cliente
            )

            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível cadastrar o cliente. "
                "Verifique os dados e tente novamente.",
                "danger"
            )

            return render_template(
                "clientes/novo.html",
                dados=dados
            )

        flash(
            "✅ Cliente cadastrado com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    return render_template(
        "clientes/novo.html",
        dados={}
    )


# =====================================
# DETALHES DO CLIENTE
# =====================================
@cliente_bp.route(
    "/clientes/<int:id>"
)
@login_required
def detalhes_cliente(id):
    cliente = Cliente.query.get_or_404(
        id
    )

    return render_template(
        "clientes/detalhes.html",
        cliente=cliente
    )


# =====================================
# EDITAR CLIENTE
# =====================================
@cliente_bp.route(
    "/clientes/<int:id>/editar",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(
        id
    )

    if request.method == "POST":
        dados = obter_dados_formulario_cliente()

        if not dados["nome"]:
            flash(
                "Informe o nome completo do cliente.",
                "danger"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        if not dados["cpf"]:
            flash(
                "Informe o CPF do cliente.",
                "danger"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        if not email_valido(
            dados["email"]
        ):
            flash(
                "Informe um endereço de e-mail válido.",
                "danger"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        cpf_em_uso = (
            Cliente.query
            .filter(
                Cliente.cpf == dados["cpf"],
                Cliente.id != cliente.id
            )
            .first()
        )

        if cpf_em_uso:
            flash(
                "Já existe outro cliente cadastrado com este CPF.",
                "warning"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        try:
            data_nascimento = converter_data_nascimento(
                dados["data_nascimento"]
            )

        except ValueError:
            flash(
                "Informe uma data de nascimento válida.",
                "danger"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        cliente.nome = dados["nome"]
        cliente.cpf = dados["cpf"]
        cliente.rg = dados["rg"]
        cliente.data_nascimento = data_nascimento
        cliente.telefone = dados["telefone"]
        cliente.whatsapp = dados["whatsapp"]
        cliente.email = dados["email"]
        cliente.profissao = dados["profissao"]
        cliente.estado_civil = dados["estado_civil"]
        cliente.cep = dados["cep"]
        cliente.rua = dados["rua"]
        cliente.numero = dados["numero"]
        cliente.complemento = dados["complemento"]
        cliente.bairro = dados["bairro"]
        cliente.cidade = dados["cidade"]
        cliente.estado = dados["estado"]
        cliente.area_juridica = dados["area_juridica"]
        cliente.origem_cliente = dados["origem_cliente"]
        cliente.responsavel = dados["responsavel"]
        cliente.observacoes = dados["observacoes"]

        # Auditoria
        cliente.atualizado_por_id = current_user.id
        cliente.atualizado_em = datetime.utcnow()

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível atualizar o cliente. "
                "Verifique os dados e tente novamente.",
                "danger"
            )

            return render_template(
                "clientes/editar.html",
                cliente=cliente,
                dados=dados
            )

        flash(
            "✏️ Cliente atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    return render_template(
        "clientes/editar.html",
        cliente=cliente,
        dados={}
    )


# =====================================
# EXCLUIR CLIENTE
# =====================================
@cliente_bp.route(
    "/clientes/<int:id>/excluir",
    methods=[
        "POST"
    ]
)
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(
        id
    )

    try:
        db.session.delete(
            cliente
        )

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível remover o cliente. "
            "Verifique se existem dados relacionados.",
            "danger"
        )

        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=cliente.id
            )
        )

    flash(
        "🗑️ Cliente removido com sucesso!",
        "success"
    )

    return redirect(
        url_for(
            "clientes.listar_clientes"
        )
    )
