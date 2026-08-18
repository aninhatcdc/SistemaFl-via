from datetime import datetime

from models import db


class FichaConsumidor(db.Model):
    __tablename__ = "fichas_consumidor"

    # ============================================================
    # OPÇÕES DOS CAMPOS
    # ============================================================

    TIPOS_DEMANDA = {
        "PRODUTO_DEFEITUOSO": "Produto com defeito",
        "VICIO_OCULTO": "Vício oculto",
        "PRODUTO_NAO_ENTREGUE": "Produto não entregue",
        "SERVICO_NAO_PRESTADO": "Serviço não prestado",
        "SERVICO_MAL_PRESTADO": "Serviço mal prestado",
        "COBRANCA_INDEVIDA": "Cobrança indevida",
        "NEGATIVACAO_INDEVIDA": "Negativação indevida",
        "PUBLICIDADE_ENGANOSA": "Publicidade enganosa",
        "DESCUMPRIMENTO_OFERTA": "Descumprimento de oferta",
        "CANCELAMENTO": "Cancelamento",
        "CONTRATO_ABUSIVO": "Contrato abusivo",
        "FRAUDE_BANCARIA": "Fraude bancária",
        "PIX": "Problema com Pix",
        "CARTAO_CREDITO": "Cartão de crédito",
        "EMPRESTIMO": "Empréstimo ou financiamento",
        "PLANO_SAUDE": "Plano de saúde",
        "TELEFONIA": "Telefonia",
        "INTERNET": "Internet",
        "ENERGIA": "Energia elétrica",
        "AGUA": "Fornecimento de água",
        "TRANSPORTE_AEREO": "Transporte aéreo",
        "SEGURO": "Seguro",
        "COMPRA_ONLINE": "Compra pela internet",
        "VEICULO": "Veículo",
        "IMOVEL": "Imóvel ou construtora",
        "OUTRA": "Outra demanda",
    }

    TIPOS_FORNECEDOR = {
        "EMPRESA_PRIVADA": "Empresa privada",
        "BANCO": "Banco ou instituição financeira",
        "PLANO_SAUDE": "Plano de saúde",
        "SEGURADORA": "Seguradora",
        "OPERADORA_TELEFONIA": "Operadora de telefonia",
        "CONCESSIONARIA": "Concessionária de serviço público",
        "COMPANHIA_AEREA": "Companhia aérea",
        "LOJA_FISICA": "Loja física",
        "LOJA_ONLINE": "Loja virtual",
        "PLATAFORMA_DIGITAL": "Plataforma digital",
        "PROFISSIONAL_AUTONOMO": "Profissional autônomo",
        "OUTRO": "Outro",
    }

    TIPOS_OBJETO = {
        "PRODUTO": "Produto",
        "SERVICO": "Serviço",
        "CONTRATO": "Contrato",
        "OPERACAO_FINANCEIRA": "Operação financeira",
        "OUTRO": "Outro",
    }

    FORMAS_PAGAMENTO = {
        "DINHEIRO": "Dinheiro",
        "PIX": "Pix",
        "CARTAO_CREDITO": "Cartão de crédito",
        "CARTAO_DEBITO": "Cartão de débito",
        "BOLETO": "Boleto",
        "TRANSFERENCIA": "Transferência bancária",
        "FINANCIAMENTO": "Financiamento",
        "DEBITO_AUTOMATICO": "Débito automático",
        "OUTRA": "Outra",
    }

    CANAIS_RECLAMACAO = {
        "SAC": "SAC",
        "OUVIDORIA": "Ouvidoria",
        "PROCON": "Procon",
        "CONSUMIDOR_GOV": "Consumidor.gov.br",
        "RECLAME_AQUI": "Reclame Aqui",
        "BANCO_CENTRAL": "Banco Central",
        "ANS": "ANS",
        "ANATEL": "Anatel",
        "ANEEL": "Aneel",
        "JUIZADO": "Juizado Especial",
        "OUTRO": "Outro",
    }

    VIABILIDADES = {
        "ALTA": "Alta",
        "MEDIA": "Média",
        "BAIXA": "Baixa",
        "INVIAVEL": "Inviável",
        "PENDENTE": "Pendente de documentos ou análise",
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
        db.ForeignKey("atendimentos.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
        index=True,
    )

    # ============================================================
    # ETAPA 1 — ATENDIMENTO
    # ============================================================

    tipo_demanda = db.Column(
        db.String(50),
        nullable=True,
    )

    outro_tipo_demanda = db.Column(
        db.String(200),
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
        db.String(100),
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
    # ETAPA 2 — CONSUMIDOR
    # ============================================================

    consumidor_estado_civil = db.Column(
        db.String(50),
        nullable=True,
    )

    consumidor_profissao = db.Column(
        db.String(150),
        nullable=True,
    )

    consumidor_renda_mensal = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    consumidor_escolaridade = db.Column(
        db.String(100),
        nullable=True,
    )

    consumidor_idoso = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    consumidor_possui_deficiencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    consumidor_descricao_deficiencia = db.Column(
        db.Text,
        nullable=True,
    )

    consumidor_vulneravel = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    consumidor_descricao_vulnerabilidade = db.Column(
        db.Text,
        nullable=True,
    )

    consumidor_dependentes = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_consumidor = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 3 — FORNECEDOR
    # ============================================================

    tipo_fornecedor = db.Column(
        db.String(50),
        nullable=True,
    )

    fornecedor_nome = db.Column(
        db.String(200),
        nullable=True,
    )

    fornecedor_nome_fantasia = db.Column(
        db.String(200),
        nullable=True,
    )

    fornecedor_cnpj = db.Column(
        db.String(18),
        nullable=True,
    )

    fornecedor_cpf = db.Column(
        db.String(14),
        nullable=True,
    )

    fornecedor_telefone = db.Column(
        db.String(30),
        nullable=True,
    )

    fornecedor_email = db.Column(
        db.String(150),
        nullable=True,
    )

    fornecedor_site = db.Column(
        db.String(250),
        nullable=True,
    )

    fornecedor_endereco = db.Column(
        db.String(250),
        nullable=True,
    )

    fornecedor_cidade = db.Column(
        db.String(150),
        nullable=True,
    )

    fornecedor_estado = db.Column(
        db.String(2),
        nullable=True,
    )

    fornecedor_responsavel = db.Column(
        db.String(150),
        nullable=True,
    )

    fornecedor_grupo_economico = db.Column(
        db.String(200),
        nullable=True,
    )

    observacoes_fornecedor = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 4 — PRODUTO OU SERVIÇO
    # ============================================================

    tipo_objeto = db.Column(
        db.String(50),
        nullable=True,
    )

    produto_servico_nome = db.Column(
        db.String(200),
        nullable=True,
    )

    produto_marca = db.Column(
        db.String(150),
        nullable=True,
    )

    produto_modelo = db.Column(
        db.String(150),
        nullable=True,
    )

    numero_pedido = db.Column(
        db.String(100),
        nullable=True,
    )

    numero_contrato = db.Column(
        db.String(100),
        nullable=True,
    )

    data_compra_contratacao = db.Column(
        db.Date,
        nullable=True,
    )

    data_entrega_inicio_servico = db.Column(
        db.Date,
        nullable=True,
    )

    valor_total = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    forma_pagamento = db.Column(
        db.String(50),
        nullable=True,
    )

    quantidade_parcelas = db.Column(
        db.Integer,
        nullable=True,
    )

    valor_parcela = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    local_compra_contratacao = db.Column(
        db.String(250),
        nullable=True,
    )

    possui_nota_fiscal = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_contrato = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_garantia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    prazo_garantia = db.Column(
        db.String(100),
        nullable=True,
    )

    descricao_produto_servico = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 5 — PROBLEMA
    # ============================================================

    data_inicio_problema = db.Column(
        db.Date,
        nullable=True,
    )

    data_conhecimento_problema = db.Column(
        db.Date,
        nullable=True,
    )

    descricao_problema = db.Column(
        db.Text,
        nullable=True,
    )

    problema_continua = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    problema_recorrente = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    quantidade_ocorrencias = db.Column(
        db.Integer,
        nullable=True,
    )

    fornecedor_reconheceu_problema = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    resposta_fornecedor = db.Column(
        db.Text,
        nullable=True,
    )

    houve_interrupcao_servico = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    periodo_interrupcao = db.Column(
        db.String(200),
        nullable=True,
    )

    houve_negativacao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    orgao_negativador = db.Column(
        db.String(100),
        nullable=True,
    )

    data_negativacao = db.Column(
        db.Date,
        nullable=True,
    )

    valor_negativado = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    observacoes_problema = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 6 — TENTATIVAS DE SOLUÇÃO
    # ============================================================

    realizou_tentativa_solucao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    canais_reclamacao = db.Column(
        db.Text,
        nullable=True,
    )

    datas_reclamacoes = db.Column(
        db.Text,
        nullable=True,
    )

    protocolos_reclamacoes = db.Column(
        db.Text,
        nullable=True,
    )

    descricao_tentativas = db.Column(
        db.Text,
        nullable=True,
    )

    fornecedor_apresentou_resposta = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_resposta_fornecedor = db.Column(
        db.Text,
        nullable=True,
    )

    houve_proposta_acordo = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_proposta_acordo = db.Column(
        db.Text,
        nullable=True,
    )

    proposta_aceita = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    motivo_recusa_proposta = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_tentativas = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 7 — PREJUÍZOS
    # ============================================================

    houve_dano_material = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    valor_dano_material = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    descricao_dano_material = db.Column(
        db.Text,
        nullable=True,
    )

    houve_gastos_extras = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    valor_gastos_extras = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    descricao_gastos_extras = db.Column(
        db.Text,
        nullable=True,
    )

    houve_lucros_cessantes = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    valor_lucros_cessantes = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    descricao_lucros_cessantes = db.Column(
        db.Text,
        nullable=True,
    )

    houve_dano_moral = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_dano_moral = db.Column(
        db.Text,
        nullable=True,
    )

    houve_constrangimento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_constrangimento = db.Column(
        db.Text,
        nullable=True,
    )

    houve_perda_tempo_util = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_perda_tempo_util = db.Column(
        db.Text,
        nullable=True,
    )

    valor_total_prejuizo = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    observacoes_prejuizos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 8 — DOCUMENTOS
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

    possui_nota_fiscal_documento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_contrato_documento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_comprovante_pagamento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_faturas = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_protocolos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_conversas = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_emails = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_fotos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_videos = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_prints = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_documento_negativacao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    possui_boletim_ocorrencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    outros_documentos = db.Column(
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
    # ETAPA 9 — PEDIDOS DO CLIENTE
    # ============================================================

    pedido_troca = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_reparo = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_cancelamento = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_restituicao_simples = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_restituicao_dobro = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_dano_material = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_dano_moral = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_obrigacao_fazer = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_obrigacao_nao_fazer = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_retirada_negativacao = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_tutela_urgencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    pedido_outro = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    descricao_outro_pedido = db.Column(
        db.Text,
        nullable=True,
    )

    valor_pretendido = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    objetivo_principal_cliente = db.Column(
        db.Text,
        nullable=True,
    )

    aceita_acordo = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    valor_minimo_acordo = db.Column(
        db.Numeric(12, 2),
        nullable=True,
    )

    observacoes_pedidos = db.Column(
        db.Text,
        nullable=True,
    )

    # ============================================================
    # ETAPA 10 — ANÁLISE JURÍDICA
    # ============================================================

    relacao_consumo_configurada = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cdc_aplicavel = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    responsabilidade_objetiva = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cabivel_inversao_onus = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cabivel_tutela_urgencia = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cabivel_repeticao_indebito = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cabivel_dano_material = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    cabivel_dano_moral = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    competencia = db.Column(
        db.String(200),
        nullable=True,
    )

    prazo_prescricional = db.Column(
        db.String(200),
        nullable=True,
    )

    fundamentos_juridicos = db.Column(
        db.Text,
        nullable=True,
    )

    jurisprudencia_relevante = db.Column(
        db.Text,
        nullable=True,
    )

    provas_disponiveis = db.Column(
        db.Text,
        nullable=True,
    )

    provas_pendentes = db.Column(
        db.Text,
        nullable=True,
    )

    riscos_processuais = db.Column(
        db.Text,
        nullable=True,
    )

    estrategia_recomendada = db.Column(
        db.Text,
        nullable=True,
    )

    possibilidade_acordo = db.Column(
        db.Text,
        nullable=True,
    )

    viabilidade = db.Column(
        db.String(30),
        nullable=True,
    )

    parecer_inicial = db.Column(
        db.Text,
        nullable=True,
    )

    observacoes_analise = db.Column(
        db.Text,
        nullable=True,
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

    etapa_consumidor_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_fornecedor_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_produto_servico_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_problema_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_tentativas_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_prejuizos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_documentos_concluida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    etapa_pedidos_concluida = db.Column(
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
    )

    atualizado_por = db.relationship(
        "Usuario",
        foreign_keys=[atualizado_por_id],
    )

    # ============================================================
    # PROPRIEDADES
    # ============================================================

    @property
    def progresso_percentual(self):
        etapas = [
            self.etapa_atendimento_concluida,
            self.etapa_consumidor_concluida,
            self.etapa_fornecedor_concluida,
            self.etapa_produto_servico_concluida,
            self.etapa_problema_concluida,
            self.etapa_tentativas_concluida,
            self.etapa_prejuizos_concluida,
            self.etapa_documentos_concluida,
            self.etapa_pedidos_concluida,
            self.etapa_analise_concluida,
        ]

        total = len(etapas)

        if total == 0:
            return 0

        concluidas = sum(
            1
            for etapa in etapas
            if etapa
        )

        return int(
            concluidas * 100 / total
        )

    @property
    def nome_tipo_demanda(self):
        if self.tipo_demanda == "OUTRA" and self.outro_tipo_demanda:
            return self.outro_tipo_demanda

        return self.TIPOS_DEMANDA.get(
            self.tipo_demanda,
            "Não informado",
        )

    @property
    def nome_viabilidade(self):
        return self.VIABILIDADES.get(
            self.viabilidade,
            "Não analisada",
        )

    def __repr__(self):
        return (
            f"<FichaConsumidor "
            f"id={self.id} "
            f"atendimento_id={self.atendimento_id}>"
        )