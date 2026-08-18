from datetime import datetime

from . import db


class FichaPrevidenciaria(db.Model):
    __tablename__ = "fichas_previdenciarias"

    # ============================================================
    # RESPOSTAS PADRONIZADAS
    # ============================================================

    RESPOSTA_SIM = "SIM"
    RESPOSTA_NAO = "NAO"
    RESPOSTA_NAO_SABE = "NAO_SABE"
    RESPOSTA_NAO_RECORDA = "NAO_RECORDA"
    RESPOSTA_NAO_SE_APLICA = "NAO_SE_APLICA"

    RESPOSTAS = {
        RESPOSTA_SIM: "Sim",
        RESPOSTA_NAO: "Não",
        RESPOSTA_NAO_SABE: "Não sabe informar",
        RESPOSTA_NAO_RECORDA: "Não se recorda",
        RESPOSTA_NAO_SE_APLICA: "Não se aplica",
    }

    # ============================================================
    # ESCOLARIDADE
    # ============================================================

    ESCOLARIDADE_NAO_ALFABETIZADO = "NAO_ALFABETIZADO"
    ESCOLARIDADE_FUNDAMENTAL_INCOMPLETO = "FUNDAMENTAL_INCOMPLETO"
    ESCOLARIDADE_FUNDAMENTAL_COMPLETO = "FUNDAMENTAL_COMPLETO"
    ESCOLARIDADE_MEDIO_INCOMPLETO = "MEDIO_INCOMPLETO"
    ESCOLARIDADE_MEDIO_COMPLETO = "MEDIO_COMPLETO"
    ESCOLARIDADE_TECNICO = "TECNICO"
    ESCOLARIDADE_SUPERIOR_INCOMPLETO = "SUPERIOR_INCOMPLETO"
    ESCOLARIDADE_SUPERIOR_COMPLETO = "SUPERIOR_COMPLETO"
    ESCOLARIDADE_POS_GRADUACAO = "POS_GRADUACAO"
    ESCOLARIDADE_OUTRA = "OUTRA"

    ESCOLARIDADES = {
        ESCOLARIDADE_NAO_ALFABETIZADO: "Não alfabetizado",
        ESCOLARIDADE_FUNDAMENTAL_INCOMPLETO: (
            "Ensino Fundamental incompleto"
        ),
        ESCOLARIDADE_FUNDAMENTAL_COMPLETO: (
            "Ensino Fundamental completo"
        ),
        ESCOLARIDADE_MEDIO_INCOMPLETO: "Ensino Médio incompleto",
        ESCOLARIDADE_MEDIO_COMPLETO: "Ensino Médio completo",
        ESCOLARIDADE_TECNICO: "Ensino Técnico",
        ESCOLARIDADE_SUPERIOR_INCOMPLETO: (
            "Ensino Superior incompleto"
        ),
        ESCOLARIDADE_SUPERIOR_COMPLETO: "Ensino Superior completo",
        ESCOLARIDADE_POS_GRADUACAO: "Pós-graduação",
        ESCOLARIDADE_OUTRA: "Outra",
    }

    # ============================================================
    # CATEGORIAS DO SEGURADO
    # ============================================================

    CATEGORIA_EMPREGADO = "EMPREGADO"
    CATEGORIA_EMPREGADO_DOMESTICO = "EMPREGADO_DOMESTICO"
    CATEGORIA_CONTRIBUINTE_INDIVIDUAL = "CONTRIBUINTE_INDIVIDUAL"
    CATEGORIA_SEGURADO_FACULTATIVO = "SEGURADO_FACULTATIVO"
    CATEGORIA_SEGURADO_ESPECIAL = "SEGURADO_ESPECIAL"
    CATEGORIA_TRABALHADOR_AVULSO = "TRABALHADOR_AVULSO"
    CATEGORIA_SERVIDOR_PUBLICO = "SERVIDOR_PUBLICO"
    CATEGORIA_MILITAR = "MILITAR"
    CATEGORIA_SEM_FILIACAO = "SEM_FILIACAO"
    CATEGORIA_OUTRA = "OUTRA"

    CATEGORIAS_SEGURADO = {
        CATEGORIA_EMPREGADO: "Empregado",
        CATEGORIA_EMPREGADO_DOMESTICO: "Empregado doméstico",
        CATEGORIA_CONTRIBUINTE_INDIVIDUAL: (
            "Contribuinte individual"
        ),
        CATEGORIA_SEGURADO_FACULTATIVO: "Segurado facultativo",
        CATEGORIA_SEGURADO_ESPECIAL: "Segurado especial",
        CATEGORIA_TRABALHADOR_AVULSO: "Trabalhador avulso",
        CATEGORIA_SERVIDOR_PUBLICO: "Servidor público",
        CATEGORIA_MILITAR: "Militar",
        CATEGORIA_SEM_FILIACAO: "Sem filiação previdenciária",
        CATEGORIA_OUTRA: "Outra",
    }

    # ============================================================
    # SITUAÇÃO PROFISSIONAL
    # ============================================================

    SITUACAO_TRABALHANDO = "TRABALHANDO"
    SITUACAO_DESEMPREGADO = "DESEMPREGADO"
    SITUACAO_AFASTADO = "AFASTADO"
    SITUACAO_APOSENTADO = "APOSENTADO"
    SITUACAO_RECEBENDO_BENEFICIO = "RECEBENDO_BENEFICIO"
    SITUACAO_SEM_ATIVIDADE = "SEM_ATIVIDADE"
    SITUACAO_OUTRA = "OUTRA"

    SITUACOES_PROFISSIONAIS = {
        SITUACAO_TRABALHANDO: "Trabalhando",
        SITUACAO_DESEMPREGADO: "Desempregado",
        SITUACAO_AFASTADO: "Afastado do trabalho",
        SITUACAO_APOSENTADO: "Aposentado",
        SITUACAO_RECEBENDO_BENEFICIO: "Recebendo benefício",
        SITUACAO_SEM_ATIVIDADE: "Sem atividade profissional",
        SITUACAO_OUTRA: "Outra",
    }

    # ============================================================
    # TIPOS DE BENEFÍCIO
    # ============================================================

    BENEFICIO_APOSENTADORIA_IDADE = "APOSENTADORIA_IDADE"
    BENEFICIO_APOSENTADORIA_TEMPO = "APOSENTADORIA_TEMPO"
    BENEFICIO_APOSENTADORIA_ESPECIAL = "APOSENTADORIA_ESPECIAL"
    BENEFICIO_APOSENTADORIA_RURAL = "APOSENTADORIA_RURAL"
    BENEFICIO_APOSENTADORIA_PCD = "APOSENTADORIA_PCD"
    BENEFICIO_INCAPACIDADE_TEMPORARIA = "INCAPACIDADE_TEMPORARIA"
    BENEFICIO_INCAPACIDADE_PERMANENTE = "INCAPACIDADE_PERMANENTE"
    BENEFICIO_AUXILIO_ACIDENTE = "AUXILIO_ACIDENTE"
    BENEFICIO_PENSAO_MORTE = "PENSAO_MORTE"
    BENEFICIO_SALARIO_MATERNIDADE = "SALARIO_MATERNIDADE"
    BENEFICIO_AUXILIO_RECLUSAO = "AUXILIO_RECLUSAO"
    BENEFICIO_BPC_IDOSO = "BPC_IDOSO"
    BENEFICIO_BPC_PCD = "BPC_PCD"
    BENEFICIO_REVISAO = "REVISAO"
    BENEFICIO_PLANEJAMENTO = "PLANEJAMENTO"
    BENEFICIO_RECURSO = "RECURSO"
    BENEFICIO_OUTRO = "OUTRO"

    TIPOS_BENEFICIO = {
        BENEFICIO_APOSENTADORIA_IDADE: "Aposentadoria por idade",
        BENEFICIO_APOSENTADORIA_TEMPO: (
            "Aposentadoria por tempo de contribuição"
        ),
        BENEFICIO_APOSENTADORIA_ESPECIAL: (
            "Aposentadoria especial"
        ),
        BENEFICIO_APOSENTADORIA_RURAL: "Aposentadoria rural",
        BENEFICIO_APOSENTADORIA_PCD: (
            "Aposentadoria da pessoa com deficiência"
        ),
        BENEFICIO_INCAPACIDADE_TEMPORARIA: (
            "Benefício por incapacidade temporária"
        ),
        BENEFICIO_INCAPACIDADE_PERMANENTE: (
            "Aposentadoria por incapacidade permanente"
        ),
        BENEFICIO_AUXILIO_ACIDENTE: "Auxílio-acidente",
        BENEFICIO_PENSAO_MORTE: "Pensão por morte",
        BENEFICIO_SALARIO_MATERNIDADE: "Salário-maternidade",
        BENEFICIO_AUXILIO_RECLUSAO: "Auxílio-reclusão",
        BENEFICIO_BPC_IDOSO: "BPC/LOAS para pessoa idosa",
        BENEFICIO_BPC_PCD: "BPC/LOAS para pessoa com deficiência",
        BENEFICIO_REVISAO: "Revisão de benefício",
        BENEFICIO_PLANEJAMENTO: "Planejamento previdenciário",
        BENEFICIO_RECURSO: "Recurso administrativo",
        BENEFICIO_OUTRO: "Outro",
    }

    # ============================================================
    # INCAPACIDADE
    # ============================================================

    INCAPACIDADE_NAO_INFORMADA = "NAO_INFORMADA"
    INCAPACIDADE_INEXISTENTE = "INEXISTENTE"
    INCAPACIDADE_PARCIAL_TEMPORARIA = "PARCIAL_TEMPORARIA"
    INCAPACIDADE_PARCIAL_PERMANENTE = "PARCIAL_PERMANENTE"
    INCAPACIDADE_TOTAL_TEMPORARIA = "TOTAL_TEMPORARIA"
    INCAPACIDADE_TOTAL_PERMANENTE = "TOTAL_PERMANENTE"

    TIPOS_INCAPACIDADE = {
        INCAPACIDADE_NAO_INFORMADA: "Ainda não avaliada",
        INCAPACIDADE_INEXISTENTE: "Não há incapacidade",
        INCAPACIDADE_PARCIAL_TEMPORARIA: (
            "Parcial e temporária"
        ),
        INCAPACIDADE_PARCIAL_PERMANENTE: (
            "Parcial e permanente"
        ),
        INCAPACIDADE_TOTAL_TEMPORARIA: "Total e temporária",
        INCAPACIDADE_TOTAL_PERMANENTE: "Total e permanente",
    }

    # ============================================================
    # ORIGEM DA DOENÇA OU INCAPACIDADE
    # ============================================================

    ORIGEM_COMUM = "COMUM"
    ORIGEM_ACIDENTE_TRABALHO = "ACIDENTE_TRABALHO"
    ORIGEM_DOENCA_OCUPACIONAL = "DOENCA_OCUPACIONAL"
    ORIGEM_ACIDENTE_TRANSITO = "ACIDENTE_TRANSITO"
    ORIGEM_ACIDENTE_DOMESTICO = "ACIDENTE_DOMESTICO"
    ORIGEM_OUTRA = "OUTRA"
    ORIGEM_NAO_INFORMADA = "NAO_INFORMADA"

    ORIGENS_INCAPACIDADE = {
        ORIGEM_COMUM: "Doença comum",
        ORIGEM_ACIDENTE_TRABALHO: "Acidente de trabalho",
        ORIGEM_DOENCA_OCUPACIONAL: "Doença ocupacional",
        ORIGEM_ACIDENTE_TRANSITO: "Acidente de trânsito",
        ORIGEM_ACIDENTE_DOMESTICO: "Acidente doméstico",
        ORIGEM_OUTRA: "Outra origem",
        ORIGEM_NAO_INFORMADA: "Não informada",
    }

    # ============================================================
    # SITUAÇÃO DO REQUERIMENTO NO INSS
    # ============================================================

    INSS_NAO_REQUERIDO = "NAO_REQUERIDO"
    INSS_AGUARDANDO_ANALISE = "AGUARDANDO_ANALISE"
    INSS_EM_ANALISE = "EM_ANALISE"
    INSS_EXIGENCIA = "EXIGENCIA"
    INSS_PERICIA_AGENDADA = "PERICIA_AGENDADA"
    INSS_DEFERIDO = "DEFERIDO"
    INSS_INDEFERIDO = "INDEFERIDO"
    INSS_RECURSO = "RECURSO"
    INSS_JUDICIALIZADO = "JUDICIALIZADO"
    INSS_ARQUIVADO = "ARQUIVADO"

    SITUACOES_INSS = {
        INSS_NAO_REQUERIDO: "Ainda não requerido",
        INSS_AGUARDANDO_ANALISE: "Aguardando análise",
        INSS_EM_ANALISE: "Em análise",
        INSS_EXIGENCIA: "Exigência aberta",
        INSS_PERICIA_AGENDADA: "Perícia agendada",
        INSS_DEFERIDO: "Deferido",
        INSS_INDEFERIDO: "Indeferido",
        INSS_RECURSO: "Em recurso administrativo",
        INSS_JUDICIALIZADO: "Judicializado",
        INSS_ARQUIVADO: "Arquivado",
    }

    # ============================================================
    # RESULTADOS DA PERÍCIA
    # ============================================================

    PERICIA_NAO_REALIZADA = "NAO_REALIZADA"
    PERICIA_FAVORAVEL = "FAVORAVEL"
    PERICIA_DESFAVORAVEL = "DESFAVORAVEL"
    PERICIA_INCONCLUSIVA = "INCONCLUSIVA"
    PERICIA_AGUARDANDO_RESULTADO = "AGUARDANDO_RESULTADO"

    RESULTADOS_PERICIA = {
        PERICIA_NAO_REALIZADA: "Não realizada",
        PERICIA_FAVORAVEL: "Favorável",
        PERICIA_DESFAVORAVEL: "Desfavorável",
        PERICIA_INCONCLUSIVA: "Inconclusiva",
        PERICIA_AGUARDANDO_RESULTADO: "Aguardando resultado",
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
        db.String(50),
        nullable=False,
        default="atendimento",
    )

    etapa_atendimento_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_segurado_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_historico_contributivo_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_beneficio_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_saude_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_documentacao_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_inss_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_resumo_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # ============================================================
    # 1. DADOS DO SEGURADO
    # ============================================================

    nit_pis_pasep = db.Column(
        db.String(30),
        nullable=True,
        index=True,
    )

    rg = db.Column(
        db.String(30),
        nullable=True,
    )

    orgao_expedidor = db.Column(
        db.String(30),
        nullable=True,
    )

    escolaridade = db.Column(
        db.String(40),
        nullable=True,
    )

    escolaridade_outro = db.Column(
        db.String(120),
        nullable=True,
    )

    profissao = db.Column(
        db.String(150),
        nullable=True,
    )

    ocupacao_atual = db.Column(
        db.String(150),
        nullable=True,
    )

    categoria_segurado = db.Column(
        db.String(40),
        nullable=True,
    )

    categoria_segurado_outro = db.Column(
        db.String(150),
        nullable=True,
    )

    situacao_profissional = db.Column(
        db.String(40),
        nullable=True,
    )

    situacao_profissional_outro = db.Column(
        db.String(150),
        nullable=True,
    )

    data_ultimo_trabalho = db.Column(
        db.Date,
        nullable=True,
    )

    possui_dependentes = db.Column(
        db.String(20),
        nullable=True,
    )

    quantidade_dependentes = db.Column(
        db.Integer,
        nullable=True,
    )

    dependentes_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_deficiencia = db.Column(
        db.String(20),
        nullable=True,
    )

    tipo_deficiencia = db.Column(
        db.String(150),
        nullable=True,
    )

    data_inicio_deficiencia = db.Column(
        db.Date,
        nullable=True,
    )

    observacoes_segurado = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 2. HISTÓRICO CONTRIBUTIVO
    # ============================================================

    possui_cnis = db.Column(
        db.String(20),
        nullable=True,
    )

    cnis_atualizado = db.Column(
        db.String(20),
        nullable=True,
    )

    data_emissao_cnis = db.Column(
        db.Date,
        nullable=True,
    )

    possui_vinculos_ausentes_cnis = db.Column(
        db.String(20),
        nullable=True,
    )

    vinculos_ausentes_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_contribuicoes_abaixo_minimo = db.Column(
        db.String(20),
        nullable=True,
    )

    contribuicoes_abaixo_minimo_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_contribuicoes_em_atraso = db.Column(
        db.String(20),
        nullable=True,
    )

    contribuicoes_em_atraso_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_periodo_rural = db.Column(
        db.String(20),
        nullable=True,
    )

    periodo_rural_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_atividade_especial = db.Column(
        db.String(20),
        nullable=True,
    )

    atividade_especial_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_tempo_servico_publico = db.Column(
        db.String(20),
        nullable=True,
    )

    tempo_servico_publico_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_tempo_militar = db.Column(
        db.String(20),
        nullable=True,
    )

    tempo_militar_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    tempo_contribuicao_estimado = db.Column(
        db.String(100),
        nullable=True,
    )

    carencia_estimada = db.Column(
        db.Integer,
        nullable=True,
    )

    observacoes_historico_contributivo = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 3. BENEFÍCIO PRETENDIDO
    # ============================================================

    beneficio_principal = db.Column(
        db.String(50),
        nullable=True,
    )

    beneficio_principal_outro = db.Column(
        db.String(180),
        nullable=True,
    )

    beneficio_alternativo = db.Column(
        db.String(50),
        nullable=True,
    )

    beneficio_alternativo_outro = db.Column(
        db.String(180),
        nullable=True,
    )

    objetivo_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    motivo_pedido = db.Column(
        db.Text,
        nullable=True,
    )

    possui_qualidade_segurado = db.Column(
        db.String(20),
        nullable=True,
    )

    qualidade_segurado_observacoes = db.Column(
        db.Text,
        nullable=True,
    )

    carencia_cumprida = db.Column(
        db.String(20),
        nullable=True,
    )

    carencia_observacoes = db.Column(
        db.Text,
        nullable=True,
    )

    possui_direito_adquirido = db.Column(
        db.String(20),
        nullable=True,
    )

    direito_adquirido_observacoes = db.Column(
        db.Text,
        nullable=True,
    )

    aplica_regra_transicao = db.Column(
        db.String(20),
        nullable=True,
    )

    regra_transicao_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    data_prevista_beneficio = db.Column(
        db.Date,
        nullable=True,
    )

    renda_mensal_estimada = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    observacoes_beneficio = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 4. SAÚDE E INCAPACIDADE
    # ============================================================

    possui_doenca_incapacidade = db.Column(
        db.String(20),
        nullable=True,
    )

    diagnostico_principal = db.Column(
        db.String(255),
        nullable=True,
    )

    cid_principal = db.Column(
        db.String(30),
        nullable=True,
    )

    outros_diagnosticos = db.Column(
        db.Text,
        nullable=True,
    )

    data_inicio_doenca = db.Column(
        db.Date,
        nullable=True,
    )

    data_inicio_incapacidade = db.Column(
        db.Date,
        nullable=True,
    )

    tipo_incapacidade = db.Column(
        db.String(40),
        nullable=True,
    )

    origem_incapacidade = db.Column(
        db.String(40),
        nullable=True,
    )

    origem_incapacidade_outro = db.Column(
        db.String(180),
        nullable=True,
    )

    atividade_prejudicada = db.Column(
        db.String(180),
        nullable=True,
    )

    limitacoes_funcionais = db.Column(
        db.Text,
        nullable=True,
    )

    realiza_tratamento = db.Column(
        db.String(20),
        nullable=True,
    )

    tratamento_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    nome_medico_assistente = db.Column(
        db.String(180),
        nullable=True,
    )

    especialidade_medico = db.Column(
        db.String(120),
        nullable=True,
    )

    possui_laudo_medico = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_exames = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_receitas = db.Column(
        db.String(20),
        nullable=True,
    )

    houve_acidente = db.Column(
        db.String(20),
        nullable=True,
    )

    data_acidente = db.Column(
        db.Date,
        nullable=True,
    )

    acidente_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_cat = db.Column(
        db.String(20),
        nullable=True,
    )

    observacoes_saude = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 5. DOCUMENTAÇÃO
    # ============================================================

    documento_rg = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_cpf = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_comprovante_residencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_cnis = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_ctps = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_carnes_contribuicao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_guias_gps = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_ppp = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_ltcat = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_certidao_tempo_contribuicao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_laudos_medicos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_exames_medicos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_processo_inss = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_carta_indeferimento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documento_procuracao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    documentos_outros = db.Column(
        db.Text,
        nullable=True,
    )

    documentos_pendentes = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_documentacao = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 6. PROCESSO ADMINISTRATIVO NO INSS
    # ============================================================

    possui_requerimento_inss = db.Column(
        db.String(20),
        nullable=True,
    )

    numero_protocolo = db.Column(
        db.String(100),
        nullable=True,
        index=True,
    )

    numero_beneficio = db.Column(
        db.String(100),
        nullable=True,
        index=True,
    )

    data_entrada_requerimento = db.Column(
        db.Date,
        nullable=True,
    )

    data_inicio_beneficio = db.Column(
        db.Date,
        nullable=True,
    )

    agencia_previdencia_social = db.Column(
        db.String(200),
        nullable=True,
    )

    cidade_agencia = db.Column(
        db.String(120),
        nullable=True,
    )

    situacao_requerimento = db.Column(
        db.String(40),
        nullable=True,
    )

    possui_exigencia = db.Column(
        db.String(20),
        nullable=True,
    )

    data_limite_exigencia = db.Column(
        db.Date,
        nullable=True,
    )

    exigencia_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    possui_pericia = db.Column(
        db.String(20),
        nullable=True,
    )

    data_pericia = db.Column(
        db.Date,
        nullable=True,
    )

    horario_pericia = db.Column(
        db.Time,
        nullable=True,
    )

    local_pericia = db.Column(
        db.String(200),
        nullable=True,
    )

    resultado_pericia = db.Column(
        db.String(40),
        nullable=True,
    )

    resultado_pericia_descricao = db.Column(
        db.Text,
        nullable=True,
    )

    data_decisao_inss = db.Column(
        db.Date,
        nullable=True,
    )

    motivo_indeferimento = db.Column(
        db.Text,
        nullable=True,
    )

    possui_recurso = db.Column(
        db.String(20),
        nullable=True,
    )

    numero_recurso = db.Column(
        db.String(100),
        nullable=True,
    )

    data_recurso = db.Column(
        db.Date,
        nullable=True,
    )

    resultado_recurso = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_inss = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # 7. RESUMO E ANÁLISE JURÍDICA
    # ============================================================

    resumo_previdenciario = db.Column(
        db.Text,
        nullable=True,
    )

    analise_juridica = db.Column(
        db.Text,
        nullable=True,
    )

    estrategia_sugerida = db.Column(
        db.Text,
        nullable=True,
    )

    riscos_identificados = db.Column(
        db.Text,
        nullable=True,
    )

    providencias_recomendadas = db.Column(
        db.Text,
        nullable=True,
    )

    pendencias_gerais = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_gerais = db.Column(
        db.Text,
        nullable=True,
    )

    ficha_finalizada = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    data_finalizacao = db.Column(
        db.DateTime,
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
            "fichas_previdenciarias_criadas",
            lazy=True,
        ),
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "fichas_previdenciarias_atualizadas",
            lazy=True,
        ),
    )

    # ============================================================
    # RELACIONAMENTO COM O ATENDIMENTO
    # ============================================================

    atendimento = db.relationship(
        "Atendimento",
        back_populates=
            "ficha_previdenciaria",
     )

    # ============================================================
    # HISTÓRICO CONTRIBUTIVO
    # ============================================================

    periodos_contributivos = db.relationship(
        "PeriodoContributivo",
        back_populates="ficha",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="PeriodoContributivo.data_inicio.asc()",
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
            "Não informado",
        )

    @property
    def categoria_segurado_nome(self):
        if not self.categoria_segurado:
            return "Não informado"

        if (
            self.categoria_segurado == self.CATEGORIA_OUTRA
            and self.categoria_segurado_outro
        ):
            return self.categoria_segurado_outro

        return self.CATEGORIAS_SEGURADO.get(
            self.categoria_segurado,
            "Não informado",
        )

    @property
    def situacao_profissional_nome(self):
        if not self.situacao_profissional:
            return "Não informado"

        if (
            self.situacao_profissional == self.SITUACAO_OUTRA
            and self.situacao_profissional_outro
        ):
            return self.situacao_profissional_outro

        return self.SITUACOES_PROFISSIONAIS.get(
            self.situacao_profissional,
            "Não informado",
        )

    @classmethod
    def beneficio_nome(cls, valor, outro=None):
        if not valor:
            return "Não informado"

        if valor == cls.BENEFICIO_OUTRO and outro:
            return outro

        return cls.TIPOS_BENEFICIO.get(
            valor,
            "Não informado",
        )

    @property
    def beneficio_principal_nome(self):
        return self.beneficio_nome(
            self.beneficio_principal,
            self.beneficio_principal_outro,
        )

    @property
    def beneficio_alternativo_nome(self):
        return self.beneficio_nome(
            self.beneficio_alternativo,
            self.beneficio_alternativo_outro,
        )

    @property
    def tipo_incapacidade_nome(self):
        if not self.tipo_incapacidade:
            return "Não informado"

        return self.TIPOS_INCAPACIDADE.get(
            self.tipo_incapacidade,
            "Não informado",
        )

    @property
    def origem_incapacidade_nome(self):
        if not self.origem_incapacidade:
            return "Não informado"

        if (
            self.origem_incapacidade == self.ORIGEM_OUTRA
            and self.origem_incapacidade_outro
        ):
            return self.origem_incapacidade_outro

        return self.ORIGENS_INCAPACIDADE.get(
            self.origem_incapacidade,
            "Não informado",
        )

    @property
    def situacao_requerimento_nome(self):
        if not self.situacao_requerimento:
            return "Não informado"

        return self.SITUACOES_INSS.get(
            self.situacao_requerimento,
            "Não informado",
        )

    @property
    def resultado_pericia_nome(self):
        if not self.resultado_pericia:
            return "Não informado"

        return self.RESULTADOS_PERICIA.get(
            self.resultado_pericia,
            "Não informado",
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
            self.etapa_segurado_concluida,
            self.etapa_historico_contributivo_concluida,
            self.etapa_beneficio_concluida,
            self.etapa_saude_concluida,
            self.etapa_documentacao_concluida,
            self.etapa_inss_concluida,
            self.etapa_resumo_concluida,
        ]

        concluidas = sum(
            1
            for etapa in etapas
            if etapa
        )

        if not etapas:
            return 0

        return int(
            concluidas / len(etapas) * 100
        )

    def __repr__(self):
        return (
            f"<FichaPrevidenciaria "
            f"id={self.id} "
            f"atendimento_id={self.atendimento_id} "
            f"etapa_atual={self.etapa_atual}>"
        )


