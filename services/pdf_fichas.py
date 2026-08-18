from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, time
from decimal import Decimal
from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ===========================================# ============================================================
# CORES DO ESCRITÓRIO
# ============================================================

COR_PRIMARIA = colors.HexColor("#111111")      # Preto
COR_SECUNDARIA = colors.HexColor("#B08D57")    # Dourado elegante
COR_DESTAQUE = colors.HexColor("#F4EFE6")      # Dourado bem claro
COR_FUNDO_SECAO = colors.HexColor("#FAF7F2")   # Fundo suave
COR_BORDA = colors.HexColor("#D6C3A5")         # Borda dourada clara
COR_TEXTO = colors.HexColor("#1E1E1E")         # Preto
COR_TEXTO_SUAVE = colors.HexColor("#6C6C6C")   # Cinza
COR_BRANCA = colors.white
COR_ALTERNADA = colors.HexColor("#FCFBF8")

PAGINA_LARGURA, PAGINA_ALTURA = A4

MARGEM_ESQUERDA = 1.6 * cm
MARGEM_DIREITA = 1.6 * cm
MARGEM_SUPERIOR = 2.7 * cm
MARGEM_INFERIOR = 1.8 * cm


# ============================================================
# CAMPOS INTERNOS QUE NÃO DEVEM APARECER NO PDF
# ============================================================

CAMPOS_IGNORADOS = {
    "id",
    "atendimento_id",
    "cliente_id",
    "criado_por_id",
    "atualizado_por_id",
    "usuario_id",
    "responsavel_id",
    "created_at",
    "updated_at",
    "criado_em",
    "atualizado_em",
    "data_criacao",
    "data_atualizacao",
    "foto",
    "senha",
    "senha_hash",
    "password",
    "password_hash",
}


# ============================================================
# RÓTULOS HUMANIZADOS
# ============================================================

