from datetime import datetime

from . import db


class FichaFamilia(db.Model):
    __tablename__ = "fichas_familia"

    # ============================================================
    # OPÇÕES PADRÃO
    # ============================================================

    RESPOSTAS = {
        "SIM": "Sim",
        "NAO": "Não",
        "NAO_SE_APLICA": "Não se aplica",
        "NAO_INFORMADO": "Não informado",
    }

    TIPOS_DEMANDA = {
        "DIVORCIO_CONSENSUAL": "Divórcio consensual",
        "DIVORCIO_LITIGIOSO": "Divórcio litigioso",
        "RECONHECIMENTO_UNIAO_ESTAVEL": "Reconhecimento de união estável",
        "DISSOLUCAO_UNIAO_ESTAVEL": "Dissolução de união estável",
        "GUARDA": "Guarda",
        "REGULAMENTACAO_CONVIVENCIA": "Regulamentação de convivência",
        "ALIMENTOS": "Alimentos",
        "REVISIONAL_ALIMENTOS": "Revisional de alimentos",
        "EXONERACAO_ALIMENTOS": "Exoneração de alimentos",
        "EXECUCAO_ALIMENTOS": "Execução de alimentos",
        "INVESTIGACAO_PATERNIDADE": "Investigação de paternidade",
        "RECONHECIMENTO_PATERNIDADE": "Reconhecimento de paternidade",
        "NEGATORIA_PATERNIDADE": "Negatória de paternidade",
        "ADOCAO": "Adoção",
        "TUTELA": "Tutela",
        "CURATELA": "Curatela",
        "INTERDICAO": "Interdição",
        "PARTILHA_BENS": "Partilha de bens",
        "INVENTARIO": "Inventário",
        "OUTRA": "Outra demanda familiar",
    }

    TIPOS_RELACAO = {
        "CASAMENTO": "Casamento",
        "UNIAO_ESTAVEL": "União estável",
        "NAMORO": "Namoro",
        "SEPARACAO_DE_FATO": "Separação de fato",
        "RELACAO_PARENTAL": "Relação parental",
        "OUTRA": "Outra",
    }

    REGIMES_BENS = {
        "COMUNHAO_PARCIAL": "Comunhão parcial de bens",
        "COMUNHAO_UNIVERSAL": "Comunhão universal de bens",
        "SEPARACAO_TOTAL": "Separação total de bens",
        "PARTICIPACAO_FINAL_AQUESTOS": "Participação final nos aquestos",
        "SEPARACAO_OBRIGATORIA": "Separação obrigatória de bens",
        "NAO_INFORMADO": "Não informado",
        "NAO_SE_APLICA": "Não se aplica",
    }

    TIPOS_GUARDA = {
        "COMPARTILHADA": "Guarda compartilhada",
        "UNILATERAL_MAE": "Guarda unilateral materna",
        "UNILATERAL_PAI": "Guarda unilateral paterna",
        "TERCEIRO": "Guarda atribuída a terceiro",
        "DE_FATO": "Guarda de fato",
        "A_DEFINIR": "A definir",
    }

    VIABILIDADES = {
        "ALTA": "Alta",
        "MEDIA": "Média",
        "BAIXA": "Baixa",
        "INDEFINIDA": "Ainda não definida",
    }

    # ============================================================
    # IDENTIFICAÇÃO E VÍNCULOS
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

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=True,
        index=True,
    )

    atendimento = db.relationship(
        "Atendimento",
        back_populates="ficha_familia",
    )

    cliente = db.relationship(
        "Cliente",
        foreign_keys=[cliente_id],
        backref=db.backref(
            "fichas_familia",
            lazy=True,
        ),
    )

    # ============================================================
    # ETAPA 1 — ATENDIMENTO
    # ============================================================

    tipo_demanda = db.Column(
        db.String(60),
        nullable=True,
    )

    outro_tipo_demanda = db.Column(
        db.String(150),
        nullable=True,
    )

    motivo_principal = db.Column(
        db.Text,
        nullable=True,
    )

    existe_urgencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_urgencia = db.Column(
        db.Text,
        nullable=True,
    )

    existe_processo_anterior = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    numero_processo_anterior = db.Column(
        db.String(80),
        nullable=True,
    )

    vara_processo_anterior = db.Column(
        db.String(150),
        nullable=True,
    )

    comarca_processo_anterior = db.Column(
        db.String(150),
        nullable=True,
    )

    observacoes_atendimento = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 2 — CLIENTE
    # ============================================================

    cliente_estado_civil = db.Column(
        db.String(50),
        nullable=True,
    )

    cliente_profissao = db.Column(
        db.String(120),
        nullable=True,
    )

    cliente_renda_mensal = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    cliente_reside_com_quem = db.Column(
        db.String(200),
        nullable=True,
    )

    cliente_dependentes = db.Column(
        db.Text,
        nullable=True,
    )

    cliente_possui_deficiencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cliente_descricao_deficiencia = db.Column(
        db.Text,
        nullable=True,
    )

    cliente_recebe_beneficio = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cliente_beneficio_descricao = db.Column(
        db.String(200),
        nullable=True,
    )

    observacoes_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 3 — RELAÇÃO FAMILIAR
    # ============================================================

    tipo_relacao = db.Column(
        db.String(50),
        nullable=True,
    )

    data_inicio_relacao = db.Column(
        db.Date,
        nullable=True,
    )

    data_casamento = db.Column(
        db.Date,
        nullable=True,
    )

    data_separacao_fato = db.Column(
        db.Date,
        nullable=True,
    )

    regime_bens = db.Column(
        db.String(50),
        nullable=True,
    )

    possui_pacto_antenupcial = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_pacto_antenupcial = db.Column(
        db.Text,
        nullable=True,
    )

    convivencia_publica_continua = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    objetivo_constituir_familia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    relacao_encerrada = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    motivo_termino_relacao = db.Column(
        db.Text,
        nullable=True,
    )

    houve_violencia_domestica = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_violencia_domestica = db.Column(
        db.Text,
        nullable=True,
    )

    existe_medida_protetiva = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    numero_medida_protetiva = db.Column(
        db.String(80),
        nullable=True,
    )

    observacoes_relacao = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 4 — PARTE CONTRÁRIA
    # ============================================================

    parte_contraria_nome = db.Column(
        db.String(150),
        nullable=True,
    )

    parte_contraria_cpf = db.Column(
        db.String(14),
        nullable=True,
    )

    parte_contraria_rg = db.Column(
        db.String(30),
        nullable=True,
    )

    parte_contraria_data_nascimento = db.Column(
        db.Date,
        nullable=True,
    )

    parte_contraria_profissao = db.Column(
        db.String(120),
        nullable=True,
    )

    parte_contraria_renda_mensal = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    parte_contraria_telefone = db.Column(
        db.String(30),
        nullable=True,
    )

    parte_contraria_email = db.Column(
        db.String(150),
        nullable=True,
    )

    parte_contraria_endereco = db.Column(
        db.String(255),
        nullable=True,
    )

    parte_contraria_cidade = db.Column(
        db.String(120),
        nullable=True,
    )

    parte_contraria_estado = db.Column(
        db.String(2),
        nullable=True,
    )

    parte_contraria_local_trabalho = db.Column(
        db.String(200),
        nullable=True,
    )

    comunicacao_entre_partes = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_parte_contraria = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 5 — FILHOS
    # ============================================================

    possui_filhos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    quantidade_filhos = db.Column(
        db.Integer,
        nullable=True,
    )

    filhos_em_comum = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    filhos_menores = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    filhos_incapazes = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    dados_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    filhos_residem_com = db.Column(
        db.String(200),
        nullable=True,
    )

    existe_filho_com_deficiencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    necessidades_especiais_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    escola_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    plano_saude_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    despesas_mensais_filhos = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    detalhamento_despesas_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_filhos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 6 — GUARDA E CONVIVÊNCIA
    # ============================================================

    existe_acordo_guarda = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    tipo_guarda_atual = db.Column(
        db.String(50),
        nullable=True,
    )

    tipo_guarda_pretendida = db.Column(
        db.String(50),
        nullable=True,
    )

    guarda_de_fato_com = db.Column(
        db.String(150),
        nullable=True,
    )

    residencia_referencia_filhos = db.Column(
        db.String(200),
        nullable=True,
    )

    regime_convivencia_atual = db.Column(
        db.Text,
        nullable=True,
    )

    regime_convivencia_pretendido = db.Column(
        db.Text,
        nullable=True,
    )

    existe_dificuldade_convivencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_dificuldade_convivencia = db.Column(
        db.Text,
        nullable=True,
    )

    existe_risco_crianca_adolescente = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_risco_crianca_adolescente = db.Column(
        db.Text,
        nullable=True,
    )

    existe_alienacao_parental = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    indicios_alienacao_parental = db.Column(
        db.Text,
        nullable=True,
    )

    necessita_estudo_psicossocial = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    observacoes_guarda = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 7 — ALIMENTOS
    # ============================================================

    existe_pensao_atual = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pensao_fixada_judicialmente = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    numero_processo_alimentos = db.Column(
        db.String(80),
        nullable=True,
    )

    valor_pensao_atual = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    percentual_pensao_atual = db.Column(
        db.Numeric(8, 2),
        nullable=True,
    )

    forma_pagamento_pensao = db.Column(
        db.String(150),
        nullable=True,
    )

    pensao_esta_em_atraso = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    meses_em_atraso = db.Column(
        db.Integer,
        nullable=True,
    )

    valor_debito_estimado = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    valor_pretendido_alimentos = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    percentual_pretendido_alimentos = db.Column(
        db.Numeric(8, 2),
        nullable=True,
    )

    despesas_alimentando = db.Column(
        db.Text,
        nullable=True,
    )

    capacidade_financeira_alimentante = db.Column(
        db.Text,
        nullable=True,
    )

    existem_outros_dependentes = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_outros_dependentes = db.Column(
        db.Text,
        nullable=True,
    )

    pretende_alimentos_provisorios = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    observacoes_alimentos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 8 — PATRIMÔNIO
    # ============================================================

    possui_bens_partilhar = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    imoveis = db.Column(
        db.Text,
        nullable=True,
    )

    veiculos = db.Column(
        db.Text,
        nullable=True,
    )

    contas_bancarias_investimentos = db.Column(
        db.Text,
        nullable=True,
    )

    empresas_quotas_sociais = db.Column(
        db.Text,
        nullable=True,
    )

    bens_moveis_relevantes = db.Column(
        db.Text,
        nullable=True,
    )

    dividas_comuns = db.Column(
        db.Text,
        nullable=True,
    )

    bens_particulares_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    bens_particulares_parte_contraria = db.Column(
        db.Text,
        nullable=True,
    )

    existe_ocultacao_patrimonial = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    indicios_ocultacao_patrimonial = db.Column(
        db.Text,
        nullable=True,
    )

    existe_acordo_partilha = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    proposta_partilha = db.Column(
        db.Text,
        nullable=True,
    )

    valor_estimado_patrimonio = db.Column(
        db.Numeric(14, 2),
        nullable=True,
    )

    observacoes_patrimonio = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 9 — DOCUMENTOS
    # ============================================================

    possui_documento_identificacao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_comprovante_residencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_certidao_casamento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_certidao_uniao_estavel = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_certidoes_nascimento_filhos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_comprovantes_renda = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_comprovantes_despesas = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_documentos_bens = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_acordo_anterior = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_decisao_judicial = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_boletim_ocorrencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_medida_protetiva = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_conversas_mensagens = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_fotos_videos_audios = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_laudos_relatorios = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
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
    # ETAPA 10 — ANÁLISE JURÍDICA
    # ============================================================

    competencia = db.Column(
        db.String(150),
        nullable=True,
    )

    foro_competente = db.Column(
        db.String(150),
        nullable=True,
    )

    existe_prevencao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    processo_prevento = db.Column(
        db.String(80),
        nullable=True,
    )

    necessidade_intervencao_mp = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    necessidade_segredo_justica = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    necessidade_tutela_urgencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    fundamentos_tutela_urgencia = db.Column(
        db.Text,
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

    provas_necessarias = db.Column(
        db.Text,
        nullable=True,
    )

    riscos_processo = db.Column(
        db.Text,
        nullable=True,
    )

    estrategia_sugerida = db.Column(
        db.Text,
        nullable=True,
    )

    providencias_iniciais = db.Column(
        db.Text,
        nullable=True,
    )

    possibilidade_acordo = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    termos_possivel_acordo = db.Column(
        db.Text,
        nullable=True,
    )

    viabilidade_demanda = db.Column(
        db.String(30),
        nullable=True,
        default="INDEFINIDA",
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
    # CONTROLE DE ETAPAS
    # ============================================================

    etapa_atual = db.Column(
        db.String(40),
        nullable=False,
        default="atendimento",
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

    etapa_relacao_familiar_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_parte_contraria_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_filhos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_guarda_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_alimentos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_patrimonio_concluida = db.Column(
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
            "fichas_familia_criadas",
            lazy=True,
        ),
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "fichas_familia_atualizadas",
            lazy=True,
        ),
    )

    # ============================================================
    # PROPRIEDADES
    # ============================================================

    @property
    def progresso_percentual(self):
        campos_etapas = (
            "etapa_atendimento_concluida",
            "etapa_cliente_concluida",
            "etapa_relacao_familiar_concluida",
            "etapa_parte_contraria_concluida",
            "etapa_filhos_concluida",
            "etapa_guarda_concluida",
            "etapa_alimentos_concluida",
            "etapa_patrimonio_concluida",
            "etapa_documentos_concluida",
            "etapa_analise_concluida",
        )

        total = len(campos_etapas)
        concluidas = sum(
            1
            for campo in campos_etapas
            if bool(getattr(self, campo, False))
        )

        if total == 0:
            return 0

        return int(concluidas * 100 / total)

    @property
    def tipo_demanda_nome(self):
        return self.TIPOS_DEMANDA.get(
            self.tipo_demanda,
            self.outro_tipo_demanda or "Não informado",
        )

    @property
    def relacao_nome(self):
        return self.TIPOS_RELACAO.get(
            self.tipo_relacao,
            "Não informado",
        )

    @property
    def regime_bens_nome(self):
        return self.REGIMES_BENS.get(
            self.regime_bens,
            "Não informado",
        )

    @property
    def guarda_atual_nome(self):
        return self.TIPOS_GUARDA.get(
            self.tipo_guarda_atual,
            "Não informado",
        )

    @property
    def guarda_pretendida_nome(self):
        return self.TIPOS_GUARDA.get(
            self.tipo_guarda_pretendida,
            "Não informado",
        )

    @property
    def viabilidade_nome(self):
        return self.VIABILIDADES.get(
            self.viabilidade_demanda,
            "Ainda não definida",
        )

    # ============================================================
    # REPRESENTAÇÃO
    # ============================================================

    def __repr__(self):
        return (
            f"<FichaFamilia "
            f"id={self.id} "
            f"atendimento_id={self.atendimento_id} "
            f"tipo_demanda='{self.tipo_demanda}'>"
        )