class PeriodoContributivo(db.Model):
    __tablename__ = "periodos_contributivos"

    # ============================================================
    # TIPOS DE VÍNCULO
    # ============================================================

    VINCULO_EMPREGADO = "EMPREGADO"
    VINCULO_EMPREGADO_DOMESTICO = "EMPREGADO_DOMESTICO"
    VINCULO_CONTRIBUINTE_INDIVIDUAL = "CONTRIBUINTE_INDIVIDUAL"
    VINCULO_FACULTATIVO = "FACULTATIVO"
    VINCULO_SEGURADO_ESPECIAL = "SEGURADO_ESPECIAL"
    VINCULO_SERVIDOR_PUBLICO = "SERVIDOR_PUBLICO"
    VINCULO_MILITAR = "MILITAR"
    VINCULO_ATIVIDADE_RURAL = "ATIVIDADE_RURAL"
    VINCULO_ATIVIDADE_ESPECIAL = "ATIVIDADE_ESPECIAL"
    VINCULO_OUTRO = "OUTRO"

    TIPOS_VINCULO = {
        VINCULO_EMPREGADO: "Empregado",
        VINCULO_EMPREGADO_DOMESTICO: "Empregado doméstico",
        VINCULO_CONTRIBUINTE_INDIVIDUAL: "Contribuinte individual",
        VINCULO_FACULTATIVO: "Segurado facultativo",
        VINCULO_SEGURADO_ESPECIAL: "Segurado especial",
        VINCULO_SERVIDOR_PUBLICO: "Servidor público",
        VINCULO_MILITAR: "Militar",
        VINCULO_ATIVIDADE_RURAL: "Atividade rural",
        VINCULO_ATIVIDADE_ESPECIAL: "Atividade especial",
        VINCULO_OUTRO: "Outro",
    }

    # ============================================================
    # IDENTIFICAÇÃO
    # ============================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    ficha_previdenciaria_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "fichas_previdenciarias.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ============================================================
    # DADOS DO PERÍODO
    # ============================================================

    tipo_vinculo = db.Column(
        db.String(40),
        nullable=True,
    )

    tipo_vinculo_outro = db.Column(
        db.String(150),
        nullable=True,
    )

    empregador_nome = db.Column(
        db.String(200),
        nullable=True,
    )

    empregador_cnpj_cpf = db.Column(
        db.String(20),
        nullable=True,
    )

    cargo_atividade = db.Column(
        db.String(180),
        nullable=True,
    )

    data_inicio = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    data_fim = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    remuneracao_media = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    consta_no_cnis = db.Column(
        db.String(20),
        nullable=True,
    )

    consta_na_ctps = db.Column(
        db.String(20),
        nullable=True,
    )

    contribuicoes_regulares = db.Column(
        db.String(20),
        nullable=True,
    )

    contribuicoes_em_atraso = db.Column(
        db.String(20),
        nullable=True,
    )

    atividade_especial = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_ppp = db.Column(
        db.String(20),
        nullable=True,
    )

    possui_ltcat = db.Column(
        db.String(20),
        nullable=True,
    )

    tempo_rural = db.Column(
        db.String(20),
        nullable=True,
    )

    documentos_comprobatorios = db.Column(
        db.Text,
        nullable=True,
    )

    divergencias = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes = db.Column(
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
            "periodos_contributivos_criados",
            lazy=True,
        ),
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
        backref=db.backref(
            "periodos_contributivos_atualizados",
            lazy=True,
        ),
    )

    # ============================================================
    # RELACIONAMENTO
    # ============================================================

    ficha = db.relationship(
        "FichaPrevidenciaria",
        back_populates="periodos_contributivos",
    )

    # ============================================================
    # PROPRIEDADES
    # ============================================================

    @property
    def tipo_vinculo_nome(self):
        if not self.tipo_vinculo:
            return "Não informado"

        if (
            self.tipo_vinculo == self.VINCULO_OUTRO
            and self.tipo_vinculo_outro
        ):
            return self.tipo_vinculo_outro

        return self.TIPOS_VINCULO.get(
            self.tipo_vinculo,
            "Não informado",
        )

    @property
    def periodo_formatado(self):
        inicio = (
            self.data_inicio.strftime("%d/%m/%Y")
            if self.data_inicio
            else "Data inicial não informada"
        )

        fim = (
            self.data_fim.strftime("%d/%m/%Y")
            if self.data_fim
            else "Atual"
        )

        return f"{inicio} até {fim}"

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

    def __repr__(self):
        return (
            f"<PeriodoContributivo "
            f"id={self.id} "
            f"ficha_previdenciaria_id={self.ficha_previdenciaria_id} "
            f"tipo_vinculo={self.tipo_vinculo}>"
        )