ROTULOS = {
    # Atendimento
    "numero": "Número",
    "area": "Área jurídica",
    "status": "Status",
    "assunto": "Assunto",
    "descricao": "Descrição",
    "observacoes": "Observações",
    "data_atendimento": "Data do atendimento",
    "hora_atendimento": "Horário do atendimento",
    "origem": "Origem",
    "prioridade": "Prioridade",
    "responsavel": "Responsável",

    # Cliente
    "nome": "Nome",
    "cpf": "CPF",
    "rg": "RG",
    "data_nascimento": "Data de nascimento",
    "estado_civil": "Estado civil",
    "profissao": "Profissão",
    "telefone": "Telefone",
    "whatsapp": "WhatsApp",
    "email": "E-mail",
    "cep": "CEP",
    "rua": "Logradouro",
    "endereco": "Endereço",
    "numero_endereco": "Número",
    "complemento": "Complemento",
    "bairro": "Bairro",
    "cidade": "Cidade",
    "estado": "Estado",
    "origem_cliente": "Origem do cliente",
    "area_juridica": "Área jurídica",

    # Trabalhista
    "nome_empregador": "Nome do empregador",
    "razao_social": "Razão social",
    "cnpj_empregador": "CNPJ do empregador",
    "cpf_empregador": "CPF do empregador",
    "endereco_empregador": "Endereço do empregador",
    "telefone_empregador": "Telefone do empregador",
    "email_empregador": "E-mail do empregador",
    "cargo_funcao": "Cargo ou função",
    "cargo": "Cargo",
    "funcao": "Função",
    "data_admissao": "Data de admissão",
    "data_demissao": "Data de desligamento",
    "data_rescisao": "Data da rescisão",
    "tipo_contrato": "Tipo de contrato",
    "salario": "Salário",
    "ultimo_salario": "Último salário",
    "remuneracao": "Remuneração",
    "forma_pagamento": "Forma de pagamento",
    "jornada_trabalho": "Jornada de trabalho",
    "horario_entrada": "Horário de entrada",
    "horario_saida": "Horário de saída",
    "intervalo": "Intervalo",
    "trabalhava_sabado": "Trabalhava aos sábados",
    "trabalhava_domingo": "Trabalhava aos domingos",
    "trabalhava_feriado": "Trabalhava em feriados",
    "horas_extras": "Horas extras",
    "controle_ponto": "Controle de ponto",
    "recebia_horas_extras": "Recebia horas extras",
    "adicional_noturno": "Adicional noturno",
    "insalubridade": "Insalubridade",
    "periculosidade": "Periculosidade",
    "comissoes": "Comissões",
    "gorjetas": "Gorjetas",
    "premios": "Prêmios",
    "beneficios": "Benefícios",
    "vale_transporte": "Vale-transporte",
    "vale_refeicao": "Vale-refeição",
    "fgts_regular": "FGTS depositado regularmente",
    "ferias_pendentes": "Férias pendentes",
    "decimo_terceiro_pendente": "13º salário pendente",
    "verbas_rescisorias": "Verbas rescisórias",
    "aviso_previo": "Aviso-prévio",
    "seguro_desemprego": "Seguro-desemprego",
    "motivo_rescisao": "Motivo da rescisão",
    "modalidade_rescisao": "Modalidade da rescisão",
    "recebeu_rescisao": "Recebeu as verbas rescisórias",
    "homologacao": "Homologação",
    "justa_causa": "Justa causa",
    "assédio_moral": "Assédio moral",
    "assedio_moral": "Assédio moral",
    "assédio_sexual": "Assédio sexual",
    "assedio_sexual": "Assédio sexual",
    "discriminacao": "Discriminação",
    "acidente_trabalho": "Acidente de trabalho",
    "doenca_ocupacional": "Doença ocupacional",
    "estabilidade": "Estabilidade",
    "gestante": "Gestante",
    "testemunhas": "Testemunhas",
    "documentos_disponiveis": "Documentos disponíveis",
    "pedidos_trabalhistas": "Pedidos trabalhistas",
    "resumo_trabalhista": "Resumo do caso",
    "analise_juridica": "Análise jurídica",
    "estrategia_sugerida": "Estratégia sugerida",
    "riscos_identificados": "Riscos identificados",
    "providencias_recomendadas": "Providências recomendadas",
    "pendencias_gerais": "Pendências gerais",
    "observacoes_gerais": "Observações gerais",

    # Previdenciário
    "nit": "NIT/PIS/PASEP",
    "pis": "PIS",
    "pasep": "PASEP",
    "numero_nit": "NIT/PIS/PASEP",
    "qualidade_segurado": "Qualidade de segurado",
    "categoria_segurado": "Categoria do segurado",
    "segurado_especial": "Segurado especial",
    "atividade_rural": "Atividade rural",
    "atividade_especial": "Atividade especial",
    "deficiencia": "Pessoa com deficiência",
    "tempo_contribuicao_estimado": "Tempo de contribuição estimado",
    "carencia_estimada": "Carência estimada",
    "vinculos_empregaticios": "Vínculos empregatícios",
    "contribuicoes_individuais": "Contribuições individuais",
    "periodos_rurais": "Períodos rurais",
    "periodos_especiais": "Períodos especiais",
    "periodos_sem_contribuicao": "Períodos sem contribuição",
    "divergencias_cnis": "Divergências no CNIS",
    "beneficio_principal": "Benefício principal",
    "beneficio_principal_nome": "Benefício principal",
    "beneficios_secundarios": "Outros benefícios",
    "data_inicio_incapacidade": "Data de início da incapacidade",
    "tipo_incapacidade": "Tipo de incapacidade",
    "tipo_incapacidade_nome": "Tipo de incapacidade",
    "cid_principal": "CID principal",
    "outros_cids": "Outros CIDs",
    "diagnostico": "Diagnóstico",
    "tratamento": "Tratamento",
    "medicamentos": "Medicamentos",
    "medico_assistente": "Médico assistente",
    "especialidade_medica": "Especialidade médica",
    "limitacoes_funcionais": "Limitações funcionais",
    "necessita_terceiros": "Necessita de auxílio de terceiros",
    "documentacao_medica": "Documentação médica",
    "laudos_medicos": "Laudos médicos",
    "exames_medicos": "Exames médicos",
    "atestados_medicos": "Atestados médicos",
    "documentos_previdenciarios": "Documentos previdenciários",
    "cnis_disponivel": "CNIS disponível",
    "carteira_trabalho": "Carteira de trabalho",
    "guias_recolhimento": "Guias de recolhimento",
    "requerimento_administrativo": "Requerimento administrativo",
    "situacao_requerimento": "Situação do requerimento",
    "numero_beneficio": "Número do benefício",
    "numero_protocolo": "Número do protocolo",
    "data_requerimento": "Data do requerimento",
    "data_decisao": "Data da decisão",
    "data_pericia": "Data da perícia",
    "resultado_pericia": "Resultado da perícia",
    "resultado_requerimento": "Resultado do requerimento",
    "motivo_indeferimento": "Motivo do indeferimento",
    "exigencia_inss": "Exigência do INSS",
    "prazo_exigencia": "Prazo da exigência",
    "recurso_administrativo": "Recurso administrativo",
    "processo_judicial": "Processo judicial",
    "resumo_previdenciario": "Resumo do caso",

    # Cível
    "natureza_demanda": "Natureza da demanda",
    "natureza_demanda_outro": "Outra natureza da demanda",
    "assunto_principal": "Assunto principal",
    "objetivo_cliente": "Objetivo do cliente",
    "existe_urgencia": "Existe urgência",
    "descricao_urgencia": "Descrição da urgência",
    "data_limite_urgencia": "Data limite da urgência",
    "valor_estimado_causa": "Valor estimado da causa",
    "aceita_acordo": "Aceita acordo",
    "valor_minimo_acordo": "Valor mínimo para acordo",
    "observacoes_atendimento": "Observações do atendimento",
    "estado_civil_atual": "Estado civil atual",
    "profissao_atual": "Profissão atual",
    "renda_mensal_aproximada": "Renda mensal aproximada",
    "possui_beneficio_justica_gratuita": "Possui benefício da justiça gratuita",
    "motivo_justica_gratuita": "Justificativa para justiça gratuita",
    "contato_alternativo_nome": "Nome do contato alternativo",
    "contato_alternativo_telefone": "Telefone do contato alternativo",
    "contato_alternativo_relacao": "Relação do contato com o cliente",
    "melhor_horario_contato": "Melhor horário para contato",
    "observacoes_cliente": "Observações sobre o cliente",
    "parte_contraria_nome": "Nome da parte contrária",
    "parte_contraria_tipo": "Tipo da parte contrária",
    "parte_contraria_cpf_cnpj": "CPF/CNPJ da parte contrária",
    "parte_contraria_rg": "RG da parte contrária",
    "parte_contraria_endereco": "Endereço da parte contrária",
    "parte_contraria_cidade": "Cidade da parte contrária",
    "parte_contraria_estado": "Estado da parte contrária",
    "parte_contraria_cep": "CEP da parte contrária",
    "parte_contraria_telefone": "Telefone da parte contrária",
    "parte_contraria_whatsapp": "WhatsApp da parte contrária",
    "parte_contraria_email": "E-mail da parte contrária",
    "relacao_com_cliente": "Relação com o cliente",
    "possui_advogado": "A parte contrária possui advogado",
    "advogado_parte_contraria": "Advogado da parte contrária",
    "observacoes_parte_contraria": "Observações sobre a parte contrária",
    "data_inicio_fatos": "Data de início dos fatos",
    "data_ultimo_fato": "Data do último fato",
    "local_fatos": "Local dos fatos",
    "descricao_detalhada_fatos": "Descrição detalhada dos fatos",
    "fatos_continuam_ocorrendo": "Os fatos continuam ocorrendo",
    "houve_ameaca": "Houve ameaça",
    "descricao_ameaca": "Descrição da ameaça",
    "existem_testemunhas": "Existem testemunhas",
    "testemunhas_dados": "Dados das testemunhas",
    "existem_provas": "Existem provas",
    "provas_existentes": "Provas existentes",
    "cliente_participou_diretamente": "Cliente participou diretamente",
    "terceiros_envolvidos": "Terceiros envolvidos",
    "observacoes_fatos": "Observações sobre os fatos",
    "existe_contrato": "Existe contrato",
    "contrato_escrito": "Contrato escrito",
    "data_contrato": "Data do contrato",
    "data_fim_contrato": "Data final do contrato",
    "valor_contrato": "Valor do contrato",
    "contrato_quitado": "Contrato quitado",
    "possui_comprovantes_pagamento": "Possui comprovantes de pagamento",
    "obrigacao_cliente": "Obrigação do cliente",
    "obrigacao_parte_contraria": "Obrigação da parte contrária",
    "obrigacao_descumprida": "Obrigação descumprida",
    "houve_multa_contratual": "Houve multa contratual",
    "valor_multa_contratual": "Valor da multa contratual",
    "observacoes_contrato": "Observações sobre o contrato",
    "houve_dano_material": "Houve dano material",
    "descricao_dano_material": "Descrição do dano material",
    "valor_dano_material": "Valor do dano material",
    "houve_dano_moral": "Houve dano moral",
    "descricao_dano_moral": "Descrição do dano moral",
    "valor_pretendido_dano_moral": "Valor pretendido por dano moral",
    "houve_lucros_cessantes": "Houve lucros cessantes",
    "descricao_lucros_cessantes": "Descrição dos lucros cessantes",
    "valor_lucros_cessantes": "Valor dos lucros cessantes",
    "houve_dano_estetico": "Houve dano estético",
    "descricao_dano_estetico": "Descrição do dano estético",
    "existem_gastos_futuros": "Existem gastos futuros",
    "descricao_gastos_futuros": "Descrição dos gastos futuros",
    "valor_total_prejuizo": "Valor total do prejuízo",
    "observacoes_danos": "Observações sobre os danos",
    "houve_contato_parte_contraria": "Houve contato com a parte contrária",
    "descricao_contatos": "Descrição dos contatos",
    "houve_proposta_acordo": "Houve proposta de acordo",
    "descricao_proposta_acordo": "Descrição da proposta de acordo",
    "enviou_notificacao_extrajudicial": "Enviou notificação extrajudicial",
    "data_notificacao_extrajudicial": "Data da notificação extrajudicial",
    "houve_resposta_notificacao": "Houve resposta à notificação",
    "descricao_resposta_notificacao": "Descrição da resposta à notificação",
    "fez_reclamacao_administrativa": "Fez reclamação administrativa",
    "orgao_reclamacao": "Órgão da reclamação",
    "protocolo_reclamacao": "Protocolo da reclamação",
    "registrou_boletim_ocorrencia": "Registrou boletim de ocorrência",
    "numero_boletim_ocorrencia": "Número do boletim de ocorrência",
    "data_boletim_ocorrencia": "Data do boletim de ocorrência",
    "existe_processo_anterior": "Existe processo anterior",
    "numero_processo_anterior": "Número do processo anterior",
    "resultado_processo_anterior": "Resultado do processo anterior",
    "observacoes_tentativas": "Observações sobre as tentativas",
    "possui_documento_identificacao": "Documento de identificação",
    "possui_comprovante_residencia": "Comprovante de residência",
    "possui_comprovantes": "Comprovantes",
    "possui_conversas": "Conversas ou mensagens",
    "possui_fotos": "Fotos",
    "possui_audios": "Áudios",
    "possui_videos": "Vídeos",
    "possui_laudos": "Laudos",
    "possui_orcamentos": "Orçamentos",
    "possui_notificacoes": "Notificações",
    "possui_boletim_ocorrencia": "Boletim de ocorrência",
    "outros_documentos": "Outros documentos",
    "documentos_entregues": "Documentos entregues",
    "documentos_pendentes": "Documentos pendentes",
    "observacoes_documentos": "Observações sobre os documentos",
    "existe_prescricao": "Existe prescrição",
    "prazo_prescricional": "Prazo prescricional",
    "data_final_prescricao": "Data final da prescrição",
    "competencia": "Competência",
    "foro_competente": "Foro competente",
    "legitimidade_cliente": "Legitimidade do cliente",
    "legitimidade_parte_contraria": "Legitimidade da parte contrária",
    "fundamentos_juridicos": "Fundamentos jurídicos",
    "pedidos_sugeridos": "Pedidos sugeridos",
    "necessidade_tutela_urgencia": "Necessidade de tutela de urgência",
    "fundamentos_tutela_urgencia": "Fundamentos da tutela de urgência",
    "riscos_processo": "Riscos do processo",
    "provas_necessarias": "Provas necessárias",
    "providencias_iniciais": "Providências iniciais",
    "viabilidade_demanda": "Viabilidade da demanda",
    "parecer_inicial": "Parecer inicial",
}


