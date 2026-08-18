from datetime import datetime

from . import db


class FichaTrabalhista(db.Model):
    __tablename__ = "fichas_trabalhistas"

    # =====================================
    # RESPOSTAS PADRONIZADAS
    # =====================================
    RESPOSTA_SIM = "SIM"
    RESPOSTA_NAO = "NAO"
    RESPOSTA_NAO_SABE = "NAO_SABE"
    RESPOSTA_NAO_RECORDA = "NAO_RECORDA"

    RESPOSTAS = {
        RESPOSTA_SIM: "Sim",
        RESPOSTA_NAO: "Não",
        RESPOSTA_NAO_SABE: "Não sabe informar",
        RESPOSTA_NAO_RECORDA: "Não se recorda"
    }

    # =====================================
    # ESCOLARIDADE
    # =====================================
    ESCOLARIDADE_FUNDAMENTAL = "FUNDAMENTAL"
    ESCOLARIDADE_MEDIO = "MEDIO"
    ESCOLARIDADE_TECNICO = "TECNICO"
    ESCOLARIDADE_SUPERIOR = "SUPERIOR"
    ESCOLARIDADE_POS_GRADUACAO = "POS_GRADUACAO"
    ESCOLARIDADE_OUTRA = "OUTRA"

    ESCOLARIDADES = {
        ESCOLARIDADE_FUNDAMENTAL: "Ensino Fundamental",
        ESCOLARIDADE_MEDIO: "Ensino Médio",
        ESCOLARIDADE_TECNICO: "Ensino Técnico",
        ESCOLARIDADE_SUPERIOR: "Ensino Superior",
        ESCOLARIDADE_POS_GRADUACAO: "Pós-graduação",
        ESCOLARIDADE_OUTRA: "Outra"
    }

    # =====================================
    # TIPOS DE CONTRATO
    # =====================================
    CONTRATO_INDETERMINADO = "INDETERMINADO"
    CONTRATO_EXPERIENCIA = "EXPERIENCIA"
    CONTRATO_DETERMINADO = "DETERMINADO"
    CONTRATO_TEMPORARIO = "TEMPORARIO"
    CONTRATO_INTERMITENTE = "INTERMITENTE"
    CONTRATO_APRENDIZ = "APRENDIZ"
    CONTRATO_OUTRO = "OUTRO"

    TIPOS_CONTRATO = {
        CONTRATO_INDETERMINADO: "Prazo indeterminado",
        CONTRATO_EXPERIENCIA: "Experiência",
        CONTRATO_DETERMINADO: "Prazo determinado",
        CONTRATO_TEMPORARIO: "Temporário",
        CONTRATO_INTERMITENTE: "Intermitente",
        CONTRATO_APRENDIZ: "Aprendiz",
        CONTRATO_OUTRO: "Outro"
    }

    # =====================================
    # FORMAS DE PAGAMENTO EXTRAFOLHA
    # =====================================
    PAGAMENTO_SEM_RECIBO = "SEM_RECIBO"
    PAGAMENTO_ENVELOPE = "ENVELOPE"
    PAGAMENTO_ESPECIE = "ESPECIE"
    PAGAMENTO_PIX = "PIX"
    PAGAMENTO_OUTRO = "OUTRO"

    FORMAS_PAGAMENTO_EXTRAFOLHA = {
        PAGAMENTO_SEM_RECIBO: "Sem recibo",
        PAGAMENTO_ENVELOPE: "Em envelope",
        PAGAMENTO_ESPECIE: "Em espécie",
        PAGAMENTO_PIX: "PIX",
        PAGAMENTO_OUTRO: "Outro"
    }

    # =====================================
    # MOMENTO DO PAGAMENTO DAS FÉRIAS
    # =====================================
    FERIAS_ATE_DOIS_DIAS_ANTES = "ATE_DOIS_DIAS_ANTES"
    FERIAS_DURANTE = "DURANTE"
    FERIAS_APOS_RETORNO = "APOS_RETORNO"
    FERIAS_NAO_RECEBEU = "NAO_RECEBEU"

    MOMENTOS_PAGAMENTO_FERIAS = {
        FERIAS_ATE_DOIS_DIAS_ANTES: (
            "Até dois dias antes do início das férias"
        ),
        FERIAS_DURANTE: "Durante as férias",
        FERIAS_APOS_RETORNO: "Após o retorno das férias",
        FERIAS_NAO_RECEBEU: "Não recebeu"
    }

    # =====================================
    # IDENTIFICAÇÃO
    # =====================================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    atendimento_id = db.Column(
        db.Integer,
        db.ForeignKey("atendimentos.id"),
        nullable=False,
        unique=True,
        index=True
    )

    # =====================================
    # CONTROLE DAS ETAPAS
    # =====================================
    etapa_atual = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    etapa_atendimento_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_cliente_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_empresa_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_admissao_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_contrato_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_local_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_salario_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_ferias_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_decimo_terceiro_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    etapa_rescisao_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # =====================================
    # 1. DADOS COMPLEMENTARES DO CLIENTE
    # =====================================
    orgao_expedidor = db.Column(
        db.String(30),
        nullable=True
    )

    escolaridade = db.Column(
        db.String(30),
        nullable=True
    )

    escolaridade_outro = db.Column(
        db.String(100),
        nullable=True
    )

    contato_parente_amigo = db.Column(
        db.String(120),
        nullable=True
    )

    contato_parente_amigo_telefone = db.Column(
        db.String(20),
        nullable=True
    )

    contato_parente_amigo_relacao = db.Column(
        db.String(100),
        nullable=True
    )

    instagram = db.Column(
        db.String(150),
        nullable=True
    )

    facebook = db.Column(
        db.String(150),
        nullable=True
    )

    tiktok = db.Column(
        db.String(150),
        nullable=True
    )

    outra_rede_social = db.Column(
        db.String(150),
        nullable=True
    )

    nome_pai = db.Column(
        db.String(150),
        nullable=True
    )

    nome_mae = db.Column(
        db.String(150),
        nullable=True
    )

    possui_filhos_menores = db.Column(
        db.String(20),
        nullable=True
    )

    quantidade_filhos_menores = db.Column(
        db.Integer,
        nullable=True
    )

    possui_deficiencia = db.Column(
        db.String(20),
        nullable=True
    )

    descricao_deficiencia = db.Column(
        db.String(255),
        nullable=True
    )

    recebeu_beneficio_inss = db.Column(
        db.String(20),
        nullable=True
    )

    beneficio_inss_descricao = db.Column(
        db.String(255),
        nullable=True
    )

    observacoes_dados_cliente = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 2. DADOS DA EMPRESA
    # =====================================
    empresa_nome = db.Column(
        db.String(200),
        nullable=True
    )

    empresa_nome_fantasia = db.Column(
        db.String(200),
        nullable=True
    )

    empresa_cnpj_cpf = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_endereco = db.Column(
        db.String(255),
        nullable=True
    )

    empresa_cidade = db.Column(
        db.String(100),
        nullable=True
    )

    empresa_telefone = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_whatsapp = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_ramo_atividade = db.Column(
        db.String(150),
        nullable=True
    )

    empresa_proprietario = db.Column(
        db.String(150),
        nullable=True
    )

    empresa_socio = db.Column(
        db.String(150),
        nullable=True
    )

    empresa_grupo_economico = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_grupo_economico_qual = db.Column(
        db.String(255),
        nullable=True
    )

    empresa_mudou_nome = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_nome_anterior = db.Column(
        db.String(200),
        nullable=True
    )

    empresa_foi_vendida = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_trocou_cnpj = db.Column(
        db.String(20),
        nullable=True
    )

    empresa_cnpj_anterior = db.Column(
        db.String(20),
        nullable=True
    )

    prestava_servicos_outra_empresa = db.Column(
        db.String(20),
        nullable=True
    )

    prestava_servicos_empresa_qual = db.Column(
        db.String(200),
        nullable=True
    )

    trabalhava_dependencias_outra_empresa = db.Column(
        db.String(20),
        nullable=True
    )

    trabalhava_dependencias_empresa_qual = db.Column(
        db.String(200),
        nullable=True
    )

    observacoes_empresa = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 3. ADMISSÃO
    # =====================================
    data_admissao_real = db.Column(
        db.Date,
        nullable=True
    )

    data_admissao_carteira = db.Column(
        db.Date,
        nullable=True
    )

    responsavel_contratacao = db.Column(
        db.String(150),
        nullable=True
    )

    foi_indicado = db.Column(
        db.String(20),
        nullable=True
    )

    indicado_por = db.Column(
        db.String(150),
        nullable=True
    )

    realizou_entrevista = db.Column(
        db.String(20),
        nullable=True
    )

    fez_exame_admissional = db.Column(
        db.String(20),
        nullable=True
    )

    exame_admissional_clinica = db.Column(
        db.String(200),
        nullable=True
    )

    recebeu_copia_exame_admissional = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_contrato_antes_inicio = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_copia_contrato = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_documento_em_branco = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_contrato_trabalho = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_ficha_registro = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_termo_responsabilidade = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_vale_transporte = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_regulamento_interno = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_termo_confidencialidade = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_outros_documentos = db.Column(
        db.String(20),
        nullable=True
    )

    outros_documentos_admissao = db.Column(
        db.Text,
        nullable=True
    )

    recebeu_copia_documentos_admissao = db.Column(
        db.String(20),
        nullable=True
    )

    carteira_trabalho_assinada = db.Column(
        db.String(20),
        nullable=True
    )

    carteira_assinada_mesmo_dia = db.Column(
        db.String(20),
        nullable=True
    )

    carteira_dias_apos_inicio = db.Column(
        db.Integer,
        nullable=True
    )

    carteira_nunca_assinada = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_treinamento = db.Column(
        db.String(20),
        nullable=True
    )

    treinamento_duracao = db.Column(
        db.String(100),
        nullable=True
    )

    recebeu_uniforme = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_epi = db.Column(
        db.String(20),
        nullable=True
    )

    epis_recebidos = db.Column(
        db.Text,
        nullable=True
    )

    assinou_ficha_entrega_epi = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_admissao = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 4. CONTRATO DE TRABALHO
    # =====================================
    tipo_contrato = db.Column(
        db.String(30),
        nullable=True
    )

    tipo_contrato_outro = db.Column(
        db.String(150),
        nullable=True
    )

    contrato_experiencia_prorrogado = db.Column(
        db.String(20),
        nullable=True
    )

    quantidade_prorrogacoes_experiencia = db.Column(
        db.Integer,
        nullable=True
    )

    cargo_registrado_carteira = db.Column(
        db.String(150),
        nullable=True
    )

    funcao_real_exercida = db.Column(
        db.Text,
        nullable=True
    )

    exercia_mais_uma_funcao = db.Column(
        db.String(20),
        nullable=True
    )

    funcoes_acumuladas = db.Column(
        db.Text,
        nullable=True
    )

    recebeu_promocao = db.Column(
        db.String(20),
        nullable=True
    )

    promocao_qual = db.Column(
        db.String(150),
        nullable=True
    )

    possui_documento_promocao = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_aumento_promocao = db.Column(
        db.String(20),
        nullable=True
    )

    mudou_setor = db.Column(
        db.String(20),
        nullable=True
    )

    quantidade_mudancas_setor = db.Column(
        db.Integer,
        nullable=True
    )

    setores_trabalhados = db.Column(
        db.Text,
        nullable=True
    )

    mudou_cidade = db.Column(
        db.String(20),
        nullable=True
    )

    cidades_trabalhadas = db.Column(
        db.Text,
        nullable=True
    )

    recebeu_adicional_transferencia = db.Column(
        db.String(20),
        nullable=True
    )

    exerceu_funcao_superior_sem_aumento = db.Column(
        db.String(20),
        nullable=True
    )

    funcao_superior_exercida = db.Column(
        db.String(150),
        nullable=True
    )

    substituia_gerente_superior = db.Column(
        db.String(20),
        nullable=True
    )

    substituia_gerente_detalhes = db.Column(
        db.Text,
        nullable=True
    )

    substituia_colegas_afastados = db.Column(
        db.String(20),
        nullable=True
    )

    substituicao_colegas_tempo = db.Column(
        db.String(100),
        nullable=True
    )

    descricao_rotina_trabalho = db.Column(
        db.Text,
        nullable=True
    )

    assinou_outro_contrato_admissao = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_copia_outro_contrato = db.Column(
        db.String(20),
        nullable=True
    )

    assinou_outros_documentos_branco = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_contrato = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 5. LOCAL DE TRABALHO
    # =====================================
    trabalhava_mesmo_local = db.Column(
        db.String(20),
        nullable=True
    )

    locais_trabalho = db.Column(
        db.Text,
        nullable=True
    )

    trabalhava_em_obras = db.Column(
        db.String(20),
        nullable=True
    )

    obras_locais = db.Column(
        db.Text,
        nullable=True
    )

    trabalhava_viajando = db.Column(
        db.String(20),
        nullable=True
    )

    locais_viagens = db.Column(
        db.Text,
        nullable=True
    )

    dormia_fora_casa = db.Column(
        db.String(20),
        nullable=True
    )

    recebia_diarias = db.Column(
        db.String(20),
        nullable=True
    )

    valor_diarias = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    recebia_hospedagem = db.Column(
        db.String(20),
        nullable=True
    )

    recebia_alimentacao = db.Column(
        db.String(20),
        nullable=True
    )

    usava_veiculo_proprio = db.Column(
        db.String(20),
        nullable=True
    )

    veiculo_proprio_descricao = db.Column(
        db.String(150),
        nullable=True
    )

    recebia_reembolso_veiculo = db.Column(
        db.String(20),
        nullable=True
    )

    valor_reembolso_veiculo = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    utilizava_celular_particular = db.Column(
        db.String(20),
        nullable=True
    )

    recebia_ajuda_internet_telefone = db.Column(
        db.String(20),
        nullable=True
    )

    valor_ajuda_internet_telefone = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    observacoes_local_trabalho = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 6. SALÁRIO
    # =====================================
    salario_registrado = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    salario_real = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    recebia_valor_extrafolha = db.Column(
        db.String(20),
        nullable=True
    )

    valor_extrafolha_mensal = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    responsavel_pagamento_extrafolha = db.Column(
        db.String(150),
        nullable=True
    )

    forma_pagamento_extrafolha = db.Column(
        db.String(30),
        nullable=True
    )

    forma_pagamento_extrafolha_outro = db.Column(
        db.String(100),
        nullable=True
    )

    recebia_gorjetas = db.Column(
        db.String(20),
        nullable=True
    )

    valor_medio_gorjetas = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    gorjetas_constavam_contracheque = db.Column(
        db.String(20),
        nullable=True
    )

    gorjetas_divididas_empregados = db.Column(
        db.String(20),
        nullable=True
    )

    forma_divisao_gorjetas = db.Column(
        db.Text,
        nullable=True
    )

    pagamento_quinto_dia_util = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_salario = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 7. FÉRIAS
    # =====================================
    recebeu_ferias_todos_anos = db.Column(
        db.String(20),
        nullable=True
    )

    quantidade_periodos_ferias = db.Column(
        db.Integer,
        nullable=True
    )

    datas_periodos_ferias = db.Column(
        db.Text,
        nullable=True
    )

    data_pagamento_ferias = db.Column(
        db.String(100),
        nullable=True
    )

    momento_pagamento_ferias = db.Column(
        db.String(40),
        nullable=True
    )

    recebeu_um_terco_ferias = db.Column(
        db.String(20),
        nullable=True
    )

    vendia_ferias = db.Column(
        db.String(20),
        nullable=True
    )

    era_obrigado_vender_ferias = db.Column(
        db.String(20),
        nullable=True
    )

    trabalhou_durante_ferias = db.Column(
        db.String(20),
        nullable=True
    )

    assinava_ponto_durante_ferias = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_ferias = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 8. DÉCIMO TERCEIRO
    # =====================================
    recebia_decimo_terceiro = db.Column(
        db.String(20),
        nullable=True
    )

    recebia_decimo_terceiro_corretamente = db.Column(
        db.String(20),
        nullable=True
    )

    recebia_decimo_terceiro_duas_parcelas = db.Column(
        db.String(20),
        nullable=True
    )

    data_aproximada_primeira_parcela = db.Column(
        db.String(100),
        nullable=True
    )

    data_aproximada_segunda_parcela = db.Column(
        db.String(100),
        nullable=True
    )

    possui_contracheque_decimo_terceiro = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_decimo_terceiro = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # 9. RESCISÃO
    # =====================================
    recebeu_extrato_fgts_rescisao = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_comprovante_multa_fgts = db.Column(
        db.String(20),
        nullable=True
    )

    multa_fgts_creditada = db.Column(
        db.String(20),
        nullable=True
    )

    data_demissao = db.Column(
        db.Date,
        nullable=True
    )

    tipo_rescisao = db.Column(
        db.String(100),
        nullable=True
    )

    recebeu_verbas_rescisorias = db.Column(
        db.String(20),
        nullable=True
    )

    data_pagamento_rescisao = db.Column(
        db.Date,
        nullable=True
    )

    assinou_termo_rescisao = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_copia_termo_rescisao = db.Column(
        db.String(20),
        nullable=True
    )

    recebeu_guias_seguro_desemprego = db.Column(
        db.String(20),
        nullable=True
    )

    realizou_exame_demissional = db.Column(
        db.String(20),
        nullable=True
    )

    observacoes_rescisao = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================
    # OBSERVAÇÕES GERAIS
    # =====================================
    observacoes_gerais = db.Column(
        db.Text,
        nullable=True
    )

    documentos_pendentes = db.Column(
        db.Text,
        nullable=True
    )

    avaliacao_google_solicitada = db.Column(
        db.Boolean,
        nullable=False,
        default=False
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
            "fichas_trabalhistas_criadas",
            lazy=True
        )
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "fichas_trabalhistas_atualizadas",
            lazy=True
        )
    )

    # =====================================
    # RELACIONAMENTO COM ATENDIMENTO
    # =====================================
    atendimento = db.relationship(
        "Atendimento",
        back_populates="ficha_trabalhista"
    )

    # =====================================
    # PROPRIEDADES
    # =====================================
    @property
    def cliente(self):
        if self.atendimento:
            return self.atendimento.cliente

        return None

    @property
    def escolaridade_nome(self):
        if not self.escolaridade:
            return "Não informado"

        if (
            self.escolaridade == self.ESCOLARIDADE_OUTRA
            and self.escolaridade_outro
        ):
            return self.escolaridade_outro

        return self.ESCOLARIDADES.get(
            self.escolaridade,
            "Não informado"
        )

    @property
    def tipo_contrato_nome(self):
        if not self.tipo_contrato:
            return "Não informado"

        if (
            self.tipo_contrato == self.CONTRATO_OUTRO
            and self.tipo_contrato_outro
        ):
            return self.tipo_contrato_outro

        return self.TIPOS_CONTRATO.get(
            self.tipo_contrato,
            "Não informado"
        )

    @classmethod
    def resposta_nome(cls, valor):
        if not valor:
            return "Não informado"

        return cls.RESPOSTAS.get(
            valor,
            "Não informado"
        )

    @property
    def possui_filhos_menores_nome(self):
        return self.resposta_nome(
            self.possui_filhos_menores
        )

    @property
    def possui_deficiencia_nome(self):
        return self.resposta_nome(
            self.possui_deficiencia
        )

    @property
    def recebeu_beneficio_inss_nome(self):
        return self.resposta_nome(
            self.recebeu_beneficio_inss
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
            self.etapa_empresa_concluida,
            self.etapa_admissao_concluida,
            self.etapa_contrato_concluida,
            self.etapa_local_concluida,
            self.etapa_salario_concluida,
            self.etapa_ferias_concluida,
            self.etapa_decimo_terceiro_concluida,
            self.etapa_rescisao_concluida
        ]

        concluidas = sum(
            1 for etapa in etapas if etapa
        )

        return int(
            concluidas / len(etapas) * 100
        )

    # =====================================
    # REPRESENTAÇÃO
    # =====================================
    def __repr__(self):
        return (
            f"<FichaTrabalhista "
            f"id={self.id} "
            f"atendimento_id={self.atendimento_id} "
            f"etapa_atual={self.etapa_atual}>"
        )