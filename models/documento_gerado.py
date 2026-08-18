from datetime import datetime

from models import db


class DocumentoGerado(db.Model):
    __tablename__ = "documentos_gerados"

    # =====================================
    # IDENTIFICAÇÃO
    # =====================================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================
    # RELACIONAMENTOS
    # =====================================
    modelo_id = db.Column(
        db.Integer,
        db.ForeignKey("documentos_modelos.id"),
        nullable=False
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    processo_id = db.Column(
        db.Integer,
        db.ForeignKey("processos.id"),
        nullable=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    # =====================================
    # DADOS DO DOCUMENTO
    # =====================================
    nome_documento = db.Column(
        db.String(200),
        nullable=False
    )

    nome_arquivo = db.Column(
        db.String(255),
        nullable=False
    )

    caminho_arquivo = db.Column(
        db.String(500),
        nullable=False
    )

    observacoes = db.Column(
        db.Text
    )

    # =====================================
    # AUDITORIA
    # =====================================
    gerado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =====================================
    # RELACIONAMENTOS SQLALCHEMY
    # =====================================
    modelo = db.relationship(
        "DocumentoModelo",
        backref=db.backref(
            "documentos_gerados",
            lazy=True
        )
    )

    cliente = db.relationship(
        "Cliente",
        backref=db.backref(
            "documentos_gerados",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    processo = db.relationship(
        "Processo",
        backref=db.backref(
            "documentos_gerados",
            lazy=True
        )
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref(
            "documentos_gerados",
            lazy=True
        )
    )

    # =====================================
    # PROPRIEDADES
    # =====================================
    @property
    def nome_cliente(self):
        return (
            self.cliente.nome
            if self.cliente
            else "Sem cliente"
        )

    @property
    def nome_modelo(self):
        return (
            self.modelo.nome
            if self.modelo
            else "Modelo removido"
        )

    @property
    def nome_usuario(self):
        return (
            self.usuario.nome
            if self.usuario
            else "Usuário não encontrado"
        )

    # =====================================
    # REPRESENTAÇÃO
    # =====================================
    def __repr__(self):
        return (
            f"<DocumentoGerado "
            f"id={self.id} "
            f"cliente='{self.nome_cliente}'>"
        )