# ============================================================
# ORDENAÇÃO E AGRUPAMENTO DAS SEÇÕES
# ============================================================

SECOES_TRABALHISTAS = [
    (
        "Dados do empregador",
        (
            "nome_empregador",
            "razao_social",
            "cnpj_empregador",
            "cpf_empregador",
            "endereco_empregador",
            "telefone_empregador",
            "email_empregador",
        ),
    ),
    (
        "Contrato de trabalho",
        (
            "cargo_funcao",
            "cargo",
            "funcao",
            "data_admissao",
            "data_demissao",
            "data_rescisao",
            "tipo_contrato",
            "salario",
            "ultimo_salario",
            "remuneracao",
            "forma_pagamento",
        ),
    ),
    (
        "Jornada de trabalho",
        (
            "jornada_trabalho",
            "horario_entrada",
            "horario_saida",
            "intervalo",
            "trabalhava_sabado",
            "trabalhava_domingo",
            "trabalhava_feriado",
            "horas_extras",
            "controle_ponto",
            "recebia_horas_extras",
            "adicional_noturno",
        ),
    ),
    (
        "Remuneração e adicionais",
        (
            "insalubridade",
            "periculosidade",
            "comissoes",
            "gorjetas",
            "premios",
            "beneficios",
            "vale_transporte",
            "vale_refeicao",
        ),
    ),
    (
        "Direitos trabalhistas",
        (
            "fgts_regular",
            "ferias_pendentes",
            "decimo_terceiro_pendente",
            "verbas_rescisorias",
            "aviso_previo",
            "seguro_desemprego",
        ),
    ),
    (
        "Rescisão do contrato",
        (
            "motivo_rescisao",
            "modalidade_rescisao",
            "recebeu_rescisao",
            "homologacao",
            "justa_causa",
        ),
    ),
    (
        "Situações especiais",
        (
            "assedio_moral",
            "assédio_moral",
            "assedio_sexual",
            "assédio_sexual",
            "discriminacao",
            "acidente_trabalho",
            "doenca_ocupacional",
            "estabilidade",
            "gestante",
        ),
    ),
    (
        "Provas e documentos",
        (
            "testemunhas",
            "documentos_disponiveis",
        ),
    ),
    (
        "Pedidos e análise jurídica",
        (
            "pedidos_trabalhistas",
            "resumo_trabalhista",
            "analise_juridica",
            "estrategia_sugerida",
            "riscos_identificados",
            "providencias_recomendadas",
            "pendencias_gerais",
            "observacoes_gerais",
        ),
    ),
]


