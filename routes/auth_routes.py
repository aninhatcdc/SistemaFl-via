from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from models import db
from models.usuario import Usuario


auth_bp = Blueprint(
    "auth",
    __name__
)


# =====================================
# CRIAR PRIMEIRO ADMINISTRADOR
# =====================================
def garantir_primeiro_administrador():
    if Usuario.query.count() > 0:
        return

    administrador = Usuario(
        nome="Administrador",
        email="admin@escritorio.com",
        perfil=Usuario.PERFIL_ADMIN,
        ativo=True
    )

    administrador.definir_senha(
        "admin123"
    )

    db.session.add(
        administrador
    )

    db.session.commit()


# =====================================
# LOGIN
# =====================================
@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    garantir_primeiro_administrador()

    if current_user.is_authenticated:
        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    if request.method == "POST":
        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        usuario = (
            Usuario.query
            .filter_by(
                email=email
            )
            .first()
        )

        if not usuario:
            flash(
                "E-mail ou senha inválidos.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        if not usuario.ativo:
            flash(
                "Este usuário está desativado.",
                "warning"
            )

            return render_template(
                "auth/login.html"
            )

        if not usuario.verificar_senha(
            senha
        ):
            flash(
                "E-mail ou senha inválidos.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        usuario.ultimo_acesso = datetime.utcnow()

        db.session.commit()

        login_user(
            usuario,
            remember=True
        )

        proxima_pagina = request.args.get(
            "next"
        )

        if proxima_pagina:
            return redirect(
                proxima_pagina
            )

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    return render_template(
        "auth/login.html"
    )


# =====================================
# LOGOUT
# =====================================
@auth_bp.route(
    "/logout",
    methods=["POST"]
)
@login_required
def logout():
    logout_user()

    flash(
        "Você saiu do sistema.",
        "info"
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )