from flask import (
    Blueprint,
    abort,
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
from models.usuario import Usuario


usuario_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def exigir_administrador():
    """
    Permite acesso ao módulo de usuários
    somente para administradores.
    """
    if not current_user.is_authenticated:
        abort(401)

    if not current_user.pode_gerenciar_usuarios:
        abort(403)


def quantidade_administradores_ativos():
    """
    Retorna a quantidade de administradores
    ativos cadastrados no sistema.
    """
    return (
        Usuario.query
        .filter_by(
            perfil=Usuario.PERFIL_ADMIN,
            ativo=True
        )
        .count()
    )


def formulario_usuario():
    """
    Recupera e normaliza os dados enviados
    pelos formulários de usuário.
    """
    return {
        "nome": request.form.get(
            "nome",
            ""
        ).strip(),

        "email": request.form.get(
            "email",
            ""
        ).strip().lower(),

        "telefone": request.form.get(
            "telefone",
            ""
        ).strip(),

        "cargo": request.form.get(
            "cargo",
            ""
        ).strip(),

        "perfil": request.form.get(
            "perfil",
            Usuario.PERFIL_FUNCIONARIO
        ).strip()
    }


# =====================================
# LISTAR USUÁRIOS
# =====================================
@usuario_bp.route("/")
@login_required
def listar_usuarios():
    exigir_administrador()

    termo = request.args.get(
        "q",
        ""
    ).strip()

    consulta = Usuario.query

    if termo:
        termo_like = f"%{termo}%"

        consulta = consulta.filter(
            db.or_(
                Usuario.nome.ilike(termo_like),
                Usuario.email.ilike(termo_like),
                Usuario.telefone.ilike(termo_like),
                Usuario.cargo.ilike(termo_like),
                Usuario.perfil.ilike(termo_like)
            )
        )

    usuarios = (
        consulta
        .order_by(
            Usuario.ativo.desc(),
            Usuario.nome.asc()
        )
        .all()
    )

    return render_template(
        "usuarios/listar.html",
        usuarios=usuarios,
        termo=termo
    )


# =====================================
# NOVO USUÁRIO
# =====================================
@usuario_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@login_required
def novo_usuario():
    exigir_administrador()

    if request.method == "POST":
        dados = formulario_usuario()

        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        if not dados["nome"]:
            flash(
                "Informe o nome do usuário.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if not dados["email"]:
            flash(
                "Informe o e-mail do usuário.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if "@" not in dados["email"]:
            flash(
                "Informe um endereço de e-mail válido.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if dados["perfil"] not in Usuario.PERFIS:
            flash(
                "Selecione um perfil válido.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if len(senha) < 6:
            flash(
                "A senha deve ter pelo menos 6 caracteres.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if senha != confirmar_senha:
            flash(
                "As senhas não coincidem.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        usuario_existente = (
            Usuario.query
            .filter(
                db.func.lower(
                    Usuario.email
                ) == dados["email"]
            )
            .first()
        )

        if usuario_existente:
            flash(
                "Já existe um usuário com este e-mail.",
                "warning"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            telefone=dados["telefone"],
            cargo=dados["cargo"],
            perfil=dados["perfil"],
            ativo=True
        )

        usuario.definir_senha(
            senha
        )

        try:
            db.session.add(
                usuario
            )

            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível cadastrar o usuário. "
                "Verifique os dados e tente novamente.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html",
                perfis=Usuario.PERFIS,
                dados=dados
            )

        flash(
            "✅ Usuário cadastrado com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    return render_template(
        "usuarios/novo.html",
        perfis=Usuario.PERFIS,
        dados={}
    )


# =====================================
# EDITAR USUÁRIO
# =====================================
@usuario_bp.route(
    "/<int:id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar_usuario(id):
    exigir_administrador()

    usuario = Usuario.query.get_or_404(
        id
    )

    if request.method == "POST":
        dados = formulario_usuario()

        if not dados["nome"]:
            flash(
                "Informe o nome do usuário.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if not dados["email"]:
            flash(
                "Informe o e-mail do usuário.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if "@" not in dados["email"]:
            flash(
                "Informe um endereço de e-mail válido.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        if dados["perfil"] not in Usuario.PERFIS:
            flash(
                "Selecione um perfil válido.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        email_em_uso = (
            Usuario.query
            .filter(
                db.func.lower(
                    Usuario.email
                ) == dados["email"],
                Usuario.id != usuario.id
            )
            .first()
        )

        if email_em_uso:
            flash(
                "Este e-mail já está sendo utilizado.",
                "warning"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        alterando_admin_para_outro_perfil = (
            usuario.perfil == Usuario.PERFIL_ADMIN
            and dados["perfil"] != Usuario.PERFIL_ADMIN
        )

        if usuario.id == current_user.id:
            if dados["perfil"] != Usuario.PERFIL_ADMIN:
                flash(
                    "Você não pode remover o perfil de "
                    "administrador do próprio usuário.",
                    "warning"
                )

                return render_template(
                    "usuarios/editar.html",
                    usuario=usuario,
                    perfis=Usuario.PERFIS,
                    dados=dados
                )

        if (
            alterando_admin_para_outro_perfil
            and usuario.ativo
            and quantidade_administradores_ativos() <= 1
        ):
            flash(
                "Não é possível alterar o perfil do último "
                "administrador ativo do sistema.",
                "warning"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        usuario.nome = dados["nome"]
        usuario.email = dados["email"]
        usuario.telefone = dados["telefone"]
        usuario.cargo = dados["cargo"]
        usuario.perfil = dados["perfil"]

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível atualizar o usuário. "
                "Verifique os dados e tente novamente.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=Usuario.PERFIS,
                dados=dados
            )

        flash(
            "✅ Usuário atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    return render_template(
        "usuarios/editar.html",
        usuario=usuario,
        perfis=Usuario.PERFIS,
        dados={}
    )


# =====================================
# ATIVAR OU DESATIVAR
# =====================================
@usuario_bp.route(
    "/<int:id>/status",
    methods=["POST"]
)
@login_required
def alterar_status_usuario(id):
    exigir_administrador()

    usuario = Usuario.query.get_or_404(
        id
    )

    if usuario.id == current_user.id:
        flash(
            "Você não pode desativar o próprio usuário.",
            "warning"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    if (
        usuario.ativo
        and usuario.perfil == Usuario.PERFIL_ADMIN
        and quantidade_administradores_ativos() <= 1
    ):
        flash(
            "Não é possível desativar o último "
            "administrador ativo do sistema.",
            "warning"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    usuario.ativo = not usuario.ativo

    try:
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível alterar o status do usuário.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    if usuario.ativo:
        flash(
            "✅ Usuário ativado com sucesso!",
            "success"
        )

    else:
        flash(
            "⛔ Usuário desativado com sucesso!",
            "warning"
        )

    return redirect(
        url_for(
            "usuarios.listar_usuarios"
        )
    )


# =====================================
# REDEFINIR SENHA
# =====================================
@usuario_bp.route(
    "/<int:id>/senha",
    methods=["POST"]
)
@login_required
def redefinir_senha(id):
    exigir_administrador()

    usuario = Usuario.query.get_or_404(
        id
    )

    nova_senha = request.form.get(
        "nova_senha",
        ""
    )

    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    )

    if len(nova_senha) < 6:
        flash(
            "A nova senha deve ter pelo menos 6 caracteres.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.editar_usuario",
                id=usuario.id
            )
        )

    if nova_senha != confirmar_senha:
        flash(
            "As senhas não coincidem.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.editar_usuario",
                id=usuario.id
            )
        )

    usuario.definir_senha(
        nova_senha
    )

    try:
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível redefinir a senha.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.editar_usuario",
                id=usuario.id
            )
        )

    flash(
        "🔐 Senha redefinida com sucesso!",
        "success"
    )

    return redirect(
        url_for(
            "usuarios.editar_usuario",
            id=usuario.id
        )
    )

    # =====================================
# EXCLUIR USUÁRIO
# =====================================
@usuario_bp.route(
    "/<int:id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_usuario(id):
    exigir_administrador()

    usuario = Usuario.query.get_or_404(id)

    # Não pode excluir o próprio usuário
    if usuario.id == current_user.id:
        flash(
            "Você não pode excluir o próprio usuário.",
            "warning"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    # Só permite excluir usuários inativos
    if usuario.ativo:
        flash(
            "Desative o usuário antes de excluí-lo.",
            "warning"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    # Segurança extra
    if (
        usuario.perfil == Usuario.PERFIL_ADMIN
        and quantidade_administradores_ativos() == 0
    ):
        flash(
            "Não é possível excluir o último administrador do sistema.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    try:

        db.session.delete(usuario)

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        flash(
            "Não foi possível excluir o usuário.",
            "danger"
        )

        return redirect(
            url_for(
                "usuarios.listar_usuarios"
            )
        )

    flash(
        "🗑️ Usuário excluído com sucesso!",
        "success"
    )

    return redirect(
        url_for(
            "usuarios.listar_usuarios"
        )
    )