SECOES_PREVIDENCIARIAS = [
    (
        "Dados do segurado",
        (
            "nit",
            "pis",
            "pasep",
            "numero_nit",
            "qualidade_segurado",
            "categoria_segurado",
            "segurado_especial",
            "atividade_rural",
            "atividade_especial",
            "deficiencia",
        ),
    ),
    (
        "Histórico contributivo",
        (
            "tempo_contribuicao_estimado",
            "carencia_estimada",
            "vinculos_empregaticios",
            "contribuicoes_individuais",
            "periodos_rurais",
            "periodos_especiais",
            "periodos_sem_contribuicao",
            "divergencias_cnis",
        ),
    ),
    (
        "Benefício pretendido",
        (
            "beneficio_principal",
            "beneficio_principal_nome",
            "beneficios_secundarios",
        ),
    ),
    (
        "Saúde e incapacidade",
        (
            "data_inicio_incapacidade",
            "tipo_incapacidade",
            "tipo_incapacidade_nome",
            "cid_principal",
            "outros_cids",
            "diagnostico",
            "tratamento",
            "medicamentos",
            "medico_assistente",
            "especialidade_medica",
            "limitacoes_funcionais",
            "necessita_terceiros",
        ),
    ),
    (
        "Documentação",
        (
            "documentacao_medica",
            "laudos_medicos",
            "exames_medicos",
            "atestados_medicos",
            "documentos_previdenciarios",
            "cnis_disponivel",
            "carteira_trabalho",
            "guias_recolhimento",
        ),
    ),
    (
        "Processo no INSS",
        (
            "requerimento_administrativo",
            "situacao_requerimento",
            "numero_beneficio",
            "numero_protocolo",
            "data_requerimento",
            "data_decisao",
            "data_pericia",
            "resultado_pericia",
            "resultado_requerimento",
            "motivo_indeferimento",
            "exigencia_inss",
            "prazo_exigencia",
            "recurso_administrativo",
            "processo_judicial",
        ),
    ),
    (
        "Resumo e análise jurídica",
        (
            "resumo_previdenciario",
            "analise_juridica",
            "estrategia_sugerida",
            "riscos_identificados",
            "providencias_recomendadas",
            "pendencias_gerais",
            "observacoes_gerais",
        ),
    ),
]



SECOES_FAMILIA = [
    (
        "Atendimento",
        (
            "tipo_demanda",
            "outro_tipo_demanda",
            "resumo_caso",
            "objetivo_cliente",
            "existe_urgencia",
            "descricao_urgencia",
            "data_limite_urgencia",
            "observacoes_atendimento",
        ),
    ),
    (
        "Cliente",
        (
            "cliente_estado_civil",
            "cliente_profissao",
            "cliente_renda_mensal",
            "cliente_reside_com_quem",
            "cliente_dependentes",
            "cliente_possui_deficiencia",
            "cliente_descricao_deficiencia",
            "cliente_recebe_beneficio",
            "cliente_beneficio_descricao",
            "observacoes_cliente",
        ),
    ),
    (
        "Relação familiar",
        (
            "tipo_relacao",
            "data_inicio_relacao",
            "data_casamento",
            "data_separacao_fato",
            "regime_bens",
            "possui_pacto_antenupcial",
            "descricao_pacto_antenupcial",
            "convivencia_publica_continua",
            "objetivo_constituir_familia",
            "relacao_encerrada",
            "motivo_termino_relacao",
            "houve_violencia_domestica",
            "descricao_violencia_domestica",
            "existe_medida_protetiva",
            "numero_medida_protetiva",
            "observacoes_relacao",
        ),
    ),
    (
        "Parte contrária",
        (
            "parte_contraria_nome",
            "parte_contraria_cpf",
            "parte_contraria_rg",
            "parte_contraria_data_nascimento",
            "parte_contraria_profissao",
            "parte_contraria_renda_mensal",
            "parte_contraria_telefone",
            "parte_contraria_email",
            "parte_contraria_endereco",
            "parte_contraria_cidade",
            "parte_contraria_estado",
            "parte_contraria_local_trabalho",
            "comunicacao_entre_partes",
            "observacoes_parte_contraria",
        ),
    ),
    (
        "Filhos",
        (
            "possui_filhos",
            "quantidade_filhos",
            "filhos_em_comum",
            "filhos_menores",
            "filhos_incapazes",
            "dados_filhos",
            "filhos_residem_com",
            "existe_filho_com_deficiencia",
            "necessidades_especiais_filhos",
            "escola_filhos",
            "plano_saude_filhos",
            "despesas_mensais_filhos",
            "detalhamento_despesas_filhos",
            "observacoes_filhos",
        ),
    ),
    (
        "Guarda e convivência",
        (
            "existe_acordo_guarda",
            "tipo_guarda_atual",
            "tipo_guarda_pretendida",
            "guarda_de_fato_com",
            "residencia_referencia_filhos",
            "regime_convivencia_atual",
            "regime_convivencia_pretendido",
            "existe_dificuldade_convivencia",
            "descricao_dificuldade_convivencia",
            "existe_risco_crianca_adolescente",
            "descricao_risco_crianca_adolescente",
            "existe_alienacao_parental",
            "indicios_alienacao_parental",
            "necessita_estudo_psicossocial",
            "observacoes_guarda",
        ),
    ),
    (
        "Alimentos",
        (
            "existe_pensao_atual",
            "pensao_fixada_judicialmente",
            "numero_processo_alimentos",
            "valor_pensao_atual",
            "percentual_pensao_atual",
            "forma_pagamento_pensao",
            "pensao_esta_em_atraso",
            "meses_em_atraso",
            "valor_debito_estimado",
            "valor_pretendido_alimentos",
            "percentual_pretendido_alimentos",
            "despesas_alimentando",
            "capacidade_financeira_alimentante",
            "existem_outros_dependentes",
            "descricao_outros_dependentes",
            "pretende_alimentos_provisorios",
            "observacoes_alimentos",
        ),
    ),
    (
        "Patrimônio e partilha",
        (
            "possui_bens_partilhar",
            "imoveis",
            "veiculos",
            "contas_bancarias_investimentos",
            "empresas_quotas_sociais",
            "bens_moveis_relevantes",
            "dividas_comuns",
            "bens_particulares_cliente",
            "bens_particulares_parte_contraria",
            "existe_ocultacao_patrimonial",
            "indicios_ocultacao_patrimonial",
            "existe_acordo_partilha",
            "proposta_partilha",
            "valor_estimado_patrimonio",
            "observacoes_patrimonio",
        ),
    ),
    (
        "Documentos",
        (
            "possui_documento_identificacao",
            "possui_comprovante_residencia",
            "possui_certidao_casamento",
            "possui_certidao_uniao_estavel",
            "possui_certidoes_nascimento_filhos",
            "possui_comprovantes_renda",
            "possui_comprovantes_despesas",
            "possui_documentos_bens",
            "possui_acordo_anterior",
            "possui_decisao_judicial",
            "possui_boletim_ocorrencia",
            "possui_medida_protetiva",
            "possui_conversas_mensagens",
            "possui_fotos_videos_audios",
            "possui_laudos_relatorios",
            "outros_documentos",
            "documentos_entregues",
            "documentos_pendentes",
            "observacoes_documentos",
        ),
    ),
    (
        "Análise jurídica",
        (
            "competencia",
            "foro_competente",
            "existe_prevencao",
            "processo_prevento",
            "necessidade_intervencao_mp",
            "necessidade_segredo_justica",
            "necessidade_tutela_urgencia",
            "fundamentos_tutela_urgencia",
            "fundamentos_juridicos",
            "pedidos_sugeridos",
            "provas_necessarias",
            "riscos_processo",
            "estrategia_sugerida",
            "providencias_iniciais",
            "possibilidade_acordo",
            "termos_possivel_acordo",
            "viabilidade_demanda",
            "parecer_inicial",
            "observacoes_gerais",
        ),
    ),
]


