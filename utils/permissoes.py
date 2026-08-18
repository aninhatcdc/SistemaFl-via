from functools import wraps

from flask import abort
from flask_login import (
    current_user,
    login_required
)

from models.usuario import Usuario


# =====================================
# DECORADOR GENÉRICO DE PERFIS
# =====================================
def perfis_required(*perfis_permitidos):
    """
    Permite acesso somente aos usuários
    que possuem um dos perfis informados.

    Exemplo:

    @perfis_required(
        Usuario.PERFIL_ADMIN,
        Usuario.PERFIL_FINANCEIRO
    )
    """

    def decorador(funcao):

        @wraps(funcao)
        @login_required
        def funcao_protegida(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            if not current_user.ativo:
                abort(403)

            if current_user.perfil not in perfis_permitidos:
                abort(403)

            return funcao(
                *args,
                **kwargs
            )

        return funcao_protegida

    return decorador


# =====================================
# SOMENTE ADMINISTRADOR
# =====================================
def admin_required(funcao):
    """
    Permite acesso somente para usuários
    com perfil de administrador.
    """

    return perfis_required(
        Usuario.PERFIL_ADMIN
    )(funcao)


# =====================================
# ACESSO AO FINANCEIRO
# =====================================
def financeiro_required(funcao):
    """
    Permite acesso somente para usuários
    administradores ou financeiros.
    """

    return perfis_required(
        Usuario.PERFIL_ADMIN,
        Usuario.PERFIL_FINANCEIRO
    )(funcao)


# =====================================
# QUALQUER USUÁRIO ATIVO
# =====================================
def usuario_ativo_required(funcao):
    """
    Permite acesso para qualquer usuário
    autenticado e ativo.
    """

    @wraps(funcao)
    @login_required
    def funcao_protegida(*args, **kwargs):

        if not current_user.is_authenticated:
            abort(401)

        if not current_user.ativo:
            abort(403)

        return funcao(
            *args,
            **kwargs
        )

    return funcao_protegida