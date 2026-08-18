from datetime import datetime

from . import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    # =====================================
    # IDENTIFICAÇÃO
    # =====================================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================
    # DADOS PESSOAIS
    # =====================================
    nome = db.Column(
        db.String(150),
        nullable=False
    )

    cpf = db.Column(
        db.String(14),
        unique=True,
        nullable=False
    )

    rg = db.Column(
        db.String(20)
    )

    data_nascimento = db.Column(
        db.Date
    )

    estado_civil = db.Column(
        db.String(30)
    )

    profissao = db.Column(
        db.String(100)
    )

    # =====================================
    # CONTATO
    # =====================================
    telefone = db.Column(
        db.String(20)
    )

    whatsapp = db.Column(
        db.String(20)
    )

    email = db.Column(
        db.String(120)
    )

    # =====================================
    # ENDEREÇO
    # =====================================
    cep = db.Column(
        db.String(10)
    )

    rua = db.Column(
        db.String(150)
    )

    numero = db.Column(
        db.String(10)
    )

    complemento = db.Column(
        db.String(100)
    )

    bairro = db.Column(
        db.String(100)
    )

    cidade = db.Column(
        db.String(100)
    )

    estado = db.Column(
        db.String(2)
    )

    # =====================================
    # DADOS JURÍDICOS
    # =====================================
    area_juridica = db.Column(
        db.String(50)
    )

    observacoes = db.Column(
        db.Text
    )

    origem_cliente = db.Column(
        db.String(50)
    )

    responsavel = db.Column(
        db.String(100)
    )

    # =====================================
    # STATUS
    # =====================================
    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # =====================================
    # AUDITORIA
    # =====================================
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

    criado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    atualizado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    criado_por = db.relationship(
        "Usuario",
        foreign_keys=[criado_por_id],
        backref=db.backref(
            "clientes_criados",
            lazy=True
        )
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "clientes_atualizados",
            lazy=True
        )
    )

    # =====================================
    # RELACIONAMENTOS
    # =====================================
    processos = db.relationship(
        "Processo",
        backref="cliente",
        lazy=True,
        cascade="all, delete-orphan"
    )

    documentos = db.relationship(
        "Documento",
        backref="cliente",
        lazy=True,
        cascade="all, delete-orphan"
    )

    atendimentos = db.relationship(
        "Atendimento",
        back_populates="cliente",
        lazy=True,
        cascade="all, delete-orphan",
        order_by=(
            "Atendimento.data_atendimento.desc(), "
            "Atendimento.id.desc()"
        )
    )

    # =====================================
    # PROPRIEDADES DE AUDITORIA
    # =====================================
    @property
    def criado_por_nome(self):
        if self.criado_por:
            return self.criado_por.nome

        return "Não registrado"

    @property
    def atualizado_por_nome(self):
        if self.atualizado_por:
            return self.atualizado_por.nome

        return "Não registrado"

    # =====================================
    # REPRESENTAÇÃO
    # =====================================
    def __repr__(self):
        return (
            f"<Cliente "
            f"id={self.id} "
            f"nome='{self.nome}'>"
        )