SECOES_CIVEIS = [
    (
        "Dados iniciais da demanda",
        (
            "natureza_demanda",
            "natureza_demanda_outro",
            "assunto_principal",
            "objetivo_cliente",
            "existe_urgencia",
            "descricao_urgencia",
            "data_limite_urgencia",
            "valor_estimado_causa",
            "aceita_acordo",
            "valor_minimo_acordo",
            "observacoes_atendimento",
        ),
    ),
    (
        "Informações complementares do cliente",
        (
            "estado_civil_atual",
            "profissao_atual",
            "renda_mensal_aproximada",
            "possui_beneficio_justica_gratuita",
            "motivo_justica_gratuita",
            "contato_alternativo_nome",
            "contato_alternativo_telefone",
            "contato_alternativo_relacao",
            "melhor_horario_contato",
            "observacoes_cliente",
        ),
    ),
    (
        "Parte contrária",
        (
            "parte_contraria_nome",
            "parte_contraria_tipo",
            "parte_contraria_cpf_cnpj",
            "parte_contraria_rg",
            "parte_contraria_endereco",
            "parte_contraria_cidade",
            "parte_contraria_estado",
            "parte_contraria_cep",
            "parte_contraria_telefone",
            "parte_contraria_whatsapp",
            "parte_contraria_email",
            "relacao_com_cliente",
            "possui_advogado",
            "advogado_parte_contraria",
            "observacoes_parte_contraria",
        ),
    ),
    (
        "Fatos",
        (
            "data_inicio_fatos",
            "data_ultimo_fato",
            "local_fatos",
            "descricao_detalhada_fatos",
            "fatos_continuam_ocorrendo",
            "houve_ameaca",
            "descricao_ameaca",
            "existem_testemunhas",
            "testemunhas_dados",
            "existem_provas",
            "provas_existentes",
            "cliente_participou_diretamente",
            "terceiros_envolvidos",
            "observacoes_fatos",
        ),
    ),
    (
        "Contrato e obrigações",
        (
            "existe_contrato",
            "contrato_escrito",
            "tipo_contrato",
            "data_contrato",
            "data_fim_contrato",
            "valor_contrato",
            "forma_pagamento",
            "contrato_quitado",
            "possui_comprovantes_pagamento",
            "obrigacao_cliente",
            "obrigacao_parte_contraria",
            "obrigacao_descumprida",
            "houve_multa_contratual",
            "valor_multa_contratual",
            "observacoes_contrato",
        ),
    ),
    (
        "Danos e prejuízos",
        (
            "houve_dano_material",
            "descricao_dano_material",
            "valor_dano_material",
            "houve_dano_moral",
            "descricao_dano_moral",
            "valor_pretendido_dano_moral",
            "houve_lucros_cessantes",
            "descricao_lucros_cessantes",
            "valor_lucros_cessantes",
            "houve_dano_estetico",
            "descricao_dano_estetico",
            "existem_gastos_futuros",
            "descricao_gastos_futuros",
            "valor_total_prejuizo",
            "observacoes_danos",
        ),
    ),
    (
        "Tentativas de solução",
        (
            "houve_contato_parte_contraria",
            "descricao_contatos",
            "houve_proposta_acordo",
            "descricao_proposta_acordo",
            "enviou_notificacao_extrajudicial",
            "data_notificacao_extrajudicial",
            "houve_resposta_notificacao",
            "descricao_resposta_notificacao",
            "fez_reclamacao_administrativa",
            "orgao_reclamacao",
            "protocolo_reclamacao",
            "registrou_boletim_ocorrencia",
            "numero_boletim_ocorrencia",
            "data_boletim_ocorrencia",
            "existe_processo_anterior",
            "numero_processo_anterior",
            "resultado_processo_anterior",
            "observacoes_tentativas",
        ),
    ),
    (
        "Documentos",
        (
            "possui_documento_identificacao",
            "possui_comprovante_residencia",
            "possui_contrato",
            "possui_comprovantes",
            "possui_conversas",
            "possui_fotos",
            "possui_audios",
            "possui_videos",
            "possui_laudos",
            "possui_orcamentos",
            "possui_notificacoes",
            "possui_boletim_ocorrencia",
            "outros_documentos",
            "documentos_entregues",
            "documentos_pendentes",
            "observacoes_documentos",
        ),
    ),
    (
        "Análise jurídica",
        (
            "existe_prescricao",
            "prazo_prescricional",
            "data_final_prescricao",
            "competencia",
            "foro_competente",
            "legitimidade_cliente",
            "legitimidade_parte_contraria",
            "fundamentos_juridicos",
            "pedidos_sugeridos",
            "necessidade_tutela_urgencia",
            "fundamentos_tutela_urgencia",
            "riscos_processo",
            "provas_necessarias",
            "providencias_iniciais",
            "estrategia_sugerida",
            "viabilidade_demanda",
            "parecer_inicial",
            "observacoes_gerais",
        ),
    ),
]


