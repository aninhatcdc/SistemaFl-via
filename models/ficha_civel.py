from datetime import datetime

from . import db


class FichaCivel(db.Model):
    __tablename__ = "fichas_civeis"

    # ============================================================
    # RESPOSTAS PADRONIZADAS
    # ============================================================

    RESPOSTA_SIM = "SIM"
    RESPOSTA_NAO = "NAO"
    RESPOSTA_NAO_SABE = "NAO_SABE"
    RESPOSTA_NAO_RECORDA = "NAO_RECORDA"

    RESPOSTAS = {
        RESPOSTA_SIM: "Sim",
        RESPOSTA_NAO: "Não",
        RESPOSTA_NAO_SABE: "Não sabe informar",
        RESPOSTA_NAO_RECORDA: "Não se recorda",
    }

    # ============================================================
    # NATUREZA DA DEMANDA
    # ============================================================

    NATUREZA_COBRANCA = "COBRANCA"
    NATUREZA_INDENIZACAO = "INDENIZACAO"
    NATUREZA_CONTRATOS = "CONTRATOS"
    NATUREZA_RESPONSABILIDADE_CIVIL = "RESPONSABILIDADE_CIVIL"
    NATUREZA_OBRIGACAO_FAZER = "OBRIGACAO_FAZER"
    NATUREZA_OBRIGACAO_NAO_FAZER = "OBRIGACAO_NAO_FAZER"
    NATUREZA_DANOS_MORAIS = "DANOS_MORAIS"
    NATUREZA_DANOS_MATERIAIS = "DANOS_MATERIAIS"
    NATUREZA_USUCAPIAO = "USUCAPIAO"
    NATUREZA_POSSE = "POSSE"
    NATUREZA_VIZINHANCA = "VIZINHANCA"
    NATUREZA_CONDOMINIO = "CONDOMINIO"
    NATUREZA_INVENTARIO = "INVENTARIO"
    NATUREZA_SUCESSOES = "SUCESSOES"
    NATUREZA_OUTRA = "OUTRA"

    NATUREZAS = {
        NATUREZA_COBRANCA: "Cobrança",
        NATUREZA_INDENIZACAO: "Indenização",
        NATUREZA_CONTRATOS: "Contratos",
        NATUREZA_RESPONSABILIDADE_CIVIL: "Responsabilidade civil",
        NATUREZA_OBRIGACAO_FAZER: "Obrigação de fazer",
        NATUREZA_OBRIGACAO_NAO_FAZER: "Obrigação de não fazer",
        NATUREZA_DANOS_MORAIS: "Danos morais",
        NATUREZA_DANOS_MATERIAIS: "Danos materiais",
        NATUREZA_USUCAPIAO: "Usucapião",
        NATUREZA_POSSE: "Posse",
        NATUREZA_VIZINHANCA: "Direito de vizinhança",
        NATUREZA_CONDOMINIO: "Condomínio",
        NATUREZA_INVENTARIO: "Inventário",
        NATUREZA_SUCESSOES: "Sucessões",
        NATUREZA_OUTRA: "Outra",
    }

    # ============================================================
    # IDENTIFICAÇÃO
    # ============================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "atendimentos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # ============================================================
    # CONTROLE DAS ETAPAS
    # ============================================================

    etapa_atual = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    etapa_atendimento_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_cliente_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_parte_contraria_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_fatos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_contrato_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_danos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_tentativas_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_documentos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_analise_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

        # ============================================================
    # 1. DADOS DO ATENDIMENTO
    # ============================================================

    natureza_demanda = db.Column(
        db.String(50),
        nullable=True,
    )

    natureza_demanda_outro = db.Column(
        db.String(150),
        nullable=True,
    )

    assunto_principal = db.Column(
        db.String(200),
        nullable=True,
    )

    objetivo_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    existe_urgencia = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_urgencia = db.Column(
        db.Text,
        nullable=True,
    )

    data_limite_urgencia = db.Column(
        db.Date,
        nullable=True,
    )

    valor_estimado_causa = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    aceita_acordo = db.Column(
        db.String(20),
        nullable=True,
    )

    valor_minimo_acordo = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    observacoes_atendimento = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 2. DADOS COMPLEMENTARES DO CLIENTE
    # ============================================================

    estado_civil_atual = db.Column(
        db.String(50),
        nullable=True,
    )

    profissao_atual = db.Column(
        db.String(150),
        nullable=True,
    )

    renda_mensal_aproximada = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    possui_beneficio_justica_gratuita = db.Column(
        db.String(20),
        nullable=True,
    )

    motivo_justica_gratuita = db.Column(
        db.Text,
        nullable=True,
    )

    contato_alternativo_nome = db.Column(
        db.String(150),
        nullable=True,
    )

    contato_alternativo_telefone = db.Column(
        db.String(20),
        nullable=True,
    )

    contato_alternativo_relacao = db.Column(
        db.String(100),
        nullable=True,
    )

    melhor_horario_contato = db.Column(
        db.String(100),
        nullable=True,
    )

    observacoes_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 3. PARTE CONTRÁRIA
    # ============================================================

    parte_contraria_nome = db.Column(
        db.String(200),
        nullable=True,
    )

    parte_contraria_tipo = db.Column(
        db.String(30),
        nullable=True,
    )

    parte_contraria_cpf_cnpj = db.Column(
        db.String(20),
        nullable=True,
    )

    parte_contraria_rg = db.Column(
        db.String(30),
        nullable=True,
    )

    parte_contraria_endereco = db.Column(
        db.String(255),
        nullable=True,
    )

    parte_contraria_cidade = db.Column(
        db.String(100),
        nullable=True,
    )

    parte_contraria_estado = db.Column(
        db.String(2),
        nullable=True,
    )

    parte_contraria_cep = db.Column(
        db.String(10),
        nullable=True,
    )

    parte_contraria_telefone = db.Column(
        db.String(20),
        nullable=True,
    )

    parte_contraria_whatsapp = db.Column(
        db.String(20),
        nullable=True,
    )

    parte_contraria_email = db.Column(
        db.String(150),
        nullable=True,
    )

    relacao_com_cliente = db.Column(
        db.String(150),
        nullable=True,
    )

    possui_advogado = db.Column(
        db.String(20),
        nullable=True,
    )

    advogado_parte_contraria = db.Column(
        db.String(150),
        nullable=True,
    )

    observacoes_parte_contraria = db.Column(
        db.Text,
        nullable=True,
    )

        # ============================================================
    # 4. FATOS
    # ============================================================

    data_inicio_fatos = db.Column(
        db.Date,
        nullable=True,
    )

    data_ultimo_fato = db.Column(
        db.Date,
        nullable=True,
    )

    local_fatos = db.Column(
        db.String(255),
        nullable=True,
    )

    descricao_detalhada_fatos = db.Column(
        db.Text,
        nullable=True,
    )

    fatos_continuam_ocorrendo = db.Column(
        db.String(20),
        nullable=True,
    )

    houve_ameaca = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_ameaca = db.Column(
        db.Text,
        nullable=True,
    )

    existem_testemunhas = db.Column(
        db.String(20),
        nullable=True,
    )

    testemunhas_dados = db.Column(
        db.Text,
        nullable=True,
    )

    existem_provas = db.Column(
        db.String(20),
        nullable=True,
    )

    provas_existentes = db.Column(
        db.Text,
        nullable=True,
    )

    cliente_participou_diretamente = db.Column(
        db.String(20),
        nullable=True,
    )

    terceiros_envolvidos = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_fatos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 5. CONTRATOS E OBRIGAÇÕES
    # ============================================================

    existe_contrato = db.Column(
        db.String(20),
        nullable=True,
    )

    contrato_escrito = db.Column(
        db.String(20),
        nullable=True,
    )

    tipo_contrato = db.Column(
        db.String(150),
        nullable=True,
    )

    data_contrato = db.Column(
        db.Date,
        nullable=True,
    )

    data_fim_contrato = db.Column(
        db.Date,
        nullable=True,
    )

    valor_contrato = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    forma_pagamento = db.Column(
        db.String(150),
        nullable=True,
    )

    contrato_quitado = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_comprovantes_pagamento = db.Column(
        db.String(20),
        nullable=True,
    )

    obrigacao_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    obrigacao_parte_contraria = db.Column(
        db.Text,
        nullable=True,
    )

    obrigacao_descumprida = db.Column(
        db.Text,
        nullable=True,
    )

    houve_multa_contratual = db.Column(
        db.String(20),
        nullable=True,
    )

    valor_multa_contratual = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    observacoes_contrato = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 6. DANOS E VALORES
    # ============================================================

    houve_dano_material = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_dano_material = db.Column(
        db.Text,
        nullable=True,
    )

    valor_dano_material = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    houve_dano_moral = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_dano_moral = db.Column(
        db.Text,
        nullable=True,
    )

    valor_pretendido_dano_moral = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    houve_lucros_cessantes = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_lucros_cessantes = db.Column(
        db.Text,
        nullable=True,
    )

    valor_lucros_cessantes = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    houve_dano_estetico = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_dano_estetico = db.Column(
        db.Text,
        nullable=True,
    )

    existem_gastos_futuros = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_gastos_futuros = db.Column(
        db.Text,
        nullable=True,
    )

    valor_total_prejuizo = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    observacoes_danos = db.Column(
        db.Text,
        nullable=True,
    )

        # ============================================================
    # 7. TENTATIVAS DE SOLUÇÃO
    # ============================================================

    houve_contato_parte_contraria = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_contatos = db.Column(
        db.Text,
        nullable=True,
    )

    houve_proposta_acordo = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_proposta_acordo = db.Column(
        db.Text,
        nullable=True,
    )

    enviou_notificacao_extrajudicial = db.Column(
        db.String(20),
        nullable=True,
    )

    data_notificacao_extrajudicial = db.Column(
        db.Date,
        nullable=True,
    )

    houve_resposta_notificacao = db.Column(
        db.String(20),
        nullable=True,
    )

    descricao_resposta_notificacao = db.Column(
        db.Text,
        nullable=True,
    )

    fez_reclamacao_administrativa = db.Column(
        db.String(20),
        nullable=True,
    )

    orgao_reclamacao = db.Column(
        db.String(150),
        nullable=True,
    )

    protocolo_reclamacao = db.Column(
        db.String(100),
        nullable=True,
    )

    registrou_boletim_ocorrencia = db.Column(
        db.String(20),
        nullable=True,
    )

    numero_boletim_ocorrencia = db.Column(
        db.String(100),
        nullable=True,
    )

    data_boletim_ocorrencia = db.Column(
        db.Date,
        nullable=True,
    )

    existe_processo_anterior = db.Column(
        db.String(20),
        nullable=True,
    )

    numero_processo_anterior = db.Column(
        db.String(50),
        nullable=True,
    )

    resultado_processo_anterior = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_tentativas = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 8. DOCUMENTOS
    # ============================================================

    possui_documento_identificacao = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_comprovante_residencia = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_contrato = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_comprovantes = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_conversas = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_fotos = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_audios = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_videos = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_laudos = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_orcamentos = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_notificacoes = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_boletim_ocorrencia = db.Column(
        db.String(20),
        nullable=True,
    )

    outros_documentos = db.Column(
        db.Text,
        nullable=True,
    )

    documentos_entregues = db.Column(
        db.Text,
        nullable=True,
    )

    documentos_pendentes = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_documentos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 9. ANÁLISE JURÍDICA
    # ============================================================

    existe_prescricao = db.Column(
        db.String(20),
        nullable=True,
    )

    prazo_prescricional = db.Column(
        db.String(150),
        nullable=True,
    )

    data_final_prescricao = db.Column(
        db.Date,
        nullable=True,
    )

    competencia = db.Column(
        db.String(200),
        nullable=True,
    )

    foro_competente = db.Column(
        db.String(200),
        nullable=True,
    )

    legitimidade_cliente = db.Column(
        db.String(20),
        nullable=True,
    )

    legitimidade_parte_contraria = db.Column(
        db.String(20),
        nullable=True,
    )

    fundamentos_juridicos = db.Column(
        db.Text,
        nullable=True,
    )

    pedidos_sugeridos = db.Column(
        db.Text,
        nullable=True,
    )

    necessidade_tutela_urgencia = db.Column(
        db.String(20),
        nullable=True,
    )

    fundamentos_tutela_urgencia = db.Column(
        db.Text,
        nullable=True,
    )

    riscos_processo = db.Column(
        db.Text,
        nullable=True,
    )

    provas_necessarias = db.Column(
        db.Text,
        nullable=True,
    )

    providencias_iniciais = db.Column(
        db.Text,
        nullable=True,
    )

    estrategia_sugerida = db.Column(
        db.Text,
        nullable=True,
    )

    viabilidade_demanda = db.Column(
        db.String(50),
        nullable=True,
    )

    parecer_inicial = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_gerais = db.Column(
        db.Text,
        nullable=True,
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
            "fichas_civeis_criadas",
            lazy=True,
        ),
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "fichas_civeis_atualizadas",
            lazy=True,
        ),
    )

    # ============================================================
    # RELACIONAMENTO COM O ATENDIMENTO
    # ============================================================

    atendimento = db.relationship(
        "Atendimento",
        back_populates="ficha_civel",
    )

    # ============================================================
    # PROPRIEDADES
    # ============================================================

    @property
    def cliente(self):
        if self.atendimento:
            return self.atendimento.cliente

        return None

    @classmethod
    def resposta_nome(cls, valor):
        if not valor:
            return "Não informado"

        return cls.RESPOSTAS.get(
            valor,
            "Não informado",
        )

    @property
    def natureza_demanda_nome(self):
        if not self.natureza_demanda:
            return "Não informada"

        if (
            self.natureza_demanda == self.NATUREZA_OUTRA
            and self.natureza_demanda_outro
        ):
            return self.natureza_demanda_outro

        return self.NATUREZAS.get(
            self.natureza_demanda,
            "Não informada",
        )

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
    def progresso_percentual(self):
        etapas = [
            self.etapa_atendimento_concluida,
            self.etapa_cliente_concluida,
            self.etapa_parte_contraria_concluida,
            self.etapa_fatos_concluida,
            self.etapa_contrato_concluida,
            self.etapa_danos_concluida,
            self.etapa_tentativas_concluida,
            self.etapa_documentos_concluida,
            self.etapa_analise_concluida,
        ]

        concluidas = sum(
            1 for etapa in etapas if etapa
        )

        return int(
            concluidas / len(etapas) * 100
        )

    # ============================================================
    # REPRESENTAÇÃO
    # ============================================================

    def __repr__(self):
        return (
            f"<FichaCivel "
            f"id={self.id} "
            f"atendimento_id={self.atendimento_id} "
            f"etapa_atual={self.etapa_atual}>"
        )
