from datetime import date, datetime

from . import db


class Atendimento(db.Model):
    __tablename__ = "atendimentos"

    # ============================================================
    # ÁREAS JURÍDICAS
    # ============================================================

    AREA_TRABALHISTA = "TRABALHISTA"
    AREA_PREVIDENCIARIA = "PREVIDENCIARIA"
    AREA_CIVEL = "CIVEL"
    AREA_FAMILIA = "FAMILIA"
    AREA_CONSUMIDOR = "CONSUMIDOR"
    AREA_OUTRA = "OUTRA"

    AREAS = {
        AREA_TRABALHISTA: "Trabalhista",
        AREA_PREVIDENCIARIA: "Previdenciário",
        AREA_CIVEL: "Cível",
        AREA_FAMILIA: "Família",
        AREA_CONSUMIDOR: "Consumidor",
        AREA_OUTRA: "Outra área",
    }

    # ============================================================
    # STATUS
    # ============================================================

    STATUS_RASCUNHO = "RASCUNHO"
    STATUS_AGUARDANDO_DOCUMENTOS = "AGUARDANDO_DOCUMENTOS"
    STATUS_EM_ANALISE = "EM_ANALISE"
    STATUS_FINALIZADO = "FINALIZADO"
    STATUS_CONVERTIDO_PROCESSO = "CONVERTIDO_PROCESSO"
    STATUS_ARQUIVADO = "ARQUIVADO"

    STATUS = {
        STATUS_RASCUNHO: "Rascunho",
        STATUS_AGUARDANDO_DOCUMENTOS: "Aguardando documentos",
        STATUS_EM_ANALISE: "Em análise",
        STATUS_FINALIZADO: "Finalizado",
        STATUS_CONVERTIDO_PROCESSO: "Convertido em processo",
        STATUS_ARQUIVADO: "Arquivado",
    }

    # ============================================================
    # IDENTIFICAÇÃO
    # ============================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
        index=True,
    )

    area = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default=STATUS_RASCUNHO,
        index=True,
    )

    # ============================================================
    # DATA E HORÁRIO
    # ============================================================

    data_atendimento = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
    )

    horario_atendimento = db.Column(
        db.Time,
        nullable=True,
    )

    # ============================================================
    # INFORMAÇÕES GERAIS
    # ============================================================

    titulo = db.Column(
        db.String(150),
        nullable=True,
    )

    resumo_caso = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_internas = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # RESPONSÁVEL
    # ============================================================

    responsavel_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True,
        index=True,
    )

    responsavel = db.relationship(
        "Usuario",
        foreign_keys=[responsavel_id],
        backref=db.backref(
            "atendimentos_responsaveis",
            lazy=True,
        ),
    )

    # ============================================================
    # CONTROLE
    # ============================================================

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    arquivado = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # ============================================================
    # AUDITORIA
    # ============================================================

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    criado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True,
    )

    atualizado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True,
    )

    criado_por = db.relationship(
        "Usuario",
        foreign_keys=[criado_por_id],
        backref=db.backref(
            "atendimentos_criados",
            lazy=True,
        ),
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "atendimentos_atualizados",
            lazy=True,
        ),
    )

    # ============================================================
    # RELACIONAMENTO COM O CLIENTE
    # ============================================================

    cliente = db.relationship(
        "Cliente",
        back_populates="atendimentos",
    )

    # ============================================================
    # FICHA TRABALHISTA
    # ============================================================

    ficha_trabalhista = db.relationship(
        "FichaTrabalhista",
        back_populates="atendimento",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ============================================================
    # FICHA PREVIDENCIÁRIA
    # ============================================================

    ficha_previdenciaria = db.relationship(
        "FichaPrevidenciaria",
        back_populates="atendimento",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ============================================================
    # FICHA CÍVEL
    # ============================================================

    ficha_civel = db.relationship(
        "FichaCivel",
        back_populates="atendimento",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ============================================================
    # FICHA FAMÍLIA
    # ============================================================

    ficha_familia = db.relationship(
        "FichaFamilia",
        back_populates="atendimento",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    ficha_consumidor = db.relationship(
    "FichaConsumidor",
    backref="atendimento",
    uselist=False,
    cascade="all, delete-orphan",
    )

    # ============================================================
    # PROPRIEDADES GERAIS
    # ============================================================

    @property
    def area_nome(self):
        return self.AREAS.get(
            self.area,
            "Área não identificada",
        )

    @property
    def status_nome(self):
        return self.STATUS.get(
            self.status,
            "Status não identificado",
        )

    @property
    def responsavel_nome(self):
        if self.responsavel:
            return self.responsavel.nome

        return "Não definido"

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

    @property
    def esta_arquivado(self):
        return (
            self.arquivado
            or self.status == self.STATUS_ARQUIVADO
        )

    # ============================================================
    # IDENTIFICAÇÃO DA ÁREA
    # ============================================================

    @property
    def eh_trabalhista(self):
        return self.area == self.AREA_TRABALHISTA

    @property
    def eh_previdenciario(self):
        return self.area == self.AREA_PREVIDENCIARIA

    @property
    def eh_civel(self):
        return self.area == self.AREA_CIVEL

    @property
    def eh_familia(self):
        return self.area == self.AREA_FAMILIA

    @property
    def eh_consumidor(self):
        return self.area == self.AREA_CONSUMIDOR

    # ============================================================
    # FICHA CORRESPONDENTE À ÁREA
    # ============================================================

    @property
    def ficha_area(self):
        """
        Retorna a ficha específica relacionada à área jurídica.

        Enquanto algumas áreas ainda não possuem ficha própria,
        o retorno será None.
        """

        if self.eh_trabalhista:
            return self.ficha_trabalhista

        if self.eh_previdenciario:
            return self.ficha_previdenciaria

        if self.eh_civel:
            return self.ficha_civel

        if self.eh_familia:
            return self.ficha_familia

        return None

    @property
    def possui_ficha(self):
        return self.ficha_area is not None

    @property
    def progresso_percentual(self):
        ficha = self.ficha_area

        if ficha is None:
            return 0

        return getattr(
            ficha,
            "progresso_percentual",
            0,
        )

    # ============================================================
    # REPRESENTAÇÃO
    # ============================================================

    def __repr__(self):
        return (
            f"<Atendimento "
            f"id={self.id} "
            f"cliente_id={self.cliente_id} "
            f"area='{self.area}' "
            f"status='{self.status}'>"
        )