# ============================================================
# ESTILOS
# ============================================================

def criar_estilos() -> dict[str, ParagraphStyle]:
    estilos_base = getSampleStyleSheet()

    return {
        "titulo": ParagraphStyle(
            "TituloFicha",
            parent=estilos_base["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            alignment=TA_CENTER,
            textColor=COR_PRIMARIA,
            spaceAfter=5,
        ),
        "subtitulo": ParagraphStyle(
            "SubtituloFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=COR_TEXTO_SUAVE,
            spaceAfter=12,
        ),
        "secao": ParagraphStyle(
            "SecaoFicha",
            parent=estilos_base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=COR_PRIMARIA,
            leftIndent=0,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "rotulo": ParagraphStyle(
            "RotuloFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=COR_SECUNDARIA,
        ),
        "valor": ParagraphStyle(
            "ValorFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=COR_TEXTO,
            alignment=TA_LEFT,
        ),
        "texto_longo": ParagraphStyle(
            "TextoLongoFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=COR_TEXTO,
            alignment=TA_JUSTIFY,
            spaceAfter=3,
        ),
        "aviso": ParagraphStyle(
            "AvisoFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=10,
            alignment=TA_CENTER,
            textColor=COR_TEXTO_SUAVE,
        ),
        "rodape": ParagraphStyle(
            "RodapeFicha",
            parent=estilos_base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
            textColor=COR_TEXTO_SUAVE,
        ),
    }


# ============================================================
# DOCUMENTO COM CABEÇALHO E RODAPÉ
# ============================================================

class DocumentoFichaPDF(BaseDocTemplate):
    def __init__(
        self,
        buffer: BytesIO,
        titulo_rodape: str,
        nome_escritorio: str = "Sistema Jurídico",
    ) -> None:
        super().__init__(
            buffer,
            pagesize=A4,
            leftMargin=MARGEM_ESQUERDA,
            rightMargin=MARGEM_DIREITA,
            topMargin=MARGEM_SUPERIOR,
            bottomMargin=MARGEM_INFERIOR,
            title=titulo_rodape,
            author=nome_escritorio,
            subject="Ficha de atendimento jurídico",
            creator="Sistema Jurídico",
        )

        self.titulo_rodape = titulo_rodape
        self.nome_escritorio = nome_escritorio

        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="frame_principal",
        )

        template = PageTemplate(
            id="pagina_ficha",
            frames=[frame],
            onPage=self._desenhar_cabecalho_rodape,
        )

        self.addPageTemplates([template])

    def _desenhar_cabecalho_rodape(self, canvas, documento) -> None:
        canvas.saveState()

        # Cabeçalho
        canvas.setFillColor(COR_PRIMARIA)
        canvas.rect(
            0,
            PAGINA_ALTURA - 1.45 * cm,
            PAGINA_LARGURA,
            1.45 * cm,
            stroke=0,
            fill=1,
        )

        canvas.setFillColor(COR_BRANCA)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(
            MARGEM_ESQUERDA,
            PAGINA_ALTURA - 0.88 * cm,
            self.nome_escritorio,
        )

        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            PAGINA_LARGURA - MARGEM_DIREITA,
            PAGINA_ALTURA - 0.88 * cm,
            self.titulo_rodape,
        )

        # Linha do rodapé
        canvas.setStrokeColor(COR_BORDA)
        canvas.setLineWidth(0.5)
        canvas.line(
            MARGEM_ESQUERDA,
            1.18 * cm,
            PAGINA_LARGURA - MARGEM_DIREITA,
            1.18 * cm,
        )

        canvas.setFillColor(COR_TEXTO_SUAVE)
        canvas.setFont("Helvetica", 7)

        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

        canvas.drawString(
            MARGEM_ESQUERDA,
            0.78 * cm,
            f"Gerado em {data_geracao}",
        )

        canvas.drawRightString(
            PAGINA_LARGURA - MARGEM_DIREITA,
            0.78 * cm,
            f"Página {documento.page}",
        )

        canvas.restoreState()


# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def escapar_html(valor: Any) -> str:
    texto = str(valor)

    return (
        texto.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "<br/>")
    )


def remover_acentos(texto: str) -> str:
    texto_normalizado = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(caractere)
    )


def nome_arquivo_seguro(texto: str) -> str:
    texto = remover_acentos(texto or "cliente")
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto)

    return texto.strip("_") or "cliente"


def obter_nome_cliente(atendimento: Any) -> str:
    cliente = getattr(atendimento, "cliente", None)

    if cliente is None:
        return "Cliente não informado"

    return getattr(cliente, "nome", None) or "Cliente não informado"


def obter_nome_escritorio(configuracao: Any = None) -> str:
    if configuracao is None:
        return "Sistema Jurídico"

    for campo in (
        "nome_escritorio",
        "nome_fantasia",
        "razao_social",
        "nome",
    ):
        valor = getattr(configuracao, campo, None)

        if valor:
            return str(valor)

    return "Sistema Jurídico"


def obter_valor(objeto: Any, campo: str, padrao: Any = None) -> Any:
    if objeto is None:
        return padrao

    try:
        return getattr(objeto, campo, padrao)
    except Exception:
        return padrao


def valor_esta_vazio(valor: Any) -> bool:
    if valor is None:
        return True

    if isinstance(valor, str):
        return not valor.strip()

    if isinstance(valor, (list, tuple, set, dict)):
        return len(valor) == 0

    return False


def formatar_booleano(valor: bool) -> str:
    return "Sim" if valor else "Não"


