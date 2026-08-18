from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from models import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    # ==========================
    # PERFIS
    # ==========================
    PERFIL_ADMIN = "ADMIN"
    PERFIL_FINANCEIRO = "FIN"
    PERFIL_FUNCIONARIO = "FUNC"

    PERFIS = {
        PERFIL_ADMIN: "Administrador",
        PERFIL_FINANCEIRO: "Financeiro",
        PERFIL_FUNCIONARIO: "Funcionário"
    }

    # ==========================
    # IDENTIFICAÇÃO
    # ==========================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # DADOS PESSOAIS
    # ==========================
    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    telefone = db.Column(
        db.String(20)
    )

    cargo = db.Column(
        db.String(100)
    )

    foto = db.Column(
        db.String(255)
    )

    # ==========================
    # ACESSO
    # ==========================
    senha_hash = db.Column(
        db.String(255),
        nullable=False
    )

    perfil = db.Column(
        db.String(30),
        nullable=False,
        default=PERFIL_FUNCIONARIO
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # ==========================
    # CONTROLE
    # ==========================
    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    ultimo_acesso = db.Column(
        db.DateTime
    )

    # ==========================
    # SENHA
    # ==========================
    def definir_senha(self, senha):
        if not senha:
            raise ValueError(
                "A senha não pode ficar vazia."
            )

        self.senha_hash = generate_password_hash(
            senha
        )

    def verificar_senha(self, senha):
        if not senha or not self.senha_hash:
            return False

        return check_password_hash(
            self.senha_hash,
            senha
        )

    # ==========================
    # FLASK-LOGIN
    # ==========================
    @property
    def is_active(self):
        """
        Informa ao Flask-Login se o usuário
        está autorizado a utilizar o sistema.
        """
        return bool(self.ativo)

    # ==========================
    # PROPRIEDADES
    # ==========================
    @property
    def primeiro_nome(self):
        if not self.nome:
            return ""

        return self.nome.strip().split()[0]

    @property
    def perfil_nome(self):
        return self.PERFIS.get(
            self.perfil,
            "Perfil não identificado"
        )

    @property
    def pode_acessar_financeiro(self):
        return self.perfil in {
            self.PERFIL_ADMIN,
            self.PERFIL_FINANCEIRO
        }

    @property
    def pode_gerenciar_usuarios(self):
        return self.perfil == self.PERFIL_ADMIN

    @property
    def iniciais(self):
        if not self.nome:
            return "U"

        partes = self.nome.strip().split()

        if len(partes) == 1:
            return partes[0][0].upper()

        return (
            partes[0][0]
            + partes[-1][0]
        ).upper()

    # ==========================
    # REPRESENTAÇÃO
    # ==========================
    def __repr__(self):
        return (
            f"<Usuario "
            f"id={self.id} "
            f"email='{self.email}' "
            f"perfil='{self.perfil}'>"
        )