from datetime import datetime

from models import db


class DocumentoModelo(db.Model):
    __tablename__ = "documentos_modelos"

    # =====================================
    # CATEGORIAS
    # =====================================
    CATEGORIA_PROCURACAO = "PROCURACAO"
    CATEGORIA_CONTRATO = "CONTRATO"
    CATEGORIA_DECLARACAO = "DECLARACAO"
    CATEGORIA_PETICAO = "PETICAO"
    CATEGORIA_RECIBO = "RECIBO"
    CATEGORIA_OUTRO = "OUTRO"

    CATEGORIAS = {
        CATEGORIA_PROCURACAO: "Procuração",
        CATEGORIA_CONTRATO: "Contrato",
        CATEGORIA_DECLARACAO: "Declaração",
        CATEGORIA_PETICAO: "Petição",
        CATEGORIA_RECIBO: "Recibo",
        CATEGORIA_OUTRO: "Outro"
    }

    # =====================================
    # TIPOS DE ARQUIVO
    # =====================================
    TIPO_DOCX = "DOCX"
    TIPO_PDF = "PDF"

    TIPOS_ARQUIVO = {
        TIPO_DOCX: "Documento do Word",
        TIPO_PDF: "Documento PDF"
    }

    # =====================================
    # IDENTIFICAÇÃO
    # =====================================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    descricao = db.Column(
        db.Text
    )

    categoria = db.Column(
        db.String(30),
        nullable=False,
        default=CATEGORIA_OUTRO
    )

    area_juridica = db.Column(
        db.String(50)
    )

    # =====================================
    # ARQUIVO DO MODELO
    # =====================================
    nome_arquivo_original = db.Column(
        db.String(255),
        nullable=False
    )

    nome_arquivo_salvo = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    caminho_arquivo = db.Column(
        db.String(500),
        nullable=False
    )

    tipo_arquivo = db.Column(
        db.String(20),
        nullable=False,
        default=TIPO_DOCX
    )

    # =====================================
    # CONFIGURAÇÕES
    # =====================================
    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    exige_cliente = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    exige_processo = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    exige_honorario = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    observacoes = db.Column(
        db.Text
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
            "modelos_documentos_criados",
            lazy=True
        )
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "modelos_documentos_atualizados",
            lazy=True
        )
    )

    # =====================================
    # PROPRIEDADES
    # =====================================
    @property
    def categoria_nome(self):
        return self.CATEGORIAS.get(
            self.categoria,
            "Categoria não identificada"
        )

    @property
    def tipo_arquivo_nome(self):
        return self.TIPOS_ARQUIVO.get(
            self.tipo_arquivo,
            "Arquivo não identificado"
        )

    @property
    def status_nome(self):
        if self.ativo:
            return "Ativo"

        return "Inativo"

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
            f"<DocumentoModelo "
            f"id={self.id} "
            f"nome='{self.nome}' "
            f"categoria='{self.categoria}'>"
        )