def formatar_decimal(valor: Decimal) -> str:
    numero = float(valor)

    return (
        f"R$ {numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_lista(valor: Iterable[Any]) -> str:
    itens = []

    for item in valor:
        if item is None:
            continue

        if hasattr(item, "nome"):
            item_formatado = getattr(item, "nome")
        elif hasattr(item, "titulo"):
            item_formatado = getattr(item, "titulo")
        elif hasattr(item, "descricao"):
            item_formatado = getattr(item, "descricao")
        else:
            item_formatado = str(item)

        if item_formatado:
            itens.append(str(item_formatado))

    return ", ".join(itens)


def formatar_valor(valor: Any) -> str:
    if valor_esta_vazio(valor):
        return "Não informado"

    if isinstance(valor, bool):
        return formatar_booleano(valor)

    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y às %H:%M")

    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    if isinstance(valor, time):
        return valor.strftime("%H:%M")

    if isinstance(valor, Decimal):
        return formatar_decimal(valor)

    if isinstance(valor, float):
        return (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    if isinstance(valor, dict):
        return "; ".join(
            f"{humanizar_campo(chave)}: {formatar_valor(item)}"
            for chave, item in valor.items()
        )

    if isinstance(valor, (list, tuple, set)):
        texto_lista = formatar_lista(valor)
        return texto_lista or "Não informado"

    texto = str(valor).strip()

    if not texto:
        return "Não informado"

    texto_normalizado = texto.upper()

    respostas = {
        "SIM": "Sim",
        "NAO": "Não",
        "NÃO": "Não",
        "TRUE": "Sim",
        "FALSE": "Não",
        "NAO_INFORMADO": "Não informado",
        "NÃO_INFORMADO": "Não informado",
    }

    if texto_normalizado in respostas:
        return respostas[texto_normalizado]

    if "_" in texto and texto == texto.upper():
        return texto.replace("_", " ").title()

    return texto


def humanizar_campo(campo: str) -> str:
    if campo in ROTULOS:
        return ROTULOS[campo]

    texto = campo.replace("_", " ").strip()

    substituicoes = {
        "Cpf": "CPF",
        "Cnpj": "CNPJ",
        "Rg": "RG",
        "Pis": "PIS",
        "Pasep": "PASEP",
        "Nit": "NIT",
        "Cnis": "CNIS",
        "Inss": "INSS",
        "Cid": "CID",
        "Fgts": "FGTS",
    }

    texto = texto.capitalize()

    for original, substituto in substituicoes.items():
        texto = texto.replace(original, substituto)

    return texto


def obter_colunas_modelo(objeto: Any) -> list[str]:
    if objeto is None:
        return []

    tabela = getattr(objeto, "__table__", None)

    if tabela is not None:
        try:
            return [
                coluna.name
                for coluna in tabela.columns
                if coluna.name not in CAMPOS_IGNORADOS
            ]
        except Exception:
            pass

    mapper = getattr(objeto, "__mapper__", None)

    if mapper is not None:
        try:
            return [
                coluna.key
                for coluna in mapper.column_attrs
                if coluna.key not in CAMPOS_IGNORADOS
            ]
        except Exception:
            pass

    return [
        campo
        for campo in vars(objeto).keys()
        if not campo.startswith("_")
        and campo not in CAMPOS_IGNORADOS
        and not callable(getattr(objeto, campo, None))
    ]


def coletar_campos(
    objeto: Any,
    campos: Iterable[str],
    usados: set[str] | None = None,
) -> list[tuple[str, str]]:
    resultado = []

    for campo in campos:
        if campo in CAMPOS_IGNORADOS:
            continue

        if usados is not None and campo in usados:
            continue

        if not hasattr(objeto, campo):
            continue

        valor = obter_valor(objeto, campo)

        if valor_esta_vazio(valor):
            continue

        valor_formatado = formatar_valor(valor)

        if valor_formatado == "Não informado":
            continue

        resultado.append(
            (
                humanizar_campo(campo),
                valor_formatado,
            )
        )

        if usados is not None:
            usados.add(campo)

    return resultado


def coletar_campos_restantes(
    objeto: Any,
    usados: set[str],
) -> list[tuple[str, str]]:
    campos = obter_colunas_modelo(objeto)

    return coletar_campos(
        objeto=objeto,
        campos=campos,
        usados=usados,
    )


def dados_cliente(atendimento: Any) -> list[tuple[str, str]]:
    cliente = getattr(atendimento, "cliente", None)

    if cliente is None:
        return [("Cliente", "Não informado")]

    campos = (
        "nome",
        "cpf",
        "rg",
        "data_nascimento",
        "estado_civil",
        "profissao",
        "telefone",
        "whatsapp",
        "email",
        "cep",
        "rua",
        "endereco",
        "numero",
        "numero_endereco",
        "complemento",
        "bairro",
        "cidade",
        "estado",
    )

    usados: set[str] = set()
    dados = coletar_campos(cliente, campos, usados)

    if not dados:
        dados.append(("Cliente", "Não informado"))

    return dados


def dados_atendimento(atendimento: Any) -> list[tuple[str, str]]:
    campos = (
        "numero",
        "area",
        "status",
        "assunto",
        "descricao",
        "data_atendimento",
        "hora_atendimento",
        "origem",
        "prioridade",
        "responsavel",
        "observacoes",
    )

    usados: set[str] = set()
    dados = coletar_campos(atendimento, campos, usados)

    if not dados:
        dados.append(
            (
                "Identificação",
                f"Atendimento nº {getattr(atendimento, 'id', '')}",
            )
        )

    return dados


# ============================================================
# COMPONENTES VISUAIS
# ============================================================

def criar_titulo_secao(
    titulo: str,
    estilos: dict[str, ParagraphStyle],
):
    tabela = Table(
        [
            [
                Paragraph(
                    escapar_html(titulo),
                    estilos["secao"],
                )
            ]
        ],
        colWidths=[17.8 * cm],
    )

    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COR_FUNDO_SECAO),
                ("BOX", (0, 0), (-1, -1), 0.6, COR_BORDA),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return tabela


def criar_tabela_dados(
    dados: list[tuple[str, str]],
    estilos: dict[str, ParagraphStyle],
):
    linhas = []

    for indice, (rotulo, valor) in enumerate(dados):
        fundo = COR_BRANCA if indice % 2 == 0 else COR_ALTERNADA

        linhas.append(
            [
                Paragraph(
                    escapar_html(rotulo),
                    estilos["rotulo"],
                ),
                Paragraph(
                    escapar_html(valor),
                    estilos["valor"],
                ),
                fundo,
            ]
        )

    dados_tabela = [
        [linha[0], linha[1]]
        for linha in linhas
    ]

    tabela = Table(
        dados_tabela,
        colWidths=[5.1 * cm, 12.7 * cm],
        repeatRows=0,
        hAlign="LEFT",
    )

    comandos = [
        ("GRID", (0, 0), (-1, -1), 0.35, COR_BORDA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]

    for indice, linha in enumerate(linhas):
        comandos.append(
            (
                "BACKGROUND",
                (0, indice),
                (-1, indice),
                linha[2],
            )
        )

    tabela.setStyle(TableStyle(comandos))

    return tabela


def adicionar_secao(
    elementos: list,
    titulo: str,
    dados: list[tuple[str, str]],
    estilos: dict[str, ParagraphStyle],
) -> None:
    if not dados:
        return

    elementos.append(
        KeepTogether(
            [
                criar_titulo_secao(titulo, estilos),
                Spacer(1, 0.12 * cm),
            ]
        )
    )

    elementos.append(
        criar_tabela_dados(dados, estilos)
    )

    elementos.append(Spacer(1, 0.35 * cm))


def criar_cabecalho_documento(
    titulo: str,
    atendimento: Any,
    estilos: dict[str, ParagraphStyle],
) -> list:
    nome_cliente = obter_nome_cliente(atendimento)

    atendimento_id = getattr(atendimento, "id", None)

    identificacao = (
        f"Atendimento nº {atendimento_id}"
        if atendimento_id is not None
        else "Ficha de atendimento"
    )

    return [
        Paragraph(
            escapar_html(titulo),
            estilos["titulo"],
        ),
        Paragraph(
            escapar_html(
                f"{nome_cliente} • {identificacao}"
            ),
            estilos["subtitulo"],
        ),
        HRFlowable(
            width="100%",
            thickness=1,
            color=COR_SECUNDARIA,
            spaceBefore=0,
            spaceAfter=10,
        ),
    ]


# ============================================================
# GERAÇÃO PRINCIPAL
# ============================================================

def gerar_pdf_ficha(
    atendimento: Any,
    ficha: Any,
    titulo: str,
    secoes: list[tuple[str, tuple[str, ...]]],
    configuracao: Any = None,
) -> BytesIO:
    buffer = BytesIO()

    nome_escritorio = obter_nome_escritorio(configuracao)

    documento = DocumentoFichaPDF(
        buffer=buffer,
        titulo_rodape=titulo,
        nome_escritorio=nome_escritorio,
    )

    estilos = criar_estilos()
    elementos = []

    elementos.extend(
        criar_cabecalho_documento(
            titulo=titulo,
            atendimento=atendimento,
            estilos=estilos,
        )
    )

    adicionar_secao(
        elementos=elementos,
        titulo="Dados do cliente",
        dados=dados_cliente(atendimento),
        estilos=estilos,
    )

    adicionar_secao(
        elementos=elementos,
        titulo="Dados do atendimento",
        dados=dados_atendimento(atendimento),
        estilos=estilos,
    )

    campos_usados: set[str] = set()

    for titulo_secao, campos in secoes:
        dados = coletar_campos(
            objeto=ficha,
            campos=campos,
            usados=campos_usados,
        )

        adicionar_secao(
            elementos=elementos,
            titulo=titulo_secao,
            dados=dados,
            estilos=estilos,
        )

    campos_restantes = coletar_campos_restantes(
        objeto=ficha,
        usados=campos_usados,
    )

    adicionar_secao(
        elementos=elementos,
        titulo="Informações complementares",
        dados=campos_restantes,
        estilos=estilos,
    )

    elementos.append(Spacer(1, 0.3 * cm))

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=COR_BORDA,
            spaceBefore=5,
            spaceAfter=7,
        )
    )

    elementos.append(
        Paragraph(
            (
                "Documento gerado automaticamente pelo Sistema Jurídico. "
                "As informações apresentadas refletem os dados registrados "
                "na ficha de atendimento até o momento da emissão."
            ),
            estilos["aviso"],
        )
    )

    documento.build(elementos)

    buffer.seek(0)

    return buffer


def gerar_pdf_ficha_trabalhista(
    atendimento: Any,
    ficha: Any,
    configuracao: Any = None,
) -> BytesIO:
    return gerar_pdf_ficha(
        atendimento=atendimento,
        ficha=ficha,
        titulo="Ficha de Atendimento Trabalhista",
        secoes=SECOES_TRABALHISTAS,
        configuracao=configuracao,
    )


def gerar_pdf_ficha_previdenciaria(
    atendimento: Any,
    ficha: Any,
    configuracao: Any = None,
) -> BytesIO:
    return gerar_pdf_ficha(
        atendimento=atendimento,
        ficha=ficha,
        titulo="Ficha de Atendimento Previdenciário",
        secoes=SECOES_PREVIDENCIARIAS,
        configuracao=configuracao,
    )


def gerar_pdf_ficha_civel(
    atendimento: Any,
    ficha: Any,
    configuracao: Any = None,
) -> BytesIO:
    return gerar_pdf_ficha(
        atendimento=atendimento,
        ficha=ficha,
        titulo="Ficha de Atendimento Cível",
        secoes=SECOES_CIVEIS,
        configuracao=configuracao,
    )


def gerar_pdf_ficha_familia(
    atendimento: Any,
    ficha: Any,
    configuracao: Any = None,
) -> BytesIO:
    return gerar_pdf_ficha(
        atendimento=atendimento,
        ficha=ficha,
        titulo="Ficha de Atendimento de Direito de Família",
        secoes=SECOES_FAMILIA,
        configuracao=configuracao,
    )


# ============================================================
# NOMES AUTOMÁTICOS DOS ARQUIVOS
# ============================================================

def nome_pdf_trabalhista(atendimento: Any) -> str:
    cliente = nome_arquivo_seguro(
        obter_nome_cliente(atendimento)
    )

    atendimento_id = getattr(atendimento, "id", "sem_numero")

    return (
        f"ficha_trabalhista_{cliente}_"
        f"atendimento_{atendimento_id}.pdf"
    )


def nome_pdf_previdenciario(atendimento: Any) -> str:
    cliente = nome_arquivo_seguro(
        obter_nome_cliente(atendimento)
    )

    atendimento_id = getattr(atendimento, "id", "sem_numero")

    return (
        f"ficha_previdenciaria_{cliente}_"
        f"atendimento_{atendimento_id}.pdf"
    )

def nome_pdf_civel(atendimento: Any) -> str:
    cliente = nome_arquivo_seguro(
        obter_nome_cliente(atendimento)
    )

    atendimento_id = getattr(atendimento, "id", "sem_numero")

    return (
        f"ficha_civel_{cliente}_"
        f"atendimento_{atendimento_id}.pdf"
    )

def nome_pdf_familia(atendimento: Any) -> str:
    cliente = nome_arquivo_seguro(
        obter_nome_cliente(atendimento)
    )

    atendimento_id = getattr(atendimento, "id", "sem_numero")

    return (
        f"ficha_familia_{cliente}_"
        f"atendimento_{atendimento_id}.pdf"
    )