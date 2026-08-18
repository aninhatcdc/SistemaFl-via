from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

from sqlalchemy.exc import SQLAlchemyError

from models import db
from models.atendimento import Atendimento
from models.cliente import Cliente
from models.ficha_previdenciaria import FichaPrevidenciaria
from models.ficha_trabalhista import FichaTrabalhista
from models.ficha_civel import FichaCivel
from models.ficha_familia import FichaFamilia
from models.ficha_consumidor import FichaConsumidor

from services.pdf_fichas import (
    gerar_pdf_ficha_civel,
    gerar_pdf_ficha_familia,
    gerar_pdf_ficha_previdenciaria,
    gerar_pdf_ficha_trabalhista,
    nome_pdf_civel,
    nome_pdf_familia,
    nome_pdf_previdenciario,
    nome_pdf_trabalhista,
)


atendimento_bp = Blueprint(
    "atendimentos",
    __name__,
)


# ============================================================
# CONFIGURAÇÃO DAS ETAPAS DA FICHA TRABALHISTA
# ============================================================

ETAPAS_TRABALHISTAS = [
    {
        "codigo": "atendimento",
        "titulo": "Atendimento",
        "icone": "bi-clipboard2-pulse",
        "campo_conclusao": "etapa_atendimento_concluida",
    },
    {
        "codigo": "cliente",
        "titulo": "Cliente",
        "icone": "bi-person-vcard",
        "campo_conclusao": "etapa_cliente_concluida",
    },
    {
        "codigo": "empresa",
        "titulo": "Empresa",
        "icone": "bi-buildings",
        "campo_conclusao": "etapa_empresa_concluida",
    },
    {
        "codigo": "admissao",
        "titulo": "Admissão",
        "icone": "bi-person-check",
        "campo_conclusao": "etapa_admissao_concluida",
    },
    {
        "codigo": "contrato",
        "titulo": "Contrato",
        "icone": "bi-file-earmark-text",
        "campo_conclusao": "etapa_contrato_concluida",
    },
    {
        "codigo": "local",
        "titulo": "Local de trabalho",
        "icone": "bi-geo-alt",
        "campo_conclusao": "etapa_local_concluida",
    },
    {
        "codigo": "salario",
        "titulo": "Salário",
        "icone": "bi-cash-coin",
        "campo_conclusao": "etapa_salario_concluida",
    },
    {
        "codigo": "ferias",
        "titulo": "Férias",
        "icone": "bi-calendar2-week",
        "campo_conclusao": "etapa_ferias_concluida",
    },
    {
        "codigo": "decimo_terceiro",
        "titulo": "13º salário",
        "icone": "bi-wallet2",
        "campo_conclusao": "etapa_decimo_terceiro_concluida",
    },
    {
        "codigo": "rescisao",
        "titulo": "Rescisão",
        "icone": "bi-person-x",
        "campo_conclusao": "etapa_rescisao_concluida",
    },
]


# ============================================================
# FUNÇÕES AUXILIARES DE FORMULÁRIO
# ============================================================

def texto_formulario(nome_campo):
    """
    Recupera um texto do formulário, remove espaços no início
    e no final e devolve None quando estiver vazio.
    """

    valor = request.form.get(
        nome_campo,
        "",
    ).strip()

    return valor or None


def inteiro_formulario(nome_campo):
    """
    Recupera um número inteiro do formulário.
    """

    valor = request.form.get(
        nome_campo,
        "",
    ).strip()

    if not valor:
        return None

    try:
        return int(valor)

    except ValueError:
        return None


def decimal_formulario(nome_campo):
    """
    Recupera um valor monetário do formulário.

    Aceita valores como 1500.50, 1.500,50 e 1500,50.
    """

    valor = request.form.get(
        nome_campo,
        "",
    ).strip()

    if not valor:
        return None

    valor = valor.replace("R$", "").replace(" ", "")

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return Decimal(valor)

    except InvalidOperation as erro:
        raise ValueError(
            f"O campo {nome_campo} possui um valor monetário inválido."
        ) from erro


def data_formulario(nome_campo):
    """
    Converte uma data no formato YYYY-MM-DD para um objeto date.
    """

    valor = request.form.get(
        nome_campo,
        "",
    ).strip()

    if not valor:
        return None

    return datetime.strptime(
        valor,
        "%Y-%m-%d",
    ).date()


def horario_formulario(nome_campo):
    """
    Converte um horário no formato HH:MM para um objeto time.
    """

    valor = request.form.get(
        nome_campo,
        "",
    ).strip()

    if not valor:
        return None

    return datetime.strptime(
        valor,
        "%H:%M",
    ).time()


def area_valida(area):
    """
    Verifica se a área enviada existe nas opções do modelo
    Atendimento.
    """

    return area in Atendimento.AREAS


# ============================================================
# FUNÇÕES AUXILIARES DA FICHA TRABALHISTA
# ============================================================

def buscar_atendimento_trabalhista(atendimento_id):
    """
    Busca o atendimento e confirma que ele pertence à área
    trabalhista.
    """

    atendimento = Atendimento.query.get_or_404(
        atendimento_id,
    )

    if atendimento.area != Atendimento.AREA_TRABALHISTA:
        flash(
            "Este atendimento não pertence à área trabalhista.",
            "warning",
        )

        return None

    return atendimento


def obter_ou_criar_ficha(atendimento):
    """
    Recupera a ficha trabalhista do atendimento.

    Caso ainda não exista, cria uma nova ficha vinculada ao
    atendimento.
    """

    ficha = atendimento.ficha_trabalhista

    if ficha is not None:
        return ficha

    ficha = FichaTrabalhista(
        atendimento_id=atendimento.id,
        criado_por_id=current_user.id,
        atualizado_por_id=current_user.id,
    )

    try:
        db.session.add(ficha)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível criar a ficha trabalhista.",
            "danger",
        )

        return None

    return ficha


def etapa_concluida(ficha, campo_conclusao):
    """
    Verifica com segurança se determinada etapa foi marcada
    como concluída.
    """

    return bool(
        getattr(
            ficha,
            campo_conclusao,
            False,
        )
    )


def calcular_progresso(ficha):
    """
    Calcula o percentual de conclusão com base nas dez etapas
    da ficha trabalhista.
    """

    total_etapas = len(ETAPAS_TRABALHISTAS)

    if total_etapas == 0:
        return 0

    etapas_concluidas = 0

    for etapa in ETAPAS_TRABALHISTAS:
        if etapa_concluida(
            ficha,
            etapa["campo_conclusao"],
        ):
            etapas_concluidas += 1

    return int(
        etapas_concluidas * 100 / total_etapas
    )


def montar_etapas_navegacao(ficha, atendimento_id):
    """
    Monta a lista exibida no menu lateral.

    Neste momento, somente a primeira etapa possui uma página
    implementada. As demais serão ativadas conforme criarmos
    seus respectivos templates e rotas.
    """

    etapas = []

    for etapa_configurada in ETAPAS_TRABALHISTAS:
        etapa = {
            "codigo": etapa_configurada["codigo"],
            "titulo": etapa_configurada["titulo"],
            "icone": etapa_configurada["icone"],
            "concluida": etapa_concluida(
                ficha,
                etapa_configurada["campo_conclusao"],
            ),
            "url": "#",
        }

        if etapa["codigo"] == "atendimento":
            etapa["url"] = url_for(
                "atendimentos.etapa_atendimento",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "cliente":
            etapa["url"] = url_for(
                "atendimentos.etapa_cliente",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "empresa":
            etapa["url"] = url_for(
                "atendimentos.etapa_empresa",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "admissao":
            etapa["url"] = url_for(
                "atendimentos.etapa_admissao",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "contrato":
            etapa["url"] = url_for(
                "atendimentos.etapa_contrato",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "local":
            etapa["url"] = url_for(
                "atendimentos.etapa_local_trabalho",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "salario":
            etapa["url"] = url_for(
                "atendimentos.etapa_salario",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "ferias":
            etapa["url"] = url_for(
                "atendimentos.etapa_ferias",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "decimo_terceiro":
            etapa["url"] = url_for(
                "atendimentos.etapa_decimo_terceiro",
                atendimento_id=atendimento_id,
            )

        elif etapa["codigo"] == "rescisao":
            etapa["url"] = url_for(
                "atendimentos.etapa_rescisao",
                atendimento_id=atendimento_id,
            )

        etapas.append(etapa)

    return etapas


def contexto_etapa(
    atendimento,
    ficha,
    etapa_atual,
    url_anterior=None,
    url_proxima=None,
):
    """
    Cria o contexto padrão utilizado pelos templates das etapas.
    """

    return {
        "atendimento": atendimento,
        "ficha": ficha,
        "etapa_atual": etapa_atual,
        "etapas": montar_etapas_navegacao(
            ficha,
            atendimento.id,
        ),
        "progresso": calcular_progresso(ficha),
        "url_anterior": url_anterior,
        "url_proxima": url_proxima,
        "respostas": getattr(
            FichaTrabalhista,
            "RESPOSTAS",
            {},
        ),
        "escolaridades": getattr(
            FichaTrabalhista,
            "ESCOLARIDADES",
            {},
        ),
        "status_atendimento": Atendimento.STATUS,
    }


def salvar_auditoria(atendimento, ficha):
    """
    Atualiza os campos de auditoria do atendimento e da ficha.
    """

    agora = datetime.utcnow()

    atendimento.atualizado_por_id = current_user.id
    atendimento.atualizado_em = agora

    ficha.atualizado_por_id = current_user.id
    ficha.atualizado_em = agora


# ============================================================
# CONFIGURAÇÃO E FUNÇÕES AUXILIARES DA FICHA PREVIDENCIÁRIA
# ============================================================

ETAPAS_PREVIDENCIARIAS = [
    {
        "codigo": "atendimento",
        "titulo": "Atendimento",
        "icone": "bi-clipboard2-pulse",
        "campo_conclusao": "etapa_atendimento_concluida",
        "endpoint": "atendimentos.etapa_atendimento_previdenciario",
    },
    {
        "codigo": "segurado",
        "titulo": "Segurado",
        "icone": "bi-person-vcard",
        "campo_conclusao": "etapa_segurado_concluida",
        "endpoint": "atendimentos.etapa_segurado_previdenciario",
    },
    {
        "codigo": "historico_contributivo",
        "titulo": "Histórico contributivo",
        "icone": "bi-clock-history",
        "campo_conclusao": "etapa_historico_contributivo_concluida",
        "endpoint": (
            "atendimentos.etapa_historico_contributivo_previdenciario"
        ),
    },
    {
        "codigo": "beneficio",
        "titulo": "Benefício",
        "icone": "bi-shield-check",
        "campo_conclusao": "etapa_beneficio_concluida",
        "endpoint": "atendimentos.etapa_beneficio_previdenciario",
    },
    {
        "codigo": "saude",
        "titulo": "Saúde e incapacidade",
        "icone": "bi-heart-pulse",
        "campo_conclusao": "etapa_saude_concluida",
        "endpoint": "atendimentos.etapa_saude_previdenciario",
    },
    {
        "codigo": "documentacao",
        "titulo": "Documentação",
        "icone": "bi-folder-check",
        "campo_conclusao": "etapa_documentacao_concluida",
        "endpoint": "atendimentos.etapa_documentacao_previdenciario",
    },
    {
        "codigo": "inss",
        "titulo": "Processo no INSS",
        "icone": "bi-building",
        "campo_conclusao": "etapa_inss_concluida",
        "endpoint": "atendimentos.etapa_inss_previdenciario",
    },
    {
        "codigo": "resumo",
        "titulo": "Resumo e análise",
        "icone": "bi-clipboard-check",
        "campo_conclusao": "etapa_resumo_concluida",
        "endpoint": "atendimentos.etapa_resumo_previdenciario",
    },
]


def buscar_atendimento_previdenciario(atendimento_id):
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    if atendimento.area != Atendimento.AREA_PREVIDENCIARIA:
        flash(
            "Este atendimento não pertence à área previdenciária.",
            "warning",
        )
        return None

    return atendimento


def obter_ou_criar_ficha_previdenciaria(atendimento):
    ficha = atendimento.ficha_previdenciaria

    if ficha is not None:
        return ficha

    ficha = FichaPrevidenciaria(
        atendimento_id=atendimento.id,
        etapa_atual="atendimento",
        criado_por_id=current_user.id,
        atualizado_por_id=current_user.id,
    )

    try:
        db.session.add(ficha)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "Não foi possível criar a ficha previdenciária.",
            "danger",
        )
        return None

    return ficha


def montar_etapas_previdenciarias(ficha, atendimento_id):
    etapas = []

    for configuracao in ETAPAS_PREVIDENCIARIAS:
        endpoint = configuracao["endpoint"]
        etapa = {
            "codigo": configuracao["codigo"],
            "titulo": configuracao["titulo"],
            "icone": configuracao["icone"],
            "concluida": bool(
                getattr(
                    ficha,
                    configuracao["campo_conclusao"],
                    False,
                )
            ),
            "url": (
                url_for(endpoint, atendimento_id=atendimento_id)
                if endpoint
                else "#"
            ),
            "disponivel": endpoint is not None,
        }
        etapas.append(etapa)

    return etapas


def contexto_etapa_previdenciaria(
    atendimento,
    ficha,
    etapa_atual,
    url_anterior=None,
    url_proxima=None,
):
    return {
        "atendimento": atendimento,
        "ficha": ficha,
        "etapa_atual": etapa_atual,
        "etapas": montar_etapas_previdenciarias(
            ficha,
            atendimento.id,
        ),
        "progresso": ficha.progresso_percentual,
        "url_anterior": url_anterior,
        "url_proxima": url_proxima,
        "status_atendimento": Atendimento.STATUS,
        "respostas": FichaPrevidenciaria.RESPOSTAS,
        "escolaridades": FichaPrevidenciaria.ESCOLARIDADES,
        "categorias_segurado": FichaPrevidenciaria.CATEGORIAS_SEGURADO,
        "situacoes_profissionais": (
            FichaPrevidenciaria.SITUACOES_PROFISSIONAIS
        ),
        "tipos_beneficio": FichaPrevidenciaria.TIPOS_BENEFICIO,
        "tipos_incapacidade": FichaPrevidenciaria.TIPOS_INCAPACIDADE,
        "origens_incapacidade": (
            FichaPrevidenciaria.ORIGENS_INCAPACIDADE
        ),
    }

# ============================================================
# CONFIGURAÇÃO E FUNÇÕES AUXILIARES DA FICHA CÍVEL
# ============================================================

ETAPAS_CIVEIS = [
    {
        "codigo": "atendimento",
        "titulo": "Atendimento",
        "icone": "bi-clipboard2-pulse",
        "campo_conclusao": "etapa_atendimento_concluida",
        "endpoint": "atendimentos.etapa_atendimento_civel",
    },
    {
        "codigo": "cliente",
        "titulo": "Cliente",
        "icone": "bi-person-vcard",
        "campo_conclusao": "etapa_cliente_concluida",
        "endpoint":"atendimentos.etapa_cliente_civel",
    },
    {
        "codigo": "parte_contraria",
        "titulo": "Parte contrária",
        "icone": "bi-people",
        "campo_conclusao": "etapa_parte_contraria_concluida",
        "endpoint":"atendimentos.etapa_parte_contraria_civel",
    },
    {
        "codigo": "fatos",
        "titulo": "Fatos",
        "icone": "bi-journal-text",
        "campo_conclusao": "etapa_fatos_concluida",
        "endpoint":"atendimentos.etapa_fatos_civel" ,
    },
    {
        "codigo": "contrato",
        "titulo": "Contratos e obrigações",
        "icone": "bi-file-earmark-text",
        "campo_conclusao": "etapa_contrato_concluida",
        "endpoint": "atendimentos.etapa_contrato_civel",
    },
    {
        "codigo": "danos",
        "titulo": "Danos e valores",
        "icone": "bi-cash-coin",
        "campo_conclusao": "etapa_danos_concluida",
        "endpoint": "atendimentos.etapa_danos_civel",
    },
    {
        "codigo": "tentativas",
        "titulo": "Tentativas de solução",
        "icone": "bi-chat-left-text",
        "campo_conclusao": "etapa_tentativas_concluida",
        "endpoint": "atendimentos.etapa_tentativas_civel",
    },
    {
        "codigo": "documentos",
        "titulo": "Documentos",
        "icone": "bi-folder-check",
        "campo_conclusao": "etapa_documentos_concluida",
        "endpoint": "atendimentos.etapa_documentos_civel",
    },
    {
        "codigo": "analise",
        "titulo": "Análise jurídica",
        "icone": "bi-clipboard-check",
        "campo_conclusao": "etapa_analise_concluida",
        "endpoint": "atendimentos.etapa_analise_civel",
    },
]


def buscar_atendimento_civel(atendimento_id):
    """
    Busca o atendimento e confirma que ele pertence à área cível.
    """

    atendimento = Atendimento.query.get_or_404(
        atendimento_id,
    )

    if atendimento.area != Atendimento.AREA_CIVEL:
        flash(
            "Este atendimento não pertence à área cível.",
            "warning",
        )

        return None

    return atendimento


def obter_ou_criar_ficha_civel(atendimento):
    """
    Recupera a ficha cível do atendimento.

    Caso ainda não exista, cria uma nova ficha vinculada ao
    atendimento.
    """

    ficha = atendimento.ficha_civel

    if ficha is not None:
        return ficha

    ficha = FichaCivel(
        atendimento_id=atendimento.id,
        etapa_atual="atendimento",
        criado_por_id=current_user.id,
        atualizado_por_id=current_user.id,
    )

    try:
        db.session.add(ficha)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível criar a ficha cível.",
            "danger",
        )

        return None

    return ficha


def montar_etapas_civeis(ficha, atendimento_id):
    """
    Monta as etapas exibidas no menu lateral da ficha cível.
    """

    etapas = []

    for configuracao in ETAPAS_CIVEIS:
        endpoint = configuracao["endpoint"]

        etapa = {
            "codigo": configuracao["codigo"],
            "titulo": configuracao["titulo"],
            "icone": configuracao["icone"],
            "concluida": bool(
                getattr(
                    ficha,
                    configuracao["campo_conclusao"],
                    False,
                )
            ),
            "url": (
                url_for(
                    endpoint,
                    atendimento_id=atendimento_id,
                )
                if endpoint
                else "#"
            ),
            "disponivel": endpoint is not None,
        }

        etapas.append(etapa)

    return etapas


def contexto_etapa_civel(
    atendimento,
    ficha,
    etapa_atual,
    url_anterior=None,
    url_proxima=None,
):
    """
    Cria o contexto padrão utilizado pelos templates cíveis.
    """

    return {
        "atendimento": atendimento,
        "cliente": atendimento.cliente,
        "ficha": ficha,
        "etapa_atual": etapa_atual,
        "etapas": montar_etapas_civeis(
            ficha,
            atendimento.id,
        ),
        "progresso": ficha.progresso_percentual,
        "url_anterior": url_anterior,
        "url_proxima": url_proxima,
        "status_atendimento": Atendimento.STATUS,
        "respostas": FichaCivel.RESPOSTAS,
        "naturezas_demanda": FichaCivel.NATUREZAS,
    }

# ============================================================
# CONFIGURAÇÃO E FUNÇÕES AUXILIARES DA FICHA DE FAMÍLIA
# ============================================================

ETAPAS_FAMILIA = [
    {
        "codigo": "atendimento",
        "titulo": "Atendimento",
        "icone": "bi-clipboard2-pulse",
        "campo_conclusao": "etapa_atendimento_concluida",
        "endpoint": "atendimentos.etapa_atendimento_familia",
    },
    {
        "codigo": "cliente",
        "titulo": "Cliente",
        "icone": "bi-person-vcard",
        "campo_conclusao": "etapa_cliente_concluida",
        "endpoint": "atendimentos.etapa_cliente_familia",
    },
    {
        "codigo": "relacao_familiar",
        "titulo": "Relação familiar",
        "icone": "bi-heart",
        "campo_conclusao": "etapa_relacao_familiar_concluida",
        "endpoint": "atendimentos.etapa_relacao_familiar",
    },
    {
        "codigo": "parte_contraria",
        "titulo": "Parte contrária",
        "icone": "bi-people",
        "campo_conclusao": "etapa_parte_contraria_concluida",
        "endpoint": "atendimentos.etapa_parte_contraria_familia",
    },
    {
        "codigo": "filhos",
        "titulo": "Filhos",
        "icone": "bi-person-hearts",
        "campo_conclusao": "etapa_filhos_concluida",
        "endpoint": "atendimentos.etapa_filhos_familia",
    },
    {
        "codigo": "guarda",
        "titulo": "Guarda e convivência",
        "icone": "bi-house-heart",
        "campo_conclusao": "etapa_guarda_concluida",
        "endpoint": "atendimentos.etapa_guarda_familia",
    },
    {
        "codigo": "alimentos",
        "titulo": "Alimentos",
        "icone": "bi-cash-coin",
        "campo_conclusao": "etapa_alimentos_concluida",
        "endpoint": "atendimentos.etapa_alimentos_familia",
    },
    {
        "codigo": "patrimonio",
        "titulo": "Patrimônio",
        "icone": "bi-buildings",
        "campo_conclusao": "etapa_patrimonio_concluida",
        "endpoint": "atendimentos.etapa_patrimonio_familia",
    },
    {
        "codigo": "documentos",
        "titulo": "Documentos",
        "icone": "bi-folder-check",
        "campo_conclusao": "etapa_documentos_concluida",
        "endpoint": "atendimentos.etapa_documentos_familia",
    },
    {
        "codigo": "analise",
        "titulo": "Análise jurídica",
        "icone": "bi-clipboard-check",
        "campo_conclusao": "etapa_analise_concluida",
        "endpoint": "atendimentos.etapa_analise_familia",
    },
]


def buscar_atendimento_familia(atendimento_id):
    atendimento = Atendimento.query.get_or_404(atendimento_id)

    if atendimento.area != Atendimento.AREA_FAMILIA:
        flash(
            "Este atendimento não pertence à área de Família.",
            "warning",
        )
        return None

    return atendimento


def obter_ou_criar_ficha_familia(atendimento):
    ficha = atendimento.ficha_familia

    if ficha is not None:
        return ficha

    ficha = FichaFamilia(
        atendimento_id=atendimento.id,
        cliente_id=atendimento.cliente_id,
        etapa_atual="atendimento",
        criado_por_id=current_user.id,
        atualizado_por_id=current_user.id,
    )

    try:
        db.session.add(ficha)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "Não foi possível criar a ficha de Família.",
            "danger",
        )
        return None

    return ficha


def montar_etapas_familia(ficha, atendimento_id):
    etapas = []

    for configuracao in ETAPAS_FAMILIA:
        endpoint = configuracao["endpoint"]

        etapas.append(
            {
                "codigo": configuracao["codigo"],
                "titulo": configuracao["titulo"],
                "icone": configuracao["icone"],
                "concluida": bool(
                    getattr(
                        ficha,
                        configuracao["campo_conclusao"],
                        False,
                    )
                ),
                "url": (
                    url_for(
                        endpoint,
                        atendimento_id=atendimento_id,
                    )
                    if endpoint
                    else "#"
                ),
                "disponivel": endpoint is not None,
            }
        )

    return etapas


def contexto_etapa_familia(
    atendimento,
    ficha,
    etapa_atual,
    url_anterior=None,
    url_proxima=None,
):
    return {
        "atendimento": atendimento,
        "cliente": atendimento.cliente,
        "ficha": ficha,
        "etapa_atual": etapa_atual,
        "etapas": montar_etapas_familia(
            ficha,
            atendimento.id,
        ),
        "progresso": ficha.progresso_percentual,
        "url_anterior": url_anterior,
        "url_proxima": url_proxima,
        "status_atendimento": Atendimento.STATUS,
        "tipos_demanda": FichaFamilia.TIPOS_DEMANDA,
        "tipos_relacao": FichaFamilia.TIPOS_RELACAO,
        "regimes_bens": FichaFamilia.REGIMES_BENS,
        "tipos_guarda": FichaFamilia.TIPOS_GUARDA,
        "viabilidades": FichaFamilia.VIABILIDADES,
    }




# ============================================================
# CONFIGURAÇÃO E FUNÇÕES AUXILIARES DA FICHA DO CONSUMIDOR
# ============================================================

ETAPAS_CONSUMIDOR = [
    {
        "codigo": "atendimento",
        "titulo": "Atendimento",
        "icone": "bi-clipboard2-pulse",
        "campo_conclusao": "etapa_atendimento_concluida",
        "endpoint": "atendimentos.etapa_atendimento_consumidor",
    },
    {
        "codigo": "consumidor",
        "titulo": "Consumidor",
        "icone": "bi-person-vcard",
        "campo_conclusao": "etapa_consumidor_concluida",
        "endpoint": "atendimentos.etapa_consumidor_consumidor",
    },
    {
        "codigo": "fornecedor",
        "titulo": "Fornecedor",
        "icone": "bi-buildings",
        "campo_conclusao": "etapa_fornecedor_concluida",
        "endpoint": None,
    },
    {
        "codigo": "produto_servico",
        "titulo": "Produto / Serviço",
        "icone": "bi-box-seam",
        "campo_conclusao": "etapa_produto_servico_concluida",
        "endpoint": None,
    },
    {
        "codigo": "problema",
        "titulo": "Problema",
        "icone": "bi-exclamation-triangle",
        "campo_conclusao": "etapa_problema_concluida",
        "endpoint": None,
    },
    {
        "codigo": "tentativas",
        "titulo": "Tentativas de solução",
        "icone": "bi-chat-left-text",
        "campo_conclusao": "etapa_tentativas_concluida",
        "endpoint": None,
    },
    {
        "codigo": "prejuizos",
        "titulo": "Prejuízos",
        "icone": "bi-cash-coin",
        "campo_conclusao": "etapa_prejuizos_concluida",
        "endpoint": None,
    },
    {
        "codigo": "documentos",
        "titulo": "Documentos",
        "icone": "bi-folder-check",
        "campo_conclusao": "etapa_documentos_concluida",
        "endpoint": None,
    },
    {
        "codigo": "pedidos",
        "titulo": "Pedido do cliente",
        "icone": "bi-list-check",
        "campo_conclusao": "etapa_pedidos_concluida",
        "endpoint": None,
    },
    {
        "codigo": "analise",
        "titulo": "Análise jurídica",
        "icone": "bi-clipboard-check",
        "campo_conclusao": "etapa_analise_concluida",
        "endpoint": None,
    },
]


def buscar_atendimento_consumidor(atendimento_id):
    """
    Busca o atendimento e confirma que ele pertence à área
    de Direito do Consumidor.
    """

    atendimento = Atendimento.query.get_or_404(
        atendimento_id,
    )

    if atendimento.area != Atendimento.AREA_CONSUMIDOR:
        flash(
            "Este atendimento não pertence à área de Direito do Consumidor.",
            "warning",
        )
        return None

    return atendimento


def obter_ou_criar_ficha_consumidor(atendimento):
    """
    Recupera a ficha do consumidor vinculada ao atendimento.

    Caso ainda não exista, cria uma nova ficha.
    """

    ficha = atendimento.ficha_consumidor

    if ficha is not None:
        return ficha

    ficha = FichaConsumidor(
        atendimento_id=atendimento.id,
        cliente_id=atendimento.cliente_id,
        etapa_atual="atendimento",
        criado_por_id=current_user.id,
        atualizado_por_id=current_user.id,
    )

    try:
        db.session.add(ficha)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        flash(
            "Não foi possível criar a ficha de Direito do Consumidor.",
            "danger",
        )

        return None

    return ficha


def montar_etapas_consumidor(ficha, atendimento_id):
    """
    Monta as etapas exibidas no menu lateral da ficha do consumidor.
    """

    etapas = []

    for configuracao in ETAPAS_CONSUMIDOR:
        endpoint = configuracao["endpoint"]

        etapas.append(
            {
                "codigo": configuracao["codigo"],
                "titulo": configuracao["titulo"],
                "icone": configuracao["icone"],
                "concluida": bool(
                    getattr(
                        ficha,
                        configuracao["campo_conclusao"],
                        False,
                    )
                ),
                "url": (
                    url_for(
                        endpoint,
                        atendimento_id=atendimento_id,
                    )
                    if endpoint
                    else "#"
                ),
                "disponivel": endpoint is not None,
            }
        )

    return etapas


def contexto_etapa_consumidor(
    atendimento,
    ficha,
    etapa_atual,
    url_anterior=None,
    url_proxima=None,
):
    """
    Cria o contexto padrão utilizado pelos templates da ficha
    de Direito do Consumidor.
    """

    return {
        "atendimento": atendimento,
        "cliente": atendimento.cliente,
        "ficha": ficha,
        "etapa_atual": etapa_atual,
        "etapas": montar_etapas_consumidor(
            ficha,
            atendimento.id,
        ),
        "progresso": ficha.progresso_percentual,
        "url_anterior": url_anterior,
        "url_proxima": url_proxima,
        "status_atendimento": Atendimento.STATUS,
        "tipos_demanda": getattr(
            FichaConsumidor,
            "TIPOS_DEMANDA",
            {},
        ),
        "tipos_fornecedor": getattr(
            FichaConsumidor,
            "TIPOS_FORNECEDOR",
            {},
        ),
        "tipos_objeto": getattr(
            FichaConsumidor,
            "TIPOS_OBJETO",
            {},
        ),
        "formas_pagamento": getattr(
            FichaConsumidor,
            "FORMAS_PAGAMENTO",
            {},
        ),
        "canais_reclamacao": getattr(
            FichaConsumidor,
            "CANAIS_RECLAMACAO",
            {},
        ),
        "viabilidades": getattr(
            FichaConsumidor,
            "VIABILIDADES",
            {},
        ),
    }


# ============================================================
# ENTRADA E ETAPA 1 DA FICHA DE FAMÍLIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia",
    methods=["GET"],
)
@login_required
def ficha_familia(atendimento_id):
    return redirect(
        url_for(
            "atendimentos.etapa_atendimento_familia",
            atendimento_id=atendimento_id,
        )
    )


@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/atendimento",
    methods=["GET", "POST"],
)
@login_required
def etapa_atendimento_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        titulo = texto_formulario("titulo")
        status = request.form.get(
            "status",
            Atendimento.STATUS_RASCUNHO,
        ).strip()

        if not titulo:
            flash(
                "Informe o título do atendimento.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/atendimento.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_cliente_familia",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if status not in Atendimento.STATUS:
            status = Atendimento.STATUS_RASCUNHO

        try:
            data_atendimento = data_formulario("data_atendimento")
            horario_atendimento = horario_formulario(
                "horario_atendimento"
            )
        except ValueError:
            flash(
                "Informe uma data e um horário válidos.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/atendimento.html",
                **contexto_etapa_familia(
                    atendimento,
                    ficha,
                    "atendimento",
                ),
            )

        if data_atendimento is None:
            flash(
                "Informe a data do atendimento.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/atendimento.html",
                **contexto_etapa_familia(
                    atendimento,
                    ficha,
                    "atendimento",
                ),
            )

        tipo_demanda = texto_formulario("tipo_demanda")

        if tipo_demanda not in FichaFamilia.TIPOS_DEMANDA:
            tipo_demanda = None

        atendimento.titulo = titulo
        atendimento.status = status
        atendimento.data_atendimento = data_atendimento
        atendimento.horario_atendimento = horario_atendimento
        atendimento.resumo_caso = texto_formulario("resumo_caso")
        atendimento.observacoes_internas = texto_formulario(
            "observacoes_internas"
        )

        ficha.cliente_id = atendimento.cliente_id
        ficha.tipo_demanda = tipo_demanda
        ficha.outro_tipo_demanda = texto_formulario(
            "outro_tipo_demanda"
        )
        ficha.motivo_principal = texto_formulario("motivo_principal")
        ficha.existe_urgencia = (
            request.form.get("existe_urgencia") == "on"
        )
        ficha.descricao_urgencia = texto_formulario(
            "descricao_urgencia"
        )
        ficha.existe_processo_anterior = (
            request.form.get("existe_processo_anterior") == "on"
        )
        ficha.numero_processo_anterior = texto_formulario(
            "numero_processo_anterior"
        )
        ficha.vara_processo_anterior = texto_formulario(
            "vara_processo_anterior"
        )
        ficha.comarca_processo_anterior = texto_formulario(
            "comarca_processo_anterior"
        )
        ficha.observacoes_atendimento = texto_formulario(
            "observacoes_atendimento"
        )

        if ficha.tipo_demanda != "OUTRA":
            ficha.outro_tipo_demanda = None

        if not ficha.existe_urgencia:
            ficha.descricao_urgencia = None

        if not ficha.existe_processo_anterior:
            ficha.numero_processo_anterior = None
            ficha.vara_processo_anterior = None
            ficha.comarca_processo_anterior = None

        ficha.etapa_atual = "atendimento"
        ficha.etapa_atendimento_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar o atendimento de Família.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/atendimento.html",
                **contexto_etapa_familia(
                    atendimento,
                    ficha,
                    "atendimento",
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Atendimento de Família salvo com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_cliente_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Atendimento de Família salvo com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_atendimento_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/atendimento.html",
        **contexto_etapa_familia(
            atendimento,
            ficha,
            "atendimento",
        ),
    )



# ============================================================
# ETAPA 2 — CLIENTE DA FICHA DE FAMÍLIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/cliente",
    methods=["GET", "POST"],
)
@login_required
def etapa_cliente_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_atendimento_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.cliente_id = atendimento.cliente_id

        ficha.cliente_estado_civil = texto_formulario(
            "cliente_estado_civil"
        )

        ficha.cliente_profissao = texto_formulario(
            "cliente_profissao"
        )

        try:
            ficha.cliente_renda_mensal = decimal_formulario(
                "cliente_renda_mensal"
            )
        except ValueError:
            flash(
                "Informe uma renda mensal válida.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/cliente.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="cliente",
                    url_anterior=url_anterior,
                ),
            )

        ficha.cliente_reside_com_quem = texto_formulario(
            "cliente_reside_com_quem"
        )

        ficha.cliente_dependentes = texto_formulario(
            "cliente_dependentes"
        )

        ficha.cliente_possui_deficiencia = (
            request.form.get("cliente_possui_deficiencia") == "on"
        )

        ficha.cliente_descricao_deficiencia = texto_formulario(
            "cliente_descricao_deficiencia"
        )

        ficha.cliente_recebe_beneficio = (
            request.form.get("cliente_recebe_beneficio") == "on"
        )

        ficha.cliente_beneficio_descricao = texto_formulario(
            "cliente_beneficio_descricao"
        )

        ficha.observacoes_cliente = texto_formulario(
            "observacoes_cliente"
        )

        if not ficha.cliente_possui_deficiencia:
            ficha.cliente_descricao_deficiencia = None

        if not ficha.cliente_recebe_beneficio:
            ficha.cliente_beneficio_descricao = None

        ficha.etapa_atual = "cliente"
        ficha.etapa_cliente_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do cliente.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/cliente.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="cliente",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        print("AÇÃO RECEBIDA:", repr(acao))

        if acao == "salvar_proxima":
            flash(
                "✅ Dados do cliente salvos com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_relacao_familiar",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Dados do cliente salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_cliente_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/cliente.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="cliente",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 3 — RELAÇÃO FAMILIAR
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/relacao-familiar",
    methods=["GET", "POST"],
)
@login_required
def etapa_relacao_familiar(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_cliente_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        tipo_relacao = texto_formulario("tipo_relacao")

        if tipo_relacao not in FichaFamilia.TIPOS_RELACAO:
            tipo_relacao = None

        regime_bens = texto_formulario("regime_bens")

        if regime_bens not in FichaFamilia.REGIMES_BENS:
            regime_bens = None

        try:
            data_inicio_relacao = data_formulario(
                "data_inicio_relacao"
            )

            data_casamento = data_formulario(
                "data_casamento"
            )

            data_separacao_fato = data_formulario(
                "data_separacao_fato"
            )

        except ValueError:
            flash(
                "Informe datas válidas na etapa Relação familiar.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/relacao_familiar.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="relacao_familiar",
                    url_anterior=url_anterior,
                ),
            )

        ficha.tipo_relacao = tipo_relacao
        ficha.data_inicio_relacao = data_inicio_relacao
        ficha.data_casamento = data_casamento
        ficha.data_separacao_fato = data_separacao_fato
        ficha.regime_bens = regime_bens

        ficha.possui_pacto_antenupcial = (
            request.form.get("possui_pacto_antenupcial") == "on"
        )

        ficha.descricao_pacto_antenupcial = texto_formulario(
            "descricao_pacto_antenupcial"
        )

        ficha.convivencia_publica_continua = (
            request.form.get("convivencia_publica_continua") == "on"
        )

        ficha.objetivo_constituir_familia = (
            request.form.get("objetivo_constituir_familia") == "on"
        )

        ficha.relacao_encerrada = (
            request.form.get("relacao_encerrada") == "on"
        )

        ficha.motivo_termino_relacao = texto_formulario(
            "motivo_termino_relacao"
        )

        ficha.houve_violencia_domestica = (
            request.form.get("houve_violencia_domestica") == "on"
        )

        ficha.descricao_violencia_domestica = texto_formulario(
            "descricao_violencia_domestica"
        )

        ficha.existe_medida_protetiva = (
            request.form.get("existe_medida_protetiva") == "on"
        )

        ficha.numero_medida_protetiva = texto_formulario(
            "numero_medida_protetiva"
        )

        ficha.observacoes_relacao = texto_formulario(
            "observacoes_relacao"
        )

        if not ficha.possui_pacto_antenupcial:
            ficha.descricao_pacto_antenupcial = None

        if not ficha.relacao_encerrada:
            ficha.motivo_termino_relacao = None
            ficha.data_separacao_fato = None

        if not ficha.houve_violencia_domestica:
            ficha.descricao_violencia_domestica = None
            ficha.existe_medida_protetiva = False
            ficha.numero_medida_protetiva = None

        if not ficha.existe_medida_protetiva:
            ficha.numero_medida_protetiva = None

        ficha.etapa_atual = "relacao_familiar"
        ficha.etapa_relacao_familiar_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da relação familiar.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/relacao_familiar.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="relacao_familiar",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Relação familiar salva com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_parte_contraria_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Relação familiar salva com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_relacao_familiar",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/relacao_familiar.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="relacao_familiar",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 4 — PARTE CONTRÁRIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/parte-contraria",
    methods=["GET", "POST"],
)
@login_required
def etapa_parte_contraria_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_relacao_familiar",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        try:
            parte_contraria_data_nascimento = data_formulario(
                "parte_contraria_data_nascimento"
            )

            parte_contraria_renda_mensal = decimal_formulario(
                "parte_contraria_renda_mensal"
            )

        except ValueError:
            flash(
                "Informe uma data de nascimento e uma renda mensal válidas.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/parte_contraria.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="parte_contraria",
                    url_anterior=url_anterior,
                ),
            )

        ficha.parte_contraria_nome = texto_formulario(
            "parte_contraria_nome"
        )

        ficha.parte_contraria_cpf = texto_formulario(
            "parte_contraria_cpf"
        )

        ficha.parte_contraria_rg = texto_formulario(
            "parte_contraria_rg"
        )

        ficha.parte_contraria_data_nascimento = (
            parte_contraria_data_nascimento
        )

        ficha.parte_contraria_profissao = texto_formulario(
            "parte_contraria_profissao"
        )

        ficha.parte_contraria_renda_mensal = (
            parte_contraria_renda_mensal
        )

        ficha.parte_contraria_telefone = texto_formulario(
            "parte_contraria_telefone"
        )

        ficha.parte_contraria_email = texto_formulario(
            "parte_contraria_email"
        )

        ficha.parte_contraria_endereco = texto_formulario(
            "parte_contraria_endereco"
        )

        ficha.parte_contraria_cidade = texto_formulario(
            "parte_contraria_cidade"
        )

        ficha.parte_contraria_estado = texto_formulario(
            "parte_contraria_estado"
        )

        if ficha.parte_contraria_estado:
            ficha.parte_contraria_estado = (
                ficha.parte_contraria_estado.upper()[:2]
            )

        ficha.parte_contraria_local_trabalho = texto_formulario(
            "parte_contraria_local_trabalho"
        )

        ficha.comunicacao_entre_partes = texto_formulario(
            "comunicacao_entre_partes"
        )

        ficha.observacoes_parte_contraria = texto_formulario(
            "observacoes_parte_contraria"
        )

        ficha.etapa_atual = "parte_contraria"
        ficha.etapa_parte_contraria_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da parte contrária.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/parte_contraria.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="parte_contraria",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Dados da parte contrária salvos com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_filhos_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Dados da parte contrária salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_parte_contraria_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/parte_contraria.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="parte_contraria",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 5 — FILHOS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/filhos",
    methods=["GET", "POST"],
)
@login_required
def etapa_filhos_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_parte_contraria_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        possui_filhos = (
            request.form.get("possui_filhos") == "on"
        )

        quantidade_filhos = None

        if possui_filhos:
            quantidade_texto = texto_formulario(
                "quantidade_filhos"
            )

            if quantidade_texto:
                try:
                    quantidade_filhos = int(
                        quantidade_texto
                    )

                    if quantidade_filhos < 0:
                        raise ValueError

                except (TypeError, ValueError):
                    flash(
                        "Informe uma quantidade de filhos válida.",
                        "danger",
                    )

                    return render_template(
                        "atendimentos/familia/filhos.html",
                        **contexto_etapa_familia(
                            atendimento=atendimento,
                            ficha=ficha,
                            etapa_atual="filhos",
                            url_anterior=url_anterior,
                        ),
                    )

        try:
            despesas_mensais_filhos = decimal_formulario(
                "despesas_mensais_filhos"
            )

        except ValueError:
            flash(
                "Informe um valor válido para as despesas mensais dos filhos.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/filhos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="filhos",
                    url_anterior=url_anterior,
                ),
            )

        ficha.possui_filhos = possui_filhos
        ficha.quantidade_filhos = quantidade_filhos

        ficha.filhos_em_comum = (
            request.form.get("filhos_em_comum") == "on"
        )

        ficha.filhos_menores = (
            request.form.get("filhos_menores") == "on"
        )

        ficha.filhos_incapazes = (
            request.form.get("filhos_incapazes") == "on"
        )

        ficha.dados_filhos = texto_formulario(
            "dados_filhos"
        )

        ficha.filhos_residem_com = texto_formulario(
            "filhos_residem_com"
        )

        ficha.existe_filho_com_deficiencia = (
            request.form.get(
                "existe_filho_com_deficiencia"
            ) == "on"
        )

        ficha.necessidades_especiais_filhos = texto_formulario(
            "necessidades_especiais_filhos"
        )

        ficha.escola_filhos = texto_formulario(
            "escola_filhos"
        )

        ficha.plano_saude_filhos = texto_formulario(
            "plano_saude_filhos"
        )

        ficha.despesas_mensais_filhos = (
            despesas_mensais_filhos
        )

        ficha.detalhamento_despesas_filhos = texto_formulario(
            "detalhamento_despesas_filhos"
        )

        ficha.observacoes_filhos = texto_formulario(
            "observacoes_filhos"
        )

        if not ficha.possui_filhos:
            ficha.quantidade_filhos = None
            ficha.filhos_em_comum = False
            ficha.filhos_menores = False
            ficha.filhos_incapazes = False
            ficha.dados_filhos = None
            ficha.filhos_residem_com = None
            ficha.existe_filho_com_deficiencia = False
            ficha.necessidades_especiais_filhos = None
            ficha.escola_filhos = None
            ficha.plano_saude_filhos = None
            ficha.despesas_mensais_filhos = None
            ficha.detalhamento_despesas_filhos = None

        if not ficha.existe_filho_com_deficiencia:
            ficha.necessidades_especiais_filhos = None

        ficha.etapa_atual = "filhos"
        ficha.etapa_filhos_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados dos filhos.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/filhos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="filhos",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Dados dos filhos salvos com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_guarda_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Dados dos filhos salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_filhos_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/filhos.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="filhos",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 6 — GUARDA E CONVIVÊNCIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/guarda",
    methods=["GET", "POST"],
)
@login_required
def etapa_guarda_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_filhos_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        tipo_atual = texto_formulario("tipo_guarda_atual")
        tipo_pretendido = texto_formulario("tipo_guarda_pretendida")

        if tipo_atual not in FichaFamilia.TIPOS_GUARDA:
            tipo_atual = None

        if tipo_pretendido not in FichaFamilia.TIPOS_GUARDA:
            tipo_pretendido = None

        ficha.existe_acordo_guarda = (
            request.form.get("existe_acordo_guarda") == "on"
        )
        ficha.tipo_guarda_atual = tipo_atual
        ficha.tipo_guarda_pretendida = tipo_pretendido
        ficha.guarda_de_fato_com = texto_formulario(
            "guarda_de_fato_com"
        )
        ficha.residencia_referencia_filhos = texto_formulario(
            "residencia_referencia_filhos"
        )
        ficha.regime_convivencia_atual = texto_formulario(
            "regime_convivencia_atual"
        )
        ficha.regime_convivencia_pretendido = texto_formulario(
            "regime_convivencia_pretendido"
        )
        ficha.existe_dificuldade_convivencia = (
            request.form.get("existe_dificuldade_convivencia") == "on"
        )
        ficha.descricao_dificuldade_convivencia = texto_formulario(
            "descricao_dificuldade_convivencia"
        )
        ficha.existe_risco_crianca_adolescente = (
            request.form.get("existe_risco_crianca_adolescente") == "on"
        )
        ficha.descricao_risco_crianca_adolescente = texto_formulario(
            "descricao_risco_crianca_adolescente"
        )
        ficha.existe_alienacao_parental = (
            request.form.get("existe_alienacao_parental") == "on"
        )
        ficha.indicios_alienacao_parental = texto_formulario(
            "indicios_alienacao_parental"
        )
        ficha.necessita_estudo_psicossocial = (
            request.form.get("necessita_estudo_psicossocial") == "on"
        )
        ficha.observacoes_guarda = texto_formulario(
            "observacoes_guarda"
        )

        if not ficha.existe_dificuldade_convivencia:
            ficha.descricao_dificuldade_convivencia = None

        if not ficha.existe_risco_crianca_adolescente:
            ficha.descricao_risco_crianca_adolescente = None

        if not ficha.existe_alienacao_parental:
            ficha.indicios_alienacao_parental = None

        ficha.etapa_atual = "guarda"
        ficha.etapa_guarda_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados de guarda e convivência.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/guarda.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="guarda",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Guarda e convivência salvas com sucesso.",
                "success",
            )
            return redirect(
                url_for(
                    "atendimentos.etapa_alimentos_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Guarda e convivência salvas com sucesso!",
            "success",
        )
        return redirect(
            url_for(
                "atendimentos.etapa_guarda_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/guarda.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="guarda",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 7 — ALIMENTOS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/alimentos",
    methods=["GET", "POST"],
)
@login_required
def etapa_alimentos_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_guarda_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        try:
            valor_pensao_atual = decimal_formulario("valor_pensao_atual")
            percentual_pensao_atual = decimal_formulario("percentual_pensao_atual")
            valor_debito_estimado = decimal_formulario("valor_debito_estimado")
            valor_pretendido_alimentos = decimal_formulario("valor_pretendido_alimentos")
            percentual_pretendido_alimentos = decimal_formulario("percentual_pretendido_alimentos")
        except ValueError:
            flash(
                "Confira os valores monetários e percentuais informados.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/alimentos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="alimentos",
                    url_anterior=url_anterior,
                ),
            )

        meses_em_atraso = inteiro_formulario("meses_em_atraso")
        if meses_em_atraso is not None and meses_em_atraso < 0:
            flash("Informe uma quantidade válida de meses em atraso.", "danger")
            return render_template(
                "atendimentos/familia/alimentos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="alimentos",
                    url_anterior=url_anterior,
                ),
            )

        for percentual in (percentual_pensao_atual, percentual_pretendido_alimentos):
            if percentual is not None and (percentual < 0 or percentual > 100):
                flash("Os percentuais devem estar entre 0 e 100.", "danger")
                return render_template(
                    "atendimentos/familia/alimentos.html",
                    **contexto_etapa_familia(
                        atendimento=atendimento,
                        ficha=ficha,
                        etapa_atual="alimentos",
                        url_anterior=url_anterior,
                    ),
                )

        ficha.existe_pensao_atual = request.form.get("existe_pensao_atual") == "on"
        ficha.pensao_fixada_judicialmente = request.form.get("pensao_fixada_judicialmente") == "on"
        ficha.numero_processo_alimentos = texto_formulario("numero_processo_alimentos")
        ficha.valor_pensao_atual = valor_pensao_atual
        ficha.percentual_pensao_atual = percentual_pensao_atual
        ficha.forma_pagamento_pensao = texto_formulario("forma_pagamento_pensao")
        ficha.pensao_esta_em_atraso = request.form.get("pensao_esta_em_atraso") == "on"
        ficha.meses_em_atraso = meses_em_atraso
        ficha.valor_debito_estimado = valor_debito_estimado
        ficha.valor_pretendido_alimentos = valor_pretendido_alimentos
        ficha.percentual_pretendido_alimentos = percentual_pretendido_alimentos
        ficha.despesas_alimentando = texto_formulario("despesas_alimentando")
        ficha.capacidade_financeira_alimentante = texto_formulario("capacidade_financeira_alimentante")
        ficha.existem_outros_dependentes = request.form.get("existem_outros_dependentes") == "on"
        ficha.descricao_outros_dependentes = texto_formulario("descricao_outros_dependentes")
        ficha.pretende_alimentos_provisorios = request.form.get("pretende_alimentos_provisorios") == "on"
        ficha.observacoes_alimentos = texto_formulario("observacoes_alimentos")

        if not ficha.existe_pensao_atual:
            ficha.pensao_fixada_judicialmente = False
            ficha.numero_processo_alimentos = None
            ficha.valor_pensao_atual = None
            ficha.percentual_pensao_atual = None
            ficha.forma_pagamento_pensao = None
            ficha.pensao_esta_em_atraso = False
            ficha.meses_em_atraso = None
            ficha.valor_debito_estimado = None

        if not ficha.pensao_fixada_judicialmente:
            ficha.numero_processo_alimentos = None

        if not ficha.pensao_esta_em_atraso:
            ficha.meses_em_atraso = None
            ficha.valor_debito_estimado = None

        if not ficha.existem_outros_dependentes:
            ficha.descricao_outros_dependentes = None

        ficha.etapa_atual = "alimentos"
        ficha.etapa_alimentos_concluida = True
        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("Não foi possível salvar os dados de alimentos.", "danger")
            return render_template(
                "atendimentos/familia/alimentos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="alimentos",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get("acao", "salvar")
        if acao == "salvar_proxima":
            flash(
                "✅ Dados de alimentos salvos com sucesso.",
                "success",
            )
            return redirect(
                url_for(
                    "atendimentos.etapa_patrimonio_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash("✅ Dados de alimentos salvos com sucesso!", "success")

        return redirect(
            url_for(
                "atendimentos.etapa_alimentos_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/alimentos.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="alimentos",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 8 — PATRIMÔNIO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/patrimonio",
    methods=["GET", "POST"],
)
@login_required
def etapa_patrimonio_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_alimentos_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        try:
            valor_estimado_patrimonio = decimal_formulario(
                "valor_estimado_patrimonio"
            )
        except ValueError:
            flash(
                "Confira o valor estimado do patrimônio informado.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/patrimonio.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="patrimonio",
                    url_anterior=url_anterior,
                ),
            )

        if (
            valor_estimado_patrimonio is not None
            and valor_estimado_patrimonio < 0
        ):
            flash(
                "O valor estimado do patrimônio não pode ser negativo.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/patrimonio.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="patrimonio",
                    url_anterior=url_anterior,
                ),
            )

        ficha.possui_bens_partilhar = (
            request.form.get("possui_bens_partilhar") == "on"
        )
        ficha.imoveis = texto_formulario("imoveis")
        ficha.veiculos = texto_formulario("veiculos")
        ficha.contas_bancarias_investimentos = texto_formulario(
            "contas_bancarias_investimentos"
        )
        ficha.empresas_quotas_sociais = texto_formulario(
            "empresas_quotas_sociais"
        )
        ficha.bens_moveis_relevantes = texto_formulario(
            "bens_moveis_relevantes"
        )
        ficha.dividas_comuns = texto_formulario("dividas_comuns")

        ficha.bens_particulares_cliente = texto_formulario(
            "bens_particulares_cliente"
        )
        ficha.bens_particulares_parte_contraria = texto_formulario(
            "bens_particulares_parte_contraria"
        )

        ficha.existe_ocultacao_patrimonial = (
            request.form.get("existe_ocultacao_patrimonial") == "on"
        )
        ficha.indicios_ocultacao_patrimonial = texto_formulario(
            "indicios_ocultacao_patrimonial"
        )

        ficha.existe_acordo_partilha = (
            request.form.get("existe_acordo_partilha") == "on"
        )
        ficha.proposta_partilha = texto_formulario("proposta_partilha")
        ficha.valor_estimado_patrimonio = valor_estimado_patrimonio
        ficha.observacoes_patrimonio = texto_formulario(
            "observacoes_patrimonio"
        )

        if not ficha.possui_bens_partilhar:
            ficha.imoveis = None
            ficha.veiculos = None
            ficha.contas_bancarias_investimentos = None
            ficha.empresas_quotas_sociais = None
            ficha.bens_moveis_relevantes = None
            ficha.dividas_comuns = None
            ficha.existe_ocultacao_patrimonial = False
            ficha.indicios_ocultacao_patrimonial = None
            ficha.existe_acordo_partilha = False
            ficha.proposta_partilha = None
            ficha.valor_estimado_patrimonio = None

        if not ficha.existe_ocultacao_patrimonial:
            ficha.indicios_ocultacao_patrimonial = None

        if not ficha.existe_acordo_partilha:
            ficha.proposta_partilha = None

        ficha.etapa_atual = "patrimonio"
        ficha.etapa_patrimonio_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados patrimoniais.",
                "danger",
            )
            return render_template(
                "atendimentos/familia/patrimonio.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="patrimonio",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Dados patrimoniais salvos com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_documentos_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Dados patrimoniais salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_patrimonio_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/patrimonio.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="patrimonio",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 9 — DOCUMENTOS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/documentos",
    methods=["GET", "POST"],
)
@login_required
def etapa_documentos_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_patrimonio_familia",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.possui_documento_identificacao = (
            request.form.get("possui_documento_identificacao") == "on"
        )

        ficha.possui_comprovante_residencia = (
            request.form.get("possui_comprovante_residencia") == "on"
        )

        ficha.possui_certidao_casamento = (
            request.form.get("possui_certidao_casamento") == "on"
        )

        ficha.possui_certidao_uniao_estavel = (
            request.form.get("possui_certidao_uniao_estavel") == "on"
        )

        ficha.possui_certidoes_nascimento_filhos = (
            request.form.get(
                "possui_certidoes_nascimento_filhos"
            ) == "on"
        )

        ficha.possui_comprovantes_renda = (
            request.form.get("possui_comprovantes_renda") == "on"
        )

        ficha.possui_comprovantes_despesas = (
            request.form.get("possui_comprovantes_despesas") == "on"
        )

        ficha.possui_documentos_bens = (
            request.form.get("possui_documentos_bens") == "on"
        )

        ficha.possui_acordo_anterior = (
            request.form.get("possui_acordo_anterior") == "on"
        )

        ficha.possui_decisao_judicial = (
            request.form.get("possui_decisao_judicial") == "on"
        )

        ficha.possui_boletim_ocorrencia = (
            request.form.get("possui_boletim_ocorrencia") == "on"
        )

        ficha.possui_medida_protetiva = (
            request.form.get("possui_medida_protetiva") == "on"
        )

        ficha.possui_conversas_mensagens = (
            request.form.get("possui_conversas_mensagens") == "on"
        )

        ficha.possui_fotos_videos_audios = (
            request.form.get("possui_fotos_videos_audios") == "on"
        )

        ficha.possui_laudos_relatorios = (
            request.form.get("possui_laudos_relatorios") == "on"
        )

        ficha.outros_documentos = texto_formulario(
            "outros_documentos"
        )

        ficha.documentos_entregues = texto_formulario(
            "documentos_entregues"
        )

        ficha.documentos_pendentes = texto_formulario(
            "documentos_pendentes"
        )

        ficha.observacoes_documentos = texto_formulario(
            "observacoes_documentos"
        )

        ficha.etapa_atual = "documentos"
        ficha.etapa_documentos_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar o controle de documentos.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/documentos.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="documentos",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Documentos salvos com sucesso.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_analise_familia",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Controle de documentos salvo com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_documentos_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/documentos.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="documentos",
            url_anterior=url_anterior,
        ),
    )



# ============================================================
# ETAPA 10 — ANÁLISE JURÍDICA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/analise",
    methods=["GET", "POST"],
)
@login_required
def etapa_analise_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_familia(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_documentos_familia",
        atendimento_id=atendimento.id,
    )
    url_proxima = "#"

    if request.method == "POST":
        ficha.competencia = texto_formulario("competencia")
        ficha.foro_competente = texto_formulario("foro_competente")

        ficha.existe_prevencao = (
            request.form.get("existe_prevencao") == "on"
        )
        ficha.processo_prevento = texto_formulario("processo_prevento")

        ficha.necessidade_intervencao_mp = (
            request.form.get("necessidade_intervencao_mp") == "on"
        )
        ficha.necessidade_segredo_justica = (
            request.form.get("necessidade_segredo_justica") == "on"
        )
        ficha.necessidade_tutela_urgencia = (
            request.form.get("necessidade_tutela_urgencia") == "on"
        )
        ficha.fundamentos_tutela_urgencia = texto_formulario(
            "fundamentos_tutela_urgencia"
        )

        ficha.fundamentos_juridicos = texto_formulario(
            "fundamentos_juridicos"
        )
        ficha.pedidos_sugeridos = texto_formulario(
            "pedidos_sugeridos"
        )
        ficha.provas_necessarias = texto_formulario(
            "provas_necessarias"
        )
        ficha.riscos_processo = texto_formulario(
            "riscos_processo"
        )
        ficha.estrategia_sugerida = texto_formulario(
            "estrategia_sugerida"
        )
        ficha.providencias_iniciais = texto_formulario(
            "providencias_iniciais"
        )

        ficha.possibilidade_acordo = (
            request.form.get("possibilidade_acordo") == "on"
        )
        ficha.termos_possivel_acordo = texto_formulario(
            "termos_possivel_acordo"
        )

        viabilidade_demanda = texto_formulario(
            "viabilidade_demanda"
        )

        if viabilidade_demanda not in FichaFamilia.VIABILIDADES:
            viabilidade_demanda = "INDEFINIDA"

        ficha.viabilidade_demanda = viabilidade_demanda
        ficha.parecer_inicial = texto_formulario("parecer_inicial")
        ficha.observacoes_gerais = texto_formulario(
            "observacoes_gerais"
        )

        if not ficha.existe_prevencao:
            ficha.processo_prevento = None

        if not ficha.necessidade_tutela_urgencia:
            ficha.fundamentos_tutela_urgencia = None

        if not ficha.possibilidade_acordo:
            ficha.termos_possivel_acordo = None

        ficha.etapa_atual = "analise"
        ficha.etapa_analise_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar a análise jurídica. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/familia/analise_juridica.html",
                **contexto_etapa_familia(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="analise",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        flash(
            "✅ Análise jurídica salva. "
            "A Ficha de Direito de Família está completa!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_analise_familia",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/familia/analise_juridica.html",
        **contexto_etapa_familia(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="analise",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# SELECIONAR ÁREA DO ATENDIMENTO
# ============================================================

@atendimento_bp.route(
    "/clientes/<int:cliente_id>/atendimentos/novo",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def selecionar_area(cliente_id):
    cliente = Cliente.query.get_or_404(
        cliente_id,
    )

    if request.method == "POST":
        area = request.form.get(
            "area",
            "",
        ).strip().upper()

        if not area_valida(area):
            flash(
                "Selecione uma área jurídica válida.",
                "danger",
            )

            return render_template(
                "atendimentos/selecionar_area.html",
                cliente=cliente,
                areas=Atendimento.AREAS,
            )

        areas_disponiveis = {
            Atendimento.AREA_TRABALHISTA,
            Atendimento.AREA_PREVIDENCIARIA,
            Atendimento.AREA_CIVEL,
            Atendimento.AREA_FAMILIA,
        }

        if area not in areas_disponiveis:
            flash(
                "Neste momento, estão disponíveis as fichas "
                "Trabalhista, Previdenciária, Cível e Família. As demais áreas "
                "serão implantadas nas próximas etapas.",
                "warning",
            )

            return render_template(
                "atendimentos/selecionar_area.html",
                cliente=cliente,
                areas=Atendimento.AREAS,
            )

        configuracoes_area = {
            Atendimento.AREA_TRABALHISTA: {
                "titulo": "Atendimento trabalhista",
                "modelo_ficha": FichaTrabalhista,
                "rota_inicial": "atendimentos.etapa_atendimento",
                "mensagem": (
                    "✅ Atendimento trabalhista iniciado com sucesso!"
                ),
            },
            Atendimento.AREA_PREVIDENCIARIA: {
                "titulo": "Atendimento previdenciário",
                "modelo_ficha": FichaPrevidenciaria,
                "rota_inicial": "atendimentos.etapa_atendimento_previdenciario",
                "mensagem": (
                    "✅ Atendimento previdenciário iniciado com sucesso!"
                ),
            },

            Atendimento.AREA_CIVEL: {
                "titulo": "Atendimento cível",
                "modelo_ficha": FichaCivel,
                "rota_inicial": "atendimentos.etapa_atendimento_civel",
                "mensagem": (
                    "✅ Atendimento cível iniciado com sucesso!"
                ),
            },
            Atendimento.AREA_FAMILIA: {
                "titulo": "Atendimento de Família",
                "modelo_ficha": FichaFamilia,
                "rota_inicial": "atendimentos.etapa_atendimento_familia",
                "mensagem": (
                    "✅ Atendimento de Família iniciado com sucesso!"
                ),
            },
        }

        configuracao = configuracoes_area[area]

        atendimento = Atendimento(
            cliente_id=cliente.id,
            area=area,
            status=Atendimento.STATUS_RASCUNHO,
            data_atendimento=date.today(),
            titulo=configuracao["titulo"],
            responsavel_id=current_user.id,
            criado_por_id=current_user.id,
            atualizado_por_id=current_user.id,
        )

        try:
            db.session.add(atendimento)
            db.session.flush()

            ficha = configuracao["modelo_ficha"](
                atendimento_id=atendimento.id,
                etapa_atual="atendimento",
                criado_por_id=current_user.id,
                atualizado_por_id=current_user.id,
            )

            db.session.add(ficha)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível iniciar o atendimento. "
                "Tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/selecionar_area.html",
                cliente=cliente,
                areas=Atendimento.AREAS,
            )

        flash(
            configuracao["mensagem"],
            "success",
        )

        return redirect(
            url_for(
                configuracao["rota_inicial"],
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/selecionar_area.html",
        cliente=cliente,
        areas=Atendimento.AREAS,
    )

# ============================================================
# ENTRADA E ETAPA 1 DA FICHA CÍVEL
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel",
    methods=["GET"],
)
@login_required
def ficha_civel(atendimento_id):
    """
    Mantém um endereço principal para a ficha cível.
    """

    return redirect(
        url_for(
            "atendimentos.etapa_atendimento_civel",
            atendimento_id=atendimento_id,
        )
    )


@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/atendimento",
    methods=["GET", "POST"],
)
@login_required
def etapa_atendimento_civel(atendimento_id):
    """
    Exibe e salva a primeira etapa da ficha cível.
    """

    atendimento = buscar_atendimento_civel(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        titulo = texto_formulario("titulo")

        status = request.form.get(
            "status",
            Atendimento.STATUS_RASCUNHO,
        ).strip()

        if not titulo:
            flash(
                "Informe o título do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/atendimento.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                ),
            )

        if status not in Atendimento.STATUS:
            status = Atendimento.STATUS_RASCUNHO

        try:
            data_atendimento = data_formulario(
                "data_atendimento"
            )

            horario_atendimento = horario_formulario(
                "horario_atendimento"
            )

        except ValueError:
            flash(
                "Informe uma data e um horário válidos.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/atendimento.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                ),
            )

        if data_atendimento is None:
            flash(
                "Informe a data do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/atendimento.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                ),
            )

        atendimento.titulo = titulo
        atendimento.status = status
        atendimento.data_atendimento = data_atendimento
        atendimento.horario_atendimento = horario_atendimento

        atendimento.resumo_caso = texto_formulario(
            "resumo_caso"
        )

        atendimento.observacoes_internas = texto_formulario(
            "observacoes_internas"
        )

        ficha.etapa_atual = "atendimento"
        ficha.etapa_atendimento_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do atendimento "
                "cível. Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/atendimento.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Etapa Atendimento salva com sucesso. "
                "A próxima etapa será Dados do cliente.",
                "success",
            )

        else:
            flash(
                "✅ Dados do atendimento cível salvos com sucesso!",
                "success",
            )

        return redirect(
            url_for(
                "atendimentos.etapa_atendimento_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/atendimento.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="atendimento",
        ),
    )

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/cliente",
    methods=["GET", "POST"],
)
@login_required
def etapa_cliente_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    

    url_anterior = url_for(
        "atendimentos.etapa_atendimento_civel",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_parte_contraria_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":

        ficha.estado_civil_atual = texto_formulario(
            "estado_civil_atual"
        )

        ficha.profissao_atual = texto_formulario(
            "profissao_atual"
        )

        try:
            ficha.renda_mensal_aproximada = decimal_formulario(
                "renda_mensal_aproximada"
            )
        except ValueError:
            flash(
                "Informe uma renda mensal válida.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/cliente.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="cliente",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.possui_beneficio_justica_gratuita = texto_formulario(
            "possui_beneficio_justica_gratuita"
        )

        if (
            ficha.possui_beneficio_justica_gratuita
            not in FichaCivel.RESPOSTAS
        ):
            ficha.possui_beneficio_justica_gratuita = None

        ficha.motivo_justica_gratuita = texto_formulario(
            "motivo_justica_gratuita"
        )

        if (
            ficha.possui_beneficio_justica_gratuita
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.motivo_justica_gratuita = None

        ficha.contato_alternativo_nome = texto_formulario(
            "contato_alternativo_nome"
        )

        ficha.contato_alternativo_telefone = texto_formulario(
            "contato_alternativo_telefone"
        )

        ficha.contato_alternativo_relacao = texto_formulario(
            "contato_alternativo_relacao"
        )

        ficha.melhor_horario_contato = texto_formulario(
            "melhor_horario_contato"
        )

        ficha.observacoes_cliente = texto_formulario(
            "observacoes_cliente"
        )

        ficha.etapa_atual = "cliente"
        ficha.etapa_cliente_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do cliente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/cliente.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="cliente",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":

            flash(
                "✅ Dados do cliente salvos com sucesso.",
                "success",
            )

            return redirect(url_proxima)

        flash(
            "✅ Dados do cliente salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_cliente_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/cliente.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="cliente",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )

# ============================================================
# ETAPA 3 — PARTE CONTRÁRIA CÍVEL
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/parte-contraria",
    methods=["GET", "POST"],
)
@login_required
def etapa_parte_contraria_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_cliente_civel",
        atendimento_id=atendimento.id,
    )


    url_proxima = url_for(
        "atendimentos.etapa_fatos_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.parte_contraria_tipo = texto_formulario(
            "parte_contraria_tipo"
        )

        tipos_validos = {
            "PESSOA_FISICA",
            "PESSOA_JURIDICA",
            "NAO_INFORMADO",
        }

        if ficha.parte_contraria_tipo not in tipos_validos:
            ficha.parte_contraria_tipo = None

        ficha.parte_contraria_nome = texto_formulario(
            "parte_contraria_nome"
        )

        ficha.parte_contraria_cpf_cnpj = texto_formulario(
            "parte_contraria_cpf_cnpj"
        )

        ficha.parte_contraria_rg = texto_formulario(
            "parte_contraria_rg"
        )

        ficha.parte_contraria_endereco = texto_formulario(
            "parte_contraria_endereco"
        )

        ficha.parte_contraria_cidade = texto_formulario(
            "parte_contraria_cidade"
        )

        ficha.parte_contraria_estado = texto_formulario(
            "parte_contraria_estado"
        )

        if ficha.parte_contraria_estado:
            ficha.parte_contraria_estado = (
                ficha.parte_contraria_estado.upper()[:2]
            )

        ficha.parte_contraria_cep = texto_formulario(
            "parte_contraria_cep"
        )

        ficha.parte_contraria_telefone = texto_formulario(
            "parte_contraria_telefone"
        )

        ficha.parte_contraria_whatsapp = texto_formulario(
            "parte_contraria_whatsapp"
        )

        ficha.parte_contraria_email = texto_formulario(
            "parte_contraria_email"
        )

        ficha.relacao_com_cliente = texto_formulario(
            "relacao_com_cliente"
        )

        ficha.possui_advogado = texto_formulario(
            "possui_advogado"
        )

        if ficha.possui_advogado not in FichaCivel.RESPOSTAS:
            ficha.possui_advogado = None

        ficha.advogado_parte_contraria = texto_formulario(
            "advogado_parte_contraria"
        )

        if ficha.possui_advogado != FichaCivel.RESPOSTA_SIM:
            ficha.advogado_parte_contraria = None

        ficha.observacoes_parte_contraria = texto_formulario(
            "observacoes_parte_contraria"
        )

        if not ficha.parte_contraria_nome:
            flash(
                "Informe o nome da parte contrária.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/parte_contraria.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="parte_contraria",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.etapa_atual = "parte_contraria"
        ficha.etapa_parte_contraria_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da parte contrária. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/parte_contraria.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="parte_contraria",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Dados da parte contrária salvos com sucesso. ",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_contrato_civel",
                    atendimento_id=atendimento.id,
                )
            )

    return render_template(
        "atendimentos/civel/parte_contraria.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="parte_contraria",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )

# ============================================================
# ETAPA 4 — FATOS CÍVEIS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/fatos",
    methods=["GET", "POST"],
)
@login_required
def etapa_fatos_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_parte_contraria_civel",
        atendimento_id=atendimento.id,
    )
    url_proxima = url_for(
        "atendimentos.etapa_contrato_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.data_inicio_fatos = data_formulario(
            "data_inicio_fatos"
        )

        ficha.data_ultimo_fato = data_formulario(
            "data_ultimo_fato"
        )

        ficha.local_fatos = texto_formulario(
            "local_fatos"
        )

        ficha.descricao_detalhada_fatos = texto_formulario(
            "descricao_detalhada_fatos"
        )

        ficha.fatos_continuam_ocorrendo = texto_formulario(
            "fatos_continuam_ocorrendo"
        )

        ficha.houve_ameaca = texto_formulario(
            "houve_ameaca"
        )

        ficha.descricao_ameaca = texto_formulario(
            "descricao_ameaca"
        )

        ficha.existem_testemunhas = texto_formulario(
            "existem_testemunhas"
        )

        ficha.testemunhas_dados = texto_formulario(
            "testemunhas_dados"
        )

        ficha.existem_provas = texto_formulario(
            "existem_provas"
        )

        ficha.provas_existentes = texto_formulario(
            "provas_existentes"
        )

        ficha.cliente_participou_diretamente = texto_formulario(
            "cliente_participou_diretamente"
        )

        ficha.terceiros_envolvidos = texto_formulario(
            "terceiros_envolvidos"
        )

        ficha.observacoes_fatos = texto_formulario(
            "observacoes_fatos"
        )

        campos_resposta = [
            "fatos_continuam_ocorrendo",
            "houve_ameaca",
            "existem_testemunhas",
            "existem_provas",
            "cliente_participou_diretamente",
        ]

        for campo in campos_resposta:
            valor = getattr(ficha, campo)

            if valor not in FichaCivel.RESPOSTAS:
                setattr(ficha, campo, None)

        if ficha.houve_ameaca != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_ameaca = None

        if ficha.existem_testemunhas != FichaCivel.RESPOSTA_SIM:
            ficha.testemunhas_dados = None

        if ficha.existem_provas != FichaCivel.RESPOSTA_SIM:
            ficha.provas_existentes = None

        if not ficha.descricao_detalhada_fatos:
            flash(
                "Descreva detalhadamente os fatos.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/fatos.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="fatos",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.etapa_atual = "fatos"
        ficha.etapa_fatos_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os fatos. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/fatos.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="fatos",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Fatos salvos com sucesso. "
                "A próxima etapa será Contratos e obrigações.",
                "success",
            )

            return redirect(
                url_for(
                    "atendimentos.etapa_fatos_civel",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Fatos salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_fatos_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/fatos.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="fatos",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )

# ============================================================
# ETAPA 5 — CONTRATOS E OBRIGAÇÕES CÍVEIS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/contrato",
    methods=["GET", "POST"],
)
@login_required
def etapa_contrato_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_fatos_civel",
        atendimento_id=atendimento.id,
    )
    url_proxima = url_for(
        "atendimentos.etapa_danos_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.existe_contrato = texto_formulario(
            "existe_contrato"
        )

        ficha.contrato_escrito = texto_formulario(
            "contrato_escrito"
        )

        ficha.tipo_contrato = texto_formulario(
            "tipo_contrato"
        )

        try:
            ficha.data_contrato = data_formulario(
                "data_contrato"
            )

            ficha.data_fim_contrato = data_formulario(
                "data_fim_contrato"
            )

            ficha.valor_contrato = decimal_formulario(
                "valor_contrato"
            )

            ficha.valor_multa_contratual = decimal_formulario(
                "valor_multa_contratual"
            )

        except ValueError:
            flash(
                "Informe datas e valores monetários válidos.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/contrato.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="contrato",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.forma_pagamento = texto_formulario(
            "forma_pagamento"
        )

        ficha.contrato_quitado = texto_formulario(
            "contrato_quitado"
        )

        ficha.possui_comprovantes_pagamento = texto_formulario(
            "possui_comprovantes_pagamento"
        )

        ficha.obrigacao_cliente = texto_formulario(
            "obrigacao_cliente"
        )

        ficha.obrigacao_parte_contraria = texto_formulario(
            "obrigacao_parte_contraria"
        )

        ficha.obrigacao_descumprida = texto_formulario(
            "obrigacao_descumprida"
        )

        ficha.houve_multa_contratual = texto_formulario(
            "houve_multa_contratual"
        )

        ficha.observacoes_contrato = texto_formulario(
            "observacoes_contrato"
        )

        campos_resposta = [
            "existe_contrato",
            "contrato_escrito",
            "contrato_quitado",
            "possui_comprovantes_pagamento",
            "houve_multa_contratual",
        ]

        for campo in campos_resposta:
            valor = getattr(ficha, campo)

            if valor not in FichaCivel.RESPOSTAS:
                setattr(ficha, campo, None)

        if ficha.existe_contrato != FichaCivel.RESPOSTA_SIM:
            ficha.contrato_escrito = None
            ficha.tipo_contrato = None
            ficha.data_contrato = None
            ficha.data_fim_contrato = None
            ficha.valor_contrato = None
            ficha.forma_pagamento = None
            ficha.contrato_quitado = None
            ficha.possui_comprovantes_pagamento = None
            ficha.obrigacao_cliente = None
            ficha.obrigacao_parte_contraria = None
            ficha.obrigacao_descumprida = None
            ficha.houve_multa_contratual = None
            ficha.valor_multa_contratual = None

        if (
            ficha.houve_multa_contratual
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.valor_multa_contratual = None

        ficha.etapa_atual = "contrato"
        ficha.etapa_contrato_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do contrato. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/contrato.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="contrato",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima" and url_proxima != "#":
            flash(
                "✅ Contratos e obrigações salvos com sucesso.",
                "success",
            )

            return redirect(url_proxima)

        flash(
            "✅ Contratos e obrigações salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_contrato_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/contrato.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="contrato",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# ETAPA 6 — DANOS E VALORES CÍVEIS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/danos",
    methods=["GET", "POST"],
)
@login_required
def etapa_danos_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_contrato_civel",
        atendimento_id=atendimento.id,
    )
    url_proxima = url_for(
        "atendimentos.etapa_tentativas_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_resposta = [
            "houve_dano_material",
            "houve_dano_moral",
            "houve_lucros_cessantes",
            "houve_dano_estetico",
            "existem_gastos_futuros",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaCivel.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        ficha.descricao_dano_material = texto_formulario(
            "descricao_dano_material"
        )

        ficha.descricao_dano_moral = texto_formulario(
            "descricao_dano_moral"
        )

        ficha.descricao_lucros_cessantes = texto_formulario(
            "descricao_lucros_cessantes"
        )

        ficha.descricao_dano_estetico = texto_formulario(
            "descricao_dano_estetico"
        )

        ficha.descricao_gastos_futuros = texto_formulario(
            "descricao_gastos_futuros"
        )

        ficha.observacoes_danos = texto_formulario(
            "observacoes_danos"
        )

        try:
            ficha.valor_dano_material = decimal_formulario(
                "valor_dano_material"
            )

            ficha.valor_pretendido_dano_moral = decimal_formulario(
                "valor_pretendido_dano_moral"
            )

            ficha.valor_lucros_cessantes = decimal_formulario(
                "valor_lucros_cessantes"
            )

            ficha.valor_total_prejuizo = decimal_formulario(
                "valor_total_prejuizo"
            )

        except ValueError:
            flash(
                "Informe valores monetários válidos.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/danos.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="danos",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        if ficha.houve_dano_material != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_dano_material = None
            ficha.valor_dano_material = None

        if ficha.houve_dano_moral != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_dano_moral = None
            ficha.valor_pretendido_dano_moral = None

        if ficha.houve_lucros_cessantes != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_lucros_cessantes = None
            ficha.valor_lucros_cessantes = None

        if ficha.houve_dano_estetico != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_dano_estetico = None

        if ficha.existem_gastos_futuros != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_gastos_futuros = None

        ficha.etapa_atual = "danos"
        ficha.etapa_danos_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados de danos e valores. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/danos.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="danos",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima" and url_proxima != "#":
            flash(
                "✅ Danos e valores salvos com sucesso.",
                "success",
            )

            return redirect(url_proxima)

        flash(
            "✅ Danos e valores salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_danos_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/danos.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="danos",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# ETAPA 7 — TENTATIVAS DE SOLUÇÃO CÍVEIS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/tentativas",
    methods=["GET", "POST"],
)
@login_required
def etapa_tentativas_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_danos_civel",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_documentos_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_resposta = [
            "houve_contato_parte_contraria",
            "houve_proposta_acordo",
            "enviou_notificacao_extrajudicial",
            "houve_resposta_notificacao",
            "fez_reclamacao_administrativa",
            "registrou_boletim_ocorrencia",
            "existe_processo_anterior",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaCivel.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        ficha.descricao_contatos = texto_formulario(
            "descricao_contatos"
        )

        ficha.descricao_proposta_acordo = texto_formulario(
            "descricao_proposta_acordo"
        )

        ficha.descricao_resposta_notificacao = texto_formulario(
            "descricao_resposta_notificacao"
        )

        ficha.orgao_reclamacao = texto_formulario(
            "orgao_reclamacao"
        )

        ficha.protocolo_reclamacao = texto_formulario(
            "protocolo_reclamacao"
        )

        ficha.numero_boletim_ocorrencia = texto_formulario(
            "numero_boletim_ocorrencia"
        )

        ficha.numero_processo_anterior = texto_formulario(
            "numero_processo_anterior"
        )

        ficha.resultado_processo_anterior = texto_formulario(
            "resultado_processo_anterior"
        )

        ficha.observacoes_tentativas = texto_formulario(
            "observacoes_tentativas"
        )

        try:
            ficha.data_notificacao_extrajudicial = data_formulario(
                "data_notificacao_extrajudicial"
            )

            ficha.data_boletim_ocorrencia = data_formulario(
                "data_boletim_ocorrencia"
            )

        except ValueError:
            flash(
                "Informe datas válidas.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/tentativas.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="tentativas",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        if (
            ficha.houve_contato_parte_contraria
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.descricao_contatos = None

        if ficha.houve_proposta_acordo != FichaCivel.RESPOSTA_SIM:
            ficha.descricao_proposta_acordo = None

        if (
            ficha.enviou_notificacao_extrajudicial
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.data_notificacao_extrajudicial = None
            ficha.houve_resposta_notificacao = None
            ficha.descricao_resposta_notificacao = None

        elif (
            ficha.houve_resposta_notificacao
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.descricao_resposta_notificacao = None

        if (
            ficha.fez_reclamacao_administrativa
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.orgao_reclamacao = None
            ficha.protocolo_reclamacao = None

        if (
            ficha.registrou_boletim_ocorrencia
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.numero_boletim_ocorrencia = None
            ficha.data_boletim_ocorrencia = None

        if ficha.existe_processo_anterior != FichaCivel.RESPOSTA_SIM:
            ficha.numero_processo_anterior = None
            ficha.resultado_processo_anterior = None

        ficha.etapa_atual = "tentativas"
        ficha.etapa_tentativas_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar as tentativas de solução. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/tentativas.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="tentativas",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima" and url_proxima != "#":
            flash(
                "✅ Tentativas de solução salvas com sucesso.",
                "success",
            )

            return redirect(url_proxima)

        flash(
            "✅ Tentativas de solução salvas com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_tentativas_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/tentativas.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="tentativas",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# ETAPA 8 — DOCUMENTOS CÍVEIS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/documentos",
    methods=["GET", "POST"],
)
@login_required
def etapa_documentos_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_tentativas_civel",
        atendimento_id=atendimento.id,
    )
    url_proxima = url_for(
        "atendimentos.etapa_analise_civel",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_resposta = [
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
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaCivel.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        campos_texto = [
            "outros_documentos",
            "documentos_entregues",
            "documentos_pendentes",
            "observacoes_documentos",
        ]

        for campo in campos_texto:
            setattr(
                ficha,
                campo,
                texto_formulario(campo),
            )

        ficha.etapa_atual = "documentos"
        ficha.etapa_documentos_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os documentos. "
                "Verifique os dados e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/civel/documentos.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="documentos",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        if request.form.get("acao") == "salvar_proxima":
            flash(
                "✅ Documentos salvos com sucesso.",
                "success",
            )
            return redirect(url_proxima)

        flash(
            "✅ Documentos salvos com sucesso!",
            "success",
        )
        return redirect(
            url_for(
                "atendimentos.etapa_documentos_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/documentos.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="documentos",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# ETAPA 9 — ANÁLISE JURÍDICA CÍVEL
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/analise",
    methods=["GET", "POST"],
)
@login_required
def etapa_analise_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(atendimento_id)

    if atendimento is None:
        return redirect(url_for("clientes.listar_clientes"))

    ficha = obter_ou_criar_ficha_civel(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_documentos_civel",
        atendimento_id=atendimento.id,
    )
    url_proxima = "#"

    if request.method == "POST":
        campos_resposta = [
            "existe_prescricao",
            "legitimidade_cliente",
            "legitimidade_parte_contraria",
            "necessidade_tutela_urgencia",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaCivel.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        campos_texto = [
            "prazo_prescricional",
            "competencia",
            "foro_competente",
            "fundamentos_juridicos",
            "pedidos_sugeridos",
            "fundamentos_tutela_urgencia",
            "riscos_processo",
            "provas_necessarias",
            "providencias_iniciais",
            "estrategia_sugerida",
            "viabilidade_demanda",
            "parecer_inicial",
            "observacoes_gerais",
        ]

        for campo in campos_texto:
            setattr(
                ficha,
                campo,
                texto_formulario(campo),
            )

        try:
            ficha.data_final_prescricao = data_formulario(
                "data_final_prescricao"
            )

        except ValueError:
            flash(
                "Informe uma data final de prescrição válida.",
                "danger",
            )
            return render_template(
                "atendimentos/civel/analise.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="analise",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        if ficha.existe_prescricao != FichaCivel.RESPOSTA_SIM:
            ficha.prazo_prescricional = None
            ficha.data_final_prescricao = None

        if (
            ficha.necessidade_tutela_urgencia
            != FichaCivel.RESPOSTA_SIM
        ):
            ficha.fundamentos_tutela_urgencia = None

        ficha.etapa_atual = "analise"
        ficha.etapa_analise_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar a análise jurídica. "
                "Verifique os dados e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/civel/analise.html",
                **contexto_etapa_civel(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="analise",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        flash(
            "✅ Análise jurídica salva. A Ficha Cível está completa!",
            "success",
        )
        return redirect(
            url_for(
                "atendimentos.etapa_analise_civel",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/civel/analise.html",
        **contexto_etapa_civel(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="analise",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )

# ============================================================
# ENTRADA E ETAPA 1 DA FICHA PREVIDENCIÁRIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria",
    methods=["GET", "POST"],
)
@login_required
def ficha_previdenciaria(atendimento_id):
    """Mantém compatibilidade com o endereço inicial antigo."""
    return redirect(
        url_for(
            "atendimentos.etapa_atendimento_previdenciario",
            atendimento_id=atendimento_id,
        )
    )


@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/atendimento",
    methods=["GET", "POST"],
)
@login_required
def etapa_atendimento_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        titulo = texto_formulario("titulo")
        status = request.form.get(
            "status",
            Atendimento.STATUS_RASCUNHO,
        ).strip()

        if not titulo:
            flash("Informe o título do atendimento.", "danger")
            return render_template(
                "atendimentos/previdenciaria/atendimento.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_segurado_previdenciario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if status not in Atendimento.STATUS:
            status = Atendimento.STATUS_RASCUNHO

        try:
            data_atendimento = data_formulario("data_atendimento")
            horario_atendimento = horario_formulario(
                "horario_atendimento"
            )
        except ValueError:
            flash(
                "Informe uma data e um horário válidos.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/atendimento.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_segurado_previdenciario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if data_atendimento is None:
            flash("Informe a data do atendimento.", "danger")
            return render_template(
                "atendimentos/previdenciaria/atendimento.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_segurado_previdenciario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        atendimento.titulo = titulo
        atendimento.status = status
        atendimento.data_atendimento = data_atendimento
        atendimento.horario_atendimento = horario_atendimento
        atendimento.resumo_caso = texto_formulario("resumo_caso")
        atendimento.observacoes_internas = texto_formulario(
            "observacoes_internas"
        )

        ficha.etapa_atual = "atendimento"
        ficha.etapa_atendimento_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados do atendimento. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/atendimento.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_segurado_previdenciario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Etapa Atendimento salva com sucesso. "
                "Agora preencha os dados do segurado.",
                "success",
            )
            return redirect(
                url_for(
                    "atendimentos.etapa_segurado_previdenciario",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Dados do atendimento previdenciário salvos com sucesso!",
            "success",
        )
        return redirect(
            url_for(
                "atendimentos.etapa_atendimento_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/atendimento.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="atendimento",
            url_proxima=url_for(
                "atendimentos.etapa_segurado_previdenciario",
                atendimento_id=atendimento.id,
            ),
        ),
    )



# ============================================================
# ETAPA 2 — DADOS DO SEGURADO PREVIDENCIÁRIO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/segurado",
    methods=["GET", "POST"],
)
@login_required
def etapa_segurado_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    cliente = atendimento.cliente

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    

    url_anterior = url_for(
        "atendimentos.etapa_atendimento_previdenciario",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_historico_contributivo_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.nit_pis_pasep = texto_formulario("nit_pis_pasep")
        ficha.rg = texto_formulario("rg")
        ficha.orgao_expedidor = texto_formulario("orgao_expedidor")

        ficha.escolaridade = texto_formulario("escolaridade")
        if ficha.escolaridade not in FichaPrevidenciaria.ESCOLARIDADES:
            ficha.escolaridade = None

        ficha.escolaridade_outro = texto_formulario(
            "escolaridade_outro"
        )
        if ficha.escolaridade != FichaPrevidenciaria.ESCOLARIDADE_OUTRA:
            ficha.escolaridade_outro = None

        ficha.profissao = texto_formulario("profissao")
        ficha.ocupacao_atual = texto_formulario("ocupacao_atual")

        ficha.categoria_segurado = texto_formulario(
            "categoria_segurado"
        )
        if (
            ficha.categoria_segurado
            not in FichaPrevidenciaria.CATEGORIAS_SEGURADO
        ):
            ficha.categoria_segurado = None

        ficha.categoria_segurado_outro = texto_formulario(
            "categoria_segurado_outro"
        )
        if (
            ficha.categoria_segurado
            != FichaPrevidenciaria.CATEGORIA_OUTRA
        ):
            ficha.categoria_segurado_outro = None

        ficha.situacao_profissional = texto_formulario(
            "situacao_profissional"
        )
        if (
            ficha.situacao_profissional
            not in FichaPrevidenciaria.SITUACOES_PROFISSIONAIS
        ):
            ficha.situacao_profissional = None

        ficha.situacao_profissional_outro = texto_formulario(
            "situacao_profissional_outro"
        )
        if (
            ficha.situacao_profissional
            != FichaPrevidenciaria.SITUACAO_OUTRA
        ):
            ficha.situacao_profissional_outro = None

        try:
            ficha.data_ultimo_trabalho = data_formulario(
                "data_ultimo_trabalho"
            )
            ficha.data_inicio_deficiencia = data_formulario(
                "data_inicio_deficiencia"
            )
        except ValueError:
            flash(
                "Informe datas válidas nos dados do segurado.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/segurado.html",
                cliente=cliente,
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="segurado",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.possui_dependentes = texto_formulario(
            "possui_dependentes"
        )
        if ficha.possui_dependentes not in FichaPrevidenciaria.RESPOSTAS:
            ficha.possui_dependentes = None

        ficha.quantidade_dependentes = inteiro_formulario(
            "quantidade_dependentes"
        )
        ficha.dependentes_descricao = texto_formulario(
            "dependentes_descricao"
        )

        if ficha.possui_dependentes != FichaPrevidenciaria.RESPOSTA_SIM:
            ficha.quantidade_dependentes = None
            ficha.dependentes_descricao = None

        ficha.possui_deficiencia = texto_formulario(
            "possui_deficiencia"
        )
        if ficha.possui_deficiencia not in FichaPrevidenciaria.RESPOSTAS:
            ficha.possui_deficiencia = None

        ficha.tipo_deficiencia = texto_formulario(
            "tipo_deficiencia"
        )

        if ficha.possui_deficiencia != FichaPrevidenciaria.RESPOSTA_SIM:
            ficha.tipo_deficiencia = None
            ficha.data_inicio_deficiencia = None

        ficha.observacoes_segurado = texto_formulario(
            "observacoes_segurado"
        )

        ficha.etapa_atual = "segurado"
        ficha.etapa_segurado_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados do segurado. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/segurado.html",
                cliente=cliente,
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="segurado",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Dados do segurado salvos. "
                "A próxima etapa será o Histórico contributivo.",
                "success",
            )
        else:
            flash(
                "✅ Dados do segurado salvos com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                "atendimentos.etapa_segurado_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/segurado.html",
        cliente=cliente,
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="segurado",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )



# ============================================================
# ETAPA 3 — HISTÓRICO CONTRIBUTIVO PREVIDENCIÁRIO
# ============================================================

@atendimento_bp.route(
    (
        "/atendimentos/<int:atendimento_id>/previdenciaria/"
        "historico-contributivo"
    ),
    methods=["GET", "POST"],
)
@login_required
def etapa_historico_contributivo_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_segurado_previdenciario",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_beneficio_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_resposta = [
            "possui_cnis",
            "cnis_atualizado",
            "possui_vinculos_ausentes_cnis",
            "possui_contribuicoes_abaixo_minimo",
            "possui_contribuicoes_em_atraso",
            "possui_periodo_rural",
            "possui_atividade_especial",
            "possui_tempo_servico_publico",
            "possui_tempo_militar",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaPrevidenciaria.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        try:
            ficha.data_emissao_cnis = data_formulario(
                "data_emissao_cnis"
            )
        except ValueError:
            flash(
                "Informe uma data de emissão do CNIS válida.",
                "danger",
            )
            return render_template(
                (
                    "atendimentos/previdenciaria/"
                    "historico_contributivo.html"
                ),
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="historico_contributivo",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.vinculos_ausentes_descricao = texto_formulario(
            "vinculos_ausentes_descricao"
        )
        if (
            ficha.possui_vinculos_ausentes_cnis
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.vinculos_ausentes_descricao = None

        ficha.contribuicoes_abaixo_minimo_descricao = texto_formulario(
            "contribuicoes_abaixo_minimo_descricao"
        )
        if (
            ficha.possui_contribuicoes_abaixo_minimo
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.contribuicoes_abaixo_minimo_descricao = None

        ficha.contribuicoes_em_atraso_descricao = texto_formulario(
            "contribuicoes_em_atraso_descricao"
        )
        if (
            ficha.possui_contribuicoes_em_atraso
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.contribuicoes_em_atraso_descricao = None

        ficha.periodo_rural_descricao = texto_formulario(
            "periodo_rural_descricao"
        )
        if (
            ficha.possui_periodo_rural
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.periodo_rural_descricao = None

        ficha.atividade_especial_descricao = texto_formulario(
            "atividade_especial_descricao"
        )
        if (
            ficha.possui_atividade_especial
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.atividade_especial_descricao = None

        ficha.tempo_servico_publico_descricao = texto_formulario(
            "tempo_servico_publico_descricao"
        )
        if (
            ficha.possui_tempo_servico_publico
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.tempo_servico_publico_descricao = None

        ficha.tempo_militar_descricao = texto_formulario(
            "tempo_militar_descricao"
        )
        if (
            ficha.possui_tempo_militar
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.tempo_militar_descricao = None

        ficha.tempo_contribuicao_estimado = texto_formulario(
            "tempo_contribuicao_estimado"
        )
        ficha.carencia_estimada = inteiro_formulario(
            "carencia_estimada"
        )
        ficha.observacoes_historico_contributivo = texto_formulario(
            "observacoes_historico_contributivo"
        )

        if ficha.possui_cnis != FichaPrevidenciaria.RESPOSTA_SIM:
            ficha.cnis_atualizado = None
            ficha.data_emissao_cnis = None

        ficha.etapa_atual = "historico_contributivo"
        ficha.etapa_historico_contributivo_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar o histórico contributivo. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                (
                    "atendimentos/previdenciaria/"
                    "historico_contributivo.html"
                ),
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="historico_contributivo",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Histórico contributivo salvo. "
                "A etapa Benefício será criada em seguida.",
                "success",
            )
        else:
            flash(
                "✅ Histórico contributivo salvo com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                (
                    "atendimentos."
                    "etapa_historico_contributivo_previdenciario"
                ),
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/historico_contributivo.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="historico_contributivo",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )



# ============================================================
# ETAPA 4 — BENEFÍCIO PRETENDIDO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/beneficio",
    methods=["GET", "POST"],
)
@login_required
def etapa_beneficio_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        (
            "atendimentos."
            "etapa_historico_contributivo_previdenciario"
        ),
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_saude_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.beneficio_principal = texto_formulario(
            "beneficio_principal"
        )
        if (
            ficha.beneficio_principal
            not in FichaPrevidenciaria.TIPOS_BENEFICIO
        ):
            ficha.beneficio_principal = None

        ficha.beneficio_principal_outro = texto_formulario(
            "beneficio_principal_outro"
        )
        if (
            ficha.beneficio_principal
            != FichaPrevidenciaria.BENEFICIO_OUTRO
        ):
            ficha.beneficio_principal_outro = None

        ficha.beneficio_alternativo = texto_formulario(
            "beneficio_alternativo"
        )
        if (
            ficha.beneficio_alternativo
            not in FichaPrevidenciaria.TIPOS_BENEFICIO
        ):
            ficha.beneficio_alternativo = None

        ficha.beneficio_alternativo_outro = texto_formulario(
            "beneficio_alternativo_outro"
        )
        if (
            ficha.beneficio_alternativo
            != FichaPrevidenciaria.BENEFICIO_OUTRO
        ):
            ficha.beneficio_alternativo_outro = None

        ficha.objetivo_cliente = texto_formulario(
            "objetivo_cliente"
        )
        ficha.motivo_pedido = texto_formulario(
            "motivo_pedido"
        )

        campos_resposta = [
            "possui_qualidade_segurado",
            "carencia_cumprida",
            "possui_direito_adquirido",
            "aplica_regra_transicao",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaPrevidenciaria.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        ficha.qualidade_segurado_observacoes = texto_formulario(
            "qualidade_segurado_observacoes"
        )
        ficha.carencia_observacoes = texto_formulario(
            "carencia_observacoes"
        )
        ficha.direito_adquirido_observacoes = texto_formulario(
            "direito_adquirido_observacoes"
        )
        ficha.regra_transicao_descricao = texto_formulario(
            "regra_transicao_descricao"
        )

        try:
            ficha.data_prevista_beneficio = data_formulario(
                "data_prevista_beneficio"
            )
            ficha.renda_mensal_estimada = decimal_formulario(
                "renda_mensal_estimada"
            )
        except ValueError:
            flash(
                "Informe uma data e uma renda mensal estimada válidas.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/beneficio.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="beneficio",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.observacoes_beneficio = texto_formulario(
            "observacoes_beneficio"
        )

        ficha.etapa_atual = "beneficio"
        ficha.etapa_beneficio_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados do benefício. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/beneficio.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="beneficio",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Benefício salvo. "
                "A próxima etapa será Saúde e incapacidade.",
                "success",
            )
        else:
            flash(
                "✅ Dados do benefício salvos com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                "atendimentos.etapa_beneficio_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/beneficio.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="beneficio",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )



# ============================================================
# ETAPA 5 — SAÚDE E INCAPACIDADE
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/saude",
    methods=["GET", "POST"],
)
@login_required
def etapa_saude_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_beneficio_previdenciario",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_documentacao_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_resposta = [
            "possui_doenca_incapacidade",
            "realiza_tratamento",
            "possui_laudo_medico",
            "possui_exames",
            "possui_receitas",
            "houve_acidente",
            "possui_cat",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaPrevidenciaria.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        ficha.diagnostico_principal = texto_formulario(
            "diagnostico_principal"
        )
        ficha.cid_principal = texto_formulario(
            "cid_principal"
        )
        ficha.outros_diagnosticos = texto_formulario(
            "outros_diagnosticos"
        )

        try:
            ficha.data_inicio_doenca = data_formulario(
                "data_inicio_doenca"
            )
            ficha.data_inicio_incapacidade = data_formulario(
                "data_inicio_incapacidade"
            )
            ficha.data_acidente = data_formulario(
                "data_acidente"
            )
        except ValueError:
            flash(
                "Informe datas válidas na etapa Saúde e incapacidade.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/saude.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="saude",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        ficha.tipo_incapacidade = texto_formulario(
            "tipo_incapacidade"
        )
        if (
            ficha.tipo_incapacidade
            not in FichaPrevidenciaria.TIPOS_INCAPACIDADE
        ):
            ficha.tipo_incapacidade = None

        ficha.origem_incapacidade = texto_formulario(
            "origem_incapacidade"
        )
        if (
            ficha.origem_incapacidade
            not in FichaPrevidenciaria.ORIGENS_INCAPACIDADE
        ):
            ficha.origem_incapacidade = None

        ficha.origem_incapacidade_outro = texto_formulario(
            "origem_incapacidade_outro"
        )
        if (
            ficha.origem_incapacidade
            != FichaPrevidenciaria.ORIGEM_OUTRA
        ):
            ficha.origem_incapacidade_outro = None

        ficha.atividade_prejudicada = texto_formulario(
            "atividade_prejudicada"
        )
        ficha.limitacoes_funcionais = texto_formulario(
            "limitacoes_funcionais"
        )

        ficha.tratamento_descricao = texto_formulario(
            "tratamento_descricao"
        )
        ficha.nome_medico_assistente = texto_formulario(
            "nome_medico_assistente"
        )
        ficha.especialidade_medico = texto_formulario(
            "especialidade_medico"
        )

        if (
            ficha.realiza_tratamento
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.tratamento_descricao = None
            ficha.nome_medico_assistente = None
            ficha.especialidade_medico = None

        ficha.acidente_descricao = texto_formulario(
            "acidente_descricao"
        )

        if ficha.houve_acidente != FichaPrevidenciaria.RESPOSTA_SIM:
            ficha.data_acidente = None
            ficha.acidente_descricao = None
            ficha.possui_cat = None

        ficha.observacoes_saude = texto_formulario(
            "observacoes_saude"
        )

        if (
            ficha.possui_doenca_incapacidade
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.diagnostico_principal = None
            ficha.cid_principal = None
            ficha.outros_diagnosticos = None
            ficha.data_inicio_doenca = None
            ficha.data_inicio_incapacidade = None
            ficha.tipo_incapacidade = None
            ficha.origem_incapacidade = None
            ficha.origem_incapacidade_outro = None
            ficha.atividade_prejudicada = None
            ficha.limitacoes_funcionais = None

        ficha.etapa_atual = "saude"
        ficha.etapa_saude_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados de saúde. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/saude.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="saude",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Dados de saúde salvos. "
                "A próxima etapa será Documentação.",
                "success",
            )
        else:
            flash(
                "✅ Dados de saúde salvos com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                "atendimentos.etapa_saude_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/saude.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="saude",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )



# ============================================================
# ETAPA 6 — DOCUMENTAÇÃO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/documentacao",
    methods=["GET", "POST"],
)
@login_required
def etapa_documentacao_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_saude_previdenciario",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_inss_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        campos_documentos = [
            "documento_rg",
            "documento_cpf",
            "documento_comprovante_residencia",
            "documento_cnis",
            "documento_ctps",
            "documento_carnes_contribuicao",
            "documento_guias_gps",
            "documento_ppp",
            "documento_ltcat",
            "documento_certidao_tempo_contribuicao",
            "documento_laudos_medicos",
            "documento_exames_medicos",
            "documento_processo_inss",
            "documento_carta_indeferimento",
            "documento_procuracao",
        ]

        for campo in campos_documentos:
            setattr(
                ficha,
                campo,
                request.form.get(campo) == "1",
            )

        ficha.documentos_outros = texto_formulario(
            "documentos_outros"
        )
        ficha.documentos_pendentes = texto_formulario(
            "documentos_pendentes"
        )
        ficha.observacoes_documentacao = texto_formulario(
            "observacoes_documentacao"
        )

        ficha.etapa_atual = "documentacao"
        ficha.etapa_documentacao_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar a documentação. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/documentacao.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="documentacao",
                    url_anterior=url_anterior,
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Documentação salva. "
                "A próxima etapa será Processo no INSS.",
                "success",
            )
        else:
            flash(
                "✅ Documentação salva com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                "atendimentos.etapa_documentacao_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/documentacao.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="documentacao",
            url_anterior=url_anterior,
            url_proxima=url_proxima,
        ),
    )



# ============================================================
# ETAPA 7 — PROCESSO ADMINISTRATIVO NO INSS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/inss",
    methods=["GET", "POST"],
)
@login_required
def etapa_inss_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_documentacao_previdenciario",
        atendimento_id=atendimento.id,
    )

    url_proxima = url_for(
        "atendimentos.etapa_resumo_previdenciario",
        atendimento_id=atendimento.id,
    )

    situacoes_requerimento = {
        "NAO_PROTOCOLADO": "Ainda não protocolado",
        "EM_ANALISE": "Em análise",
        "DEFERIDO": "Deferido",
        "INDEFERIDO": "Indeferido",
        "EXIGENCIA": "Em exigência",
        "AGUARDANDO_PERICIA": "Aguardando perícia",
        "RECURSO": "Em recurso",
        "ARQUIVADO": "Arquivado",
        "OUTRA": "Outra situação",
    }

    resultados_pericia = FichaPrevidenciaria.RESULTADOS_PERICIA

    def contexto_pagina():
        return {
            **contexto_etapa_previdenciaria(
                atendimento=atendimento,
                ficha=ficha,
                etapa_atual="inss",
                url_anterior=url_anterior,
                url_proxima=url_proxima,
            ),
            "situacoes_requerimento": situacoes_requerimento,
            "resultados_pericia": resultados_pericia,
        }

    if request.method == "POST":
        campos_resposta = [
            "possui_requerimento_inss",
            "possui_exigencia",
            "possui_pericia",
            "possui_recurso",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(campo)

            if valor not in FichaPrevidenciaria.RESPOSTAS:
                valor = None

            setattr(ficha, campo, valor)

        ficha.numero_protocolo = texto_formulario(
            "numero_protocolo"
        )
        ficha.numero_beneficio = texto_formulario(
            "numero_beneficio"
        )
        ficha.agencia_previdencia_social = texto_formulario(
            "agencia_previdencia_social"
        )
        ficha.cidade_agencia = texto_formulario(
            "cidade_agencia"
        )

        ficha.situacao_requerimento = texto_formulario(
            "situacao_requerimento"
        )
        if (
            ficha.situacao_requerimento
            not in situacoes_requerimento
        ):
            ficha.situacao_requerimento = None

        ficha.exigencia_descricao = texto_formulario(
            "exigencia_descricao"
        )
        ficha.local_pericia = texto_formulario(
            "local_pericia"
        )

        ficha.resultado_pericia = texto_formulario(
            "resultado_pericia"
        )
        if (
            ficha.resultado_pericia
            not in resultados_pericia
        ):
            ficha.resultado_pericia = None

        ficha.resultado_pericia_descricao = texto_formulario(
            "resultado_pericia_descricao"
        )
        ficha.motivo_indeferimento = texto_formulario(
            "motivo_indeferimento"
        )
        ficha.numero_recurso = texto_formulario(
            "numero_recurso"
        )
        ficha.resultado_recurso = texto_formulario(
            "resultado_recurso"
        )
        ficha.observacoes_inss = texto_formulario(
            "observacoes_inss"
        )

        try:
            ficha.data_entrada_requerimento = data_formulario(
                "data_entrada_requerimento"
            )
            ficha.data_inicio_beneficio = data_formulario(
                "data_inicio_beneficio"
            )
            ficha.data_limite_exigencia = data_formulario(
                "data_limite_exigencia"
            )
            ficha.data_pericia = data_formulario(
                "data_pericia"
            )
            ficha.horario_pericia = horario_formulario(
                "horario_pericia"
            )
            ficha.data_decisao_inss = data_formulario(
                "data_decisao_inss"
            )
            ficha.data_recurso = data_formulario(
                "data_recurso"
            )
        except ValueError:
            flash(
                "Informe datas e horários válidos na etapa do INSS.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/inss.html",
                **contexto_pagina(),
            )

        if (
            ficha.possui_requerimento_inss
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.numero_protocolo = None
            ficha.numero_beneficio = None
            ficha.data_entrada_requerimento = None
            ficha.data_inicio_beneficio = None
            ficha.agencia_previdencia_social = None
            ficha.cidade_agencia = None
            ficha.situacao_requerimento = None

        if (
            ficha.possui_exigencia
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.data_limite_exigencia = None
            ficha.exigencia_descricao = None

        if (
            ficha.possui_pericia
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.data_pericia = None
            ficha.horario_pericia = None
            ficha.local_pericia = None
            ficha.resultado_pericia = None
            ficha.resultado_pericia_descricao = None

        if (
            ficha.possui_recurso
            != FichaPrevidenciaria.RESPOSTA_SIM
        ):
            ficha.numero_recurso = None
            ficha.data_recurso = None
            ficha.resultado_recurso = None

        ficha.etapa_atual = "inss"
        ficha.etapa_inss_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar os dados do processo no INSS. "
                "Verifique as informações e tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/inss.html",
                **contexto_pagina(),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Processo no INSS salvo. "
                "A próxima etapa será Resumo e análise.",
                "success",
            )
        else:
            flash(
                "✅ Processo no INSS salvo com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(url_proxima)

        return redirect(
            url_for(
                "atendimentos.etapa_inss_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/inss.html",
        **contexto_pagina(),
    )



# ============================================================
# ETAPA 8 — RESUMO E ANÁLISE JURÍDICA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/resumo",
    methods=["GET", "POST"],
)
@login_required
def etapa_resumo_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(atendimento_id)

    if atendimento is None:
        return redirect(
            url_for("clientes.listar_clientes")
        )

    ficha = obter_ou_criar_ficha_previdenciaria(atendimento)

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_inss_previdenciario",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        ficha.resumo_previdenciario = texto_formulario(
            "resumo_previdenciario"
        )
        ficha.analise_juridica = texto_formulario(
            "analise_juridica"
        )
        ficha.estrategia_sugerida = texto_formulario(
            "estrategia_sugerida"
        )
        ficha.riscos_identificados = texto_formulario(
            "riscos_identificados"
        )
        ficha.providencias_recomendadas = texto_formulario(
            "providencias_recomendadas"
        )
        ficha.pendencias_gerais = texto_formulario(
            "pendencias_gerais"
        )
        ficha.observacoes_gerais = texto_formulario(
            "observacoes_gerais"
        )

        ficha.etapa_atual = "resumo"
        ficha.etapa_resumo_concluida = True

        salvar_auditoria(atendimento, ficha)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "Não foi possível salvar o resumo e a análise jurídica. "
                "Tente novamente.",
                "danger",
            )
            return render_template(
                "atendimentos/previdenciaria/resumo.html",
                **contexto_etapa_previdenciaria(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="resumo",
                    url_anterior=url_anterior,
                ),
            )

        acao = request.form.get("acao", "salvar")

        if acao == "salvar_proxima":
            flash(
                "✅ Ficha previdenciária finalizada com sucesso!",
                "success",
            )
            return redirect(
                url_for(
                    "clientes.detalhes_cliente",
                    id=atendimento.cliente_id,
                )
            )

        flash(
            "✅ Resumo e análise jurídica salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_resumo_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/previdenciaria/resumo.html",
        **contexto_etapa_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="resumo",
            url_anterior=url_anterior,
        ),
    )


# ============================================================
# ROTA ANTIGA DA FICHA TRABALHISTA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def ficha_trabalhista(atendimento_id):
    """
    Mantém compatibilidade com links antigos do sistema.

    Todo acesso à rota antiga é redirecionado para a primeira
    etapa do novo formulário.
    """

    if request.method == "POST":
        flash(
            "A ficha trabalhista agora está organizada por etapas. "
            "Revise os dados na nova tela antes de salvar.",
            "info",
        )

    return redirect(
        url_for(
            "atendimentos.etapa_atendimento",
            atendimento_id=atendimento_id,
        )
    )


# ============================================================
# ETAPA 1 — DADOS DO ATENDIMENTO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/atendimento",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_atendimento(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        titulo = texto_formulario(
            "titulo",
        )

        status = request.form.get(
            "status",
            Atendimento.STATUS_RASCUNHO,
        ).strip()

        if not titulo:
            flash(
                "Informe o título do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/atendimento.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_cliente",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if status not in Atendimento.STATUS:
            status = Atendimento.STATUS_RASCUNHO

        try:
            data_atendimento = data_formulario(
                "data_atendimento",
            )

            horario_atendimento = horario_formulario(
                "horario_atendimento",
            )

        except ValueError:
            flash(
                "Informe uma data e um horário válidos.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/atendimento.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_cliente",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if data_atendimento is None:
            flash(
                "Informe a data do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/atendimento.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_cliente",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        atendimento.titulo = titulo
        atendimento.status = status
        atendimento.data_atendimento = data_atendimento
        atendimento.horario_atendimento = horario_atendimento

        atendimento.resumo_caso = texto_formulario(
            "resumo_caso",
        )

        atendimento.observacoes_internas = texto_formulario(
            "observacoes_internas",
        )

        ficha.etapa_atual = "atendimento"
        ficha.etapa_atendimento_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do atendimento. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/atendimento.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_for(
                        "atendimentos.etapa_cliente",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            flash(
                "✅ Etapa Atendimento salva. "
                "Agora criaremos a etapa Cliente.",
                "success",
            )

        else:
            flash(
                "✅ Dados do atendimento salvos com sucesso!",
                "success",
            )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_cliente",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_atendimento",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/atendimento.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="atendimento",
            url_proxima=url_for(
                "atendimentos.etapa_cliente",
                atendimento_id=atendimento.id,
            ),
        ),
    )


# ============================================================
# ETAPA 2 — DADOS DO CLIENTE
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/cliente",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_cliente(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    cliente = atendimento.cliente

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    

    if request.method == "POST":
        ficha.orgao_expedidor = texto_formulario(
            "orgao_expedidor",
        )

        ficha.escolaridade = texto_formulario(
            "escolaridade",
        )

        if ficha.escolaridade not in FichaTrabalhista.ESCOLARIDADES:
            ficha.escolaridade = None

        ficha.escolaridade_outro = texto_formulario(
            "escolaridade_outro",
        )

        ficha.contato_parente_amigo = texto_formulario(
            "contato_parente_amigo",
        )

        ficha.contato_parente_amigo_telefone = texto_formulario(
            "contato_parente_amigo_telefone",
        )

        ficha.contato_parente_amigo_relacao = texto_formulario(
            "contato_parente_amigo_relacao",
        )

        ficha.instagram = texto_formulario(
            "instagram",
        )

        ficha.facebook = texto_formulario(
            "facebook",
        )

        ficha.tiktok = texto_formulario(
            "tiktok",
        )

        ficha.outra_rede_social = texto_formulario(
            "outra_rede_social",
        )

        ficha.nome_pai = texto_formulario(
            "nome_pai",
        )

        ficha.nome_mae = texto_formulario(
            "nome_mae",
        )

        ficha.possui_filhos_menores = texto_formulario(
            "possui_filhos_menores",
        )

        if ficha.possui_filhos_menores not in FichaTrabalhista.RESPOSTAS:
            ficha.possui_filhos_menores = None

        ficha.quantidade_filhos_menores = inteiro_formulario(
            "quantidade_filhos_menores",
        )

        if ficha.possui_filhos_menores != "SIM":
            ficha.quantidade_filhos_menores = None

        ficha.possui_deficiencia = texto_formulario(
            "possui_deficiencia",
        )

        if ficha.possui_deficiencia not in FichaTrabalhista.RESPOSTAS:
            ficha.possui_deficiencia = None

        ficha.descricao_deficiencia = texto_formulario(
            "descricao_deficiencia",
        )

        if ficha.possui_deficiencia != "SIM":
            ficha.descricao_deficiencia = None

        ficha.recebeu_beneficio_inss = texto_formulario(
            "recebeu_beneficio_inss",
        )

        if ficha.recebeu_beneficio_inss not in FichaTrabalhista.RESPOSTAS:
            ficha.recebeu_beneficio_inss = None

        ficha.beneficio_inss_descricao = texto_formulario(
            "beneficio_inss_descricao",
        )

        if ficha.recebeu_beneficio_inss != "SIM":
            ficha.beneficio_inss_descricao = None

        ficha.observacoes_dados_cliente = texto_formulario(
            "observacoes_dados_cliente",
        )

        ficha.etapa_atual = "cliente"
        ficha.etapa_cliente_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do cliente. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/cliente.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="cliente",
                    url_anterior=url_for(
                        "atendimentos.etapa_atendimento",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_empresa",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados do cliente salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_empresa",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_cliente",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/cliente.html",
        cliente=cliente,
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="cliente",
            url_anterior=url_for(
                "atendimentos.etapa_atendimento",
                atendimento_id=atendimento.id,
            ),
            url_proxima=url_for(
                "atendimentos.etapa_empresa",
                atendimento_id=atendimento.id,
            ),
        ),
    )


# ============================================================
# ETAPA 3 — DADOS DA EMPRESA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/empresa",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_empresa(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        ficha.empresa_nome = texto_formulario(
            "empresa_nome",
        )

        ficha.empresa_nome_fantasia = texto_formulario(
            "empresa_nome_fantasia",
        )

        ficha.empresa_cnpj_cpf = texto_formulario(
            "empresa_cnpj_cpf",
        )

        ficha.empresa_endereco = texto_formulario(
            "empresa_endereco",
        )

        ficha.empresa_cidade = texto_formulario(
            "empresa_cidade",
        )

        ficha.empresa_telefone = texto_formulario(
            "empresa_telefone",
        )

        ficha.empresa_whatsapp = texto_formulario(
            "empresa_whatsapp",
        )

        ficha.empresa_ramo_atividade = texto_formulario(
            "empresa_ramo_atividade",
        )

        ficha.empresa_proprietario = texto_formulario(
            "empresa_proprietario",
        )

        ficha.empresa_socio = texto_formulario(
            "empresa_socio",
        )

        ficha.empresa_grupo_economico = texto_formulario(
            "empresa_grupo_economico",
        )

        if ficha.empresa_grupo_economico not in FichaTrabalhista.RESPOSTAS:
            ficha.empresa_grupo_economico = None

        ficha.empresa_grupo_economico_qual = texto_formulario(
            "empresa_grupo_economico_qual",
        )

        if ficha.empresa_grupo_economico != "SIM":
            ficha.empresa_grupo_economico_qual = None

        ficha.empresa_mudou_nome = texto_formulario(
            "empresa_mudou_nome",
        )

        if ficha.empresa_mudou_nome not in FichaTrabalhista.RESPOSTAS:
            ficha.empresa_mudou_nome = None

        ficha.empresa_nome_anterior = texto_formulario(
            "empresa_nome_anterior",
        )

        if ficha.empresa_mudou_nome != "SIM":
            ficha.empresa_nome_anterior = None

        ficha.empresa_foi_vendida = texto_formulario(
            "empresa_foi_vendida",
        )

        if ficha.empresa_foi_vendida not in FichaTrabalhista.RESPOSTAS:
            ficha.empresa_foi_vendida = None

        ficha.empresa_trocou_cnpj = texto_formulario(
            "empresa_trocou_cnpj",
        )

        if ficha.empresa_trocou_cnpj not in FichaTrabalhista.RESPOSTAS:
            ficha.empresa_trocou_cnpj = None

        ficha.empresa_cnpj_anterior = texto_formulario(
            "empresa_cnpj_anterior",
        )

        if ficha.empresa_trocou_cnpj != "SIM":
            ficha.empresa_cnpj_anterior = None

        ficha.prestava_servicos_outra_empresa = texto_formulario(
            "prestava_servicos_outra_empresa",
        )

        if (
            ficha.prestava_servicos_outra_empresa
            not in FichaTrabalhista.RESPOSTAS
        ):
            ficha.prestava_servicos_outra_empresa = None

        ficha.prestava_servicos_empresa_qual = texto_formulario(
            "prestava_servicos_empresa_qual",
        )

        if ficha.prestava_servicos_outra_empresa != "SIM":
            ficha.prestava_servicos_empresa_qual = None

        ficha.trabalhava_dependencias_outra_empresa = texto_formulario(
            "trabalhava_dependencias_outra_empresa",
        )

        if (
            ficha.trabalhava_dependencias_outra_empresa
            not in FichaTrabalhista.RESPOSTAS
        ):
            ficha.trabalhava_dependencias_outra_empresa = None

        ficha.trabalhava_dependencias_empresa_qual = texto_formulario(
            "trabalhava_dependencias_empresa_qual",
        )

        if ficha.trabalhava_dependencias_outra_empresa != "SIM":
            ficha.trabalhava_dependencias_empresa_qual = None

        ficha.observacoes_empresa = texto_formulario(
            "observacoes_empresa",
        )

        ficha.etapa_atual = "empresa"
        ficha.etapa_empresa_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da empresa. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/empresa.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="empresa",
                    url_anterior=url_for(
                        "atendimentos.etapa_cliente",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_admissao",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados da empresa salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_admissao",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_empresa",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/empresa.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="empresa",
            url_anterior=url_for(
                "atendimentos.etapa_cliente",
                atendimento_id=atendimento.id,
            ),
            url_proxima=url_for(
                "atendimentos.etapa_admissao",
                atendimento_id=atendimento.id,
            ),
        ),
    )


# ============================================================
# ETAPA 4 — ADMISSÃO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/admissao",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_admissao(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        try:
            ficha.data_admissao_real = data_formulario(
                "data_admissao_real",
            )

            ficha.data_admissao_carteira = data_formulario(
                "data_admissao_carteira",
            )

        except ValueError:
            flash(
                "Informe datas de admissão válidas.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/admissao.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="admissao",
                    url_anterior=url_for(
                        "atendimentos.etapa_empresa",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_contrato",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        ficha.responsavel_contratacao = texto_formulario(
            "responsavel_contratacao",
        )

        campos_resposta = [
            "foi_indicado",
            "realizou_entrevista",
            "fez_exame_admissional",
            "recebeu_copia_exame_admissional",
            "assinou_contrato_antes_inicio",
            "recebeu_copia_contrato",
            "assinou_documento_em_branco",
            "assinou_contrato_trabalho",
            "assinou_ficha_registro",
            "assinou_termo_responsabilidade",
            "assinou_vale_transporte",
            "assinou_regulamento_interno",
            "assinou_termo_confidencialidade",
            "assinou_outros_documentos",
            "recebeu_copia_documentos_admissao",
            "carteira_trabalho_assinada",
            "carteira_assinada_mesmo_dia",
            "carteira_nunca_assinada",
            "recebeu_treinamento",
            "recebeu_uniforme",
            "recebeu_epi",
            "assinou_ficha_entrega_epi",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.indicado_por = texto_formulario(
            "indicado_por",
        )

        if ficha.foi_indicado != "SIM":
            ficha.indicado_por = None

        ficha.exame_admissional_clinica = texto_formulario(
            "exame_admissional_clinica",
        )

        if ficha.fez_exame_admissional != "SIM":
            ficha.exame_admissional_clinica = None
            ficha.recebeu_copia_exame_admissional = None

        ficha.outros_documentos_admissao = texto_formulario(
            "outros_documentos_admissao",
        )

        if ficha.assinou_outros_documentos != "SIM":
            ficha.outros_documentos_admissao = None

        ficha.carteira_dias_apos_inicio = inteiro_formulario(
            "carteira_dias_apos_inicio",
        )

        if ficha.carteira_assinada_mesmo_dia == "SIM":
            ficha.carteira_dias_apos_inicio = 0

        if ficha.carteira_trabalho_assinada != "SIM":
            ficha.carteira_assinada_mesmo_dia = None
            ficha.carteira_dias_apos_inicio = None

        if ficha.carteira_nunca_assinada == "SIM":
            ficha.carteira_trabalho_assinada = "NAO"
            ficha.carteira_assinada_mesmo_dia = None
            ficha.carteira_dias_apos_inicio = None
            ficha.data_admissao_carteira = None

        ficha.treinamento_duracao = texto_formulario(
            "treinamento_duracao",
        )

        if ficha.recebeu_treinamento != "SIM":
            ficha.treinamento_duracao = None

        ficha.epis_recebidos = texto_formulario(
            "epis_recebidos",
        )

        if ficha.recebeu_epi != "SIM":
            ficha.epis_recebidos = None
            ficha.assinou_ficha_entrega_epi = None

        ficha.observacoes_admissao = texto_formulario(
            "observacoes_admissao",
        )

        ficha.etapa_atual = "admissao"
        ficha.etapa_admissao_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da admissão. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/admissao.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="admissao",
                    url_anterior=url_for(
                        "atendimentos.etapa_empresa",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_contrato",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados da admissão salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_contrato",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_admissao",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/admissao.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="admissao",
            url_anterior=url_for(
                "atendimentos.etapa_empresa",
                atendimento_id=atendimento.id,
            ),
            url_proxima=url_for(
                "atendimentos.etapa_contrato",
                atendimento_id=atendimento.id,
            ),
        ),
    )


# ============================================================
# ETAPA 5 — CONTRATO DE TRABALHO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/contrato",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_contrato(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        ficha.tipo_contrato = texto_formulario(
            "tipo_contrato",
        )

        if ficha.tipo_contrato not in FichaTrabalhista.TIPOS_CONTRATO:
            ficha.tipo_contrato = None

        ficha.tipo_contrato_outro = texto_formulario(
            "tipo_contrato_outro",
        )

        if ficha.tipo_contrato != FichaTrabalhista.CONTRATO_OUTRO:
            ficha.tipo_contrato_outro = None

        campos_resposta = [
            "contrato_experiencia_prorrogado",
            "exercia_mais_uma_funcao",
            "recebeu_promocao",
            "possui_documento_promocao",
            "recebeu_aumento_promocao",
            "mudou_setor",
            "mudou_cidade",
            "recebeu_adicional_transferencia",
            "exerceu_funcao_superior_sem_aumento",
            "substituia_gerente_superior",
            "substituia_colegas_afastados",
            "assinou_outro_contrato_admissao",
            "recebeu_copia_outro_contrato",
            "assinou_outros_documentos_branco",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.quantidade_prorrogacoes_experiencia = inteiro_formulario(
            "quantidade_prorrogacoes_experiencia",
        )

        if ficha.contrato_experiencia_prorrogado != "SIM":
            ficha.quantidade_prorrogacoes_experiencia = None

        ficha.cargo_registrado_carteira = texto_formulario(
            "cargo_registrado_carteira",
        )

        ficha.funcao_real_exercida = texto_formulario(
            "funcao_real_exercida",
        )

        ficha.funcoes_acumuladas = texto_formulario(
            "funcoes_acumuladas",
        )

        if ficha.exercia_mais_uma_funcao != "SIM":
            ficha.funcoes_acumuladas = None

        ficha.promocao_qual = texto_formulario(
            "promocao_qual",
        )

        if ficha.recebeu_promocao != "SIM":
            ficha.promocao_qual = None
            ficha.possui_documento_promocao = None
            ficha.recebeu_aumento_promocao = None

        ficha.quantidade_mudancas_setor = inteiro_formulario(
            "quantidade_mudancas_setor",
        )

        ficha.setores_trabalhados = texto_formulario(
            "setores_trabalhados",
        )

        if ficha.mudou_setor != "SIM":
            ficha.quantidade_mudancas_setor = None
            ficha.setores_trabalhados = None

        ficha.cidades_trabalhadas = texto_formulario(
            "cidades_trabalhadas",
        )

        if ficha.mudou_cidade != "SIM":
            ficha.cidades_trabalhadas = None
            ficha.recebeu_adicional_transferencia = None

        ficha.funcao_superior_exercida = texto_formulario(
            "funcao_superior_exercida",
        )

        if ficha.exerceu_funcao_superior_sem_aumento != "SIM":
            ficha.funcao_superior_exercida = None

        ficha.substituia_gerente_detalhes = texto_formulario(
            "substituia_gerente_detalhes",
        )

        if ficha.substituia_gerente_superior != "SIM":
            ficha.substituia_gerente_detalhes = None

        ficha.substituicao_colegas_tempo = texto_formulario(
            "substituicao_colegas_tempo",
        )

        if ficha.substituia_colegas_afastados != "SIM":
            ficha.substituicao_colegas_tempo = None

        ficha.descricao_rotina_trabalho = texto_formulario(
            "descricao_rotina_trabalho",
        )

        ficha.observacoes_contrato = texto_formulario(
            "observacoes_contrato",
        )

        ficha.etapa_atual = "contrato"
        ficha.etapa_contrato_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do contrato. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/contrato.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="contrato",
                    url_anterior=url_for(
                        "atendimentos.etapa_admissao",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_local_trabalho",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados do contrato salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_local_trabalho",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_contrato",
                atendimento_id=atendimento.id,
            )
        )

    contexto = contexto_etapa(
        atendimento=atendimento,
        ficha=ficha,
        etapa_atual="contrato",
        url_anterior=url_for(
            "atendimentos.etapa_admissao",
            atendimento_id=atendimento.id,
        ),
        url_proxima=url_for(
            "atendimentos.etapa_local_trabalho",
            atendimento_id=atendimento.id,
        ),
    )

    contexto["tipos_contrato"] = FichaTrabalhista.TIPOS_CONTRATO

    return render_template(
        "atendimentos/trabalhista/contrato.html",
        **contexto,
    )

# ============================================================
# ETAPA 6 — LOCAL DE TRABALHO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/local-trabalho",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_local_trabalho(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        campos_resposta = [
            "trabalhava_mesmo_local",
            "trabalhava_em_obras",
            "trabalhava_viajando",
            "dormia_fora_casa",
            "recebia_diarias",
            "recebia_hospedagem",
            "recebia_alimentacao",
            "usava_veiculo_proprio",
            "recebia_reembolso_veiculo",
            "utilizava_celular_particular",
            "recebia_ajuda_internet_telefone",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.locais_trabalho = texto_formulario(
            "locais_trabalho",
        )

        ficha.obras_locais = texto_formulario(
            "obras_locais",
        )

        ficha.locais_viagens = texto_formulario(
            "locais_viagens",
        )

        ficha.veiculo_proprio_descricao = texto_formulario(
            "veiculo_proprio_descricao",
        )

        ficha.observacoes_local_trabalho = texto_formulario(
            "observacoes_local_trabalho",
        )

        try:
            ficha.valor_diarias = decimal_formulario(
                "valor_diarias",
            )

            ficha.valor_reembolso_veiculo = decimal_formulario(
                "valor_reembolso_veiculo",
            )

            ficha.valor_ajuda_internet_telefone = decimal_formulario(
                "valor_ajuda_internet_telefone",
            )

        except ValueError:
            flash(
                "Informe valores monetários válidos. "
                "Exemplo: 150,00.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/local_trabalho.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="local",
                    url_anterior=url_for(
                        "atendimentos.etapa_contrato",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_salario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        if ficha.trabalhava_mesmo_local == "SIM":
            ficha.locais_trabalho = None

        if ficha.trabalhava_em_obras != "SIM":
            ficha.obras_locais = None

        if ficha.trabalhava_viajando != "SIM":
            ficha.locais_viagens = None
            ficha.dormia_fora_casa = None
            ficha.recebia_diarias = None
            ficha.valor_diarias = None
            ficha.recebia_hospedagem = None
            ficha.recebia_alimentacao = None

        elif ficha.recebia_diarias != "SIM":
            ficha.valor_diarias = None

        if ficha.usava_veiculo_proprio != "SIM":
            ficha.veiculo_proprio_descricao = None
            ficha.recebia_reembolso_veiculo = None
            ficha.valor_reembolso_veiculo = None

        elif ficha.recebia_reembolso_veiculo != "SIM":
            ficha.valor_reembolso_veiculo = None

        if ficha.utilizava_celular_particular != "SIM":
            ficha.recebia_ajuda_internet_telefone = None
            ficha.valor_ajuda_internet_telefone = None

        elif ficha.recebia_ajuda_internet_telefone != "SIM":
            ficha.valor_ajuda_internet_telefone = None

        ficha.etapa_atual = "local"
        ficha.etapa_local_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do local de trabalho. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/local_trabalho.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="local",
                    url_anterior=url_for(
                        "atendimentos.etapa_contrato",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_salario",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados do local de trabalho salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_salario",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_local_trabalho",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/local_trabalho.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="local",
            url_anterior=url_for(
                "atendimentos.etapa_contrato",
                atendimento_id=atendimento.id,
            ),
            url_proxima=url_for(
                "atendimentos.etapa_salario",
                atendimento_id=atendimento.id,
            ),
        ),
    )

# ============================================================
# ETAPA 7 — SALÁRIO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/salario",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_salario(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        try:
            ficha.salario_registrado = decimal_formulario(
                "salario_registrado",
            )

            ficha.salario_real = decimal_formulario(
                "salario_real",
            )

            ficha.valor_extrafolha_mensal = decimal_formulario(
                "valor_extrafolha_mensal",
            )

            ficha.valor_medio_gorjetas = decimal_formulario(
                "valor_medio_gorjetas",
            )

        except ValueError:
            flash(
                "Informe valores monetários válidos. "
                "Exemplo: 1.500,00.",
                "danger",
            )

            contexto = contexto_etapa(
                atendimento=atendimento,
                ficha=ficha,
                etapa_atual="salario",
                url_anterior=url_for(
                    "atendimentos.etapa_local_trabalho",
                    atendimento_id=atendimento.id,
                ),
                url_proxima=url_for(
                    "atendimentos.etapa_ferias",
                    atendimento_id=atendimento.id,
                ),
            )

            contexto["formas_pagamento_extrafolha"] = (
                FichaTrabalhista.FORMAS_PAGAMENTO_EXTRAFOLHA
            )

            return render_template(
                "atendimentos/trabalhista/salario.html",
                **contexto,
            )

        campos_resposta = [
            "recebia_valor_extrafolha",
            "recebia_gorjetas",
            "gorjetas_constavam_contracheque",
            "gorjetas_divididas_empregados",
            "pagamento_quinto_dia_util",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.responsavel_pagamento_extrafolha = texto_formulario(
            "responsavel_pagamento_extrafolha",
        )

        ficha.forma_pagamento_extrafolha = texto_formulario(
            "forma_pagamento_extrafolha",
        )

        if (
            ficha.forma_pagamento_extrafolha
            not in FichaTrabalhista.FORMAS_PAGAMENTO_EXTRAFOLHA
        ):
            ficha.forma_pagamento_extrafolha = None

        ficha.forma_pagamento_extrafolha_outro = texto_formulario(
            "forma_pagamento_extrafolha_outro",
        )

        ficha.forma_divisao_gorjetas = texto_formulario(
            "forma_divisao_gorjetas",
        )

        ficha.observacoes_salario = texto_formulario(
            "observacoes_salario",
        )

        if ficha.recebia_valor_extrafolha != "SIM":
            ficha.valor_extrafolha_mensal = None
            ficha.responsavel_pagamento_extrafolha = None
            ficha.forma_pagamento_extrafolha = None
            ficha.forma_pagamento_extrafolha_outro = None

        elif (
            ficha.forma_pagamento_extrafolha
            != FichaTrabalhista.PAGAMENTO_OUTRO
        ):
            ficha.forma_pagamento_extrafolha_outro = None

        if ficha.recebia_gorjetas != "SIM":
            ficha.valor_medio_gorjetas = None
            ficha.gorjetas_constavam_contracheque = None
            ficha.gorjetas_divididas_empregados = None
            ficha.forma_divisao_gorjetas = None

        elif ficha.gorjetas_divididas_empregados != "SIM":
            ficha.forma_divisao_gorjetas = None

        ficha.etapa_atual = "salario"
        ficha.etapa_salario_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados salariais. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            contexto = contexto_etapa(
                atendimento=atendimento,
                ficha=ficha,
                etapa_atual="salario",
                url_anterior=url_for(
                    "atendimentos.etapa_local_trabalho",
                    atendimento_id=atendimento.id,
                ),
                url_proxima=url_for(
                    "atendimentos.etapa_ferias",
                    atendimento_id=atendimento.id,
                ),
            )

            contexto["formas_pagamento_extrafolha"] = (
                FichaTrabalhista.FORMAS_PAGAMENTO_EXTRAFOLHA
            )

            return render_template(
                "atendimentos/trabalhista/salario.html",
                **contexto,
            )

        flash(
            "✅ Dados salariais salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_ferias",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_salario",
                atendimento_id=atendimento.id,
            )
        )

    contexto = contexto_etapa(
        atendimento=atendimento,
        ficha=ficha,
        etapa_atual="salario",
        url_anterior=url_for(
            "atendimentos.etapa_local_trabalho",
            atendimento_id=atendimento.id,
        ),
        url_proxima=url_for(
            "atendimentos.etapa_ferias",
            atendimento_id=atendimento.id,
        ),
    )

    contexto["formas_pagamento_extrafolha"] = (
        FichaTrabalhista.FORMAS_PAGAMENTO_EXTRAFOLHA
    )

    return render_template(
        "atendimentos/trabalhista/salario.html",
        **contexto,
    )

# ============================================================
# ETAPA 8 — FÉRIAS
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/ferias",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_ferias(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        campos_resposta = [
            "recebeu_ferias_todos_anos",
            "recebeu_um_terco_ferias",
            "vendia_ferias",
            "era_obrigado_vender_ferias",
            "trabalhou_durante_ferias",
            "assinava_ponto_durante_ferias",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.quantidade_periodos_ferias = inteiro_formulario(
            "quantidade_periodos_ferias",
        )

        ficha.datas_periodos_ferias = texto_formulario(
            "datas_periodos_ferias",
        )

        ficha.data_pagamento_ferias = texto_formulario(
            "data_pagamento_ferias",
        )

        ficha.momento_pagamento_ferias = texto_formulario(
            "momento_pagamento_ferias",
        )

        if (
            ficha.momento_pagamento_ferias
            not in FichaTrabalhista.MOMENTOS_PAGAMENTO_FERIAS
        ):
            ficha.momento_pagamento_ferias = None

        ficha.observacoes_ferias = texto_formulario(
            "observacoes_ferias",
        )

        if ficha.recebeu_ferias_todos_anos != "SIM":
            ficha.quantidade_periodos_ferias = None
            ficha.datas_periodos_ferias = None
            ficha.data_pagamento_ferias = None
            ficha.momento_pagamento_ferias = None
            ficha.recebeu_um_terco_ferias = None
            ficha.vendia_ferias = None
            ficha.era_obrigado_vender_ferias = None
            ficha.trabalhou_durante_ferias = None
            ficha.assinava_ponto_durante_ferias = None

        else:
            if ficha.vendia_ferias != "SIM":
                ficha.era_obrigado_vender_ferias = None

            if ficha.trabalhou_durante_ferias != "SIM":
                ficha.assinava_ponto_durante_ferias = None

        ficha.etapa_atual = "ferias"
        ficha.etapa_ferias_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados das férias. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            contexto = contexto_etapa(
                atendimento=atendimento,
                ficha=ficha,
                etapa_atual="ferias",
                url_anterior=url_for(
                    "atendimentos.etapa_salario",
                    atendimento_id=atendimento.id,
                ),
                url_proxima=url_for(
                    "atendimentos.etapa_decimo_terceiro",
                    atendimento_id=atendimento.id,
                ),
            )

            contexto["momentos_pagamento_ferias"] = (
                FichaTrabalhista.MOMENTOS_PAGAMENTO_FERIAS
            )

            return render_template(
                "atendimentos/trabalhista/ferias.html",
                **contexto,
            )

        flash(
            "✅ Dados das férias salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_decimo_terceiro",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_ferias",
                atendimento_id=atendimento.id,
            )
        )

    contexto = contexto_etapa(
        atendimento=atendimento,
        ficha=ficha,
        etapa_atual="ferias",
        url_anterior=url_for(
            "atendimentos.etapa_salario",
            atendimento_id=atendimento.id,
        ),
        url_proxima=url_for(
            "atendimentos.etapa_decimo_terceiro",
            atendimento_id=atendimento.id,
        ),
    )

    contexto["momentos_pagamento_ferias"] = (
        FichaTrabalhista.MOMENTOS_PAGAMENTO_FERIAS
    )

    return render_template(
        "atendimentos/trabalhista/ferias.html",
        **contexto,
    )

# ============================================================
# ETAPA 9 — 13º SALÁRIO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/decimo-terceiro",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_decimo_terceiro(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        campos_resposta = [
            "recebia_decimo_terceiro",
            "recebia_decimo_terceiro_corretamente",
            "recebia_decimo_terceiro_duas_parcelas",
            "possui_contracheque_decimo_terceiro",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        ficha.data_aproximada_primeira_parcela = texto_formulario(
            "data_aproximada_primeira_parcela",
        )

        ficha.data_aproximada_segunda_parcela = texto_formulario(
            "data_aproximada_segunda_parcela",
        )

        ficha.observacoes_decimo_terceiro = texto_formulario(
            "observacoes_decimo_terceiro",
        )

        if ficha.recebia_decimo_terceiro != "SIM":
            ficha.recebia_decimo_terceiro_corretamente = None
            ficha.recebia_decimo_terceiro_duas_parcelas = None
            ficha.data_aproximada_primeira_parcela = None
            ficha.data_aproximada_segunda_parcela = None
            ficha.possui_contracheque_decimo_terceiro = None

        elif ficha.recebia_decimo_terceiro_duas_parcelas != "SIM":
            ficha.data_aproximada_primeira_parcela = None
            ficha.data_aproximada_segunda_parcela = None

        ficha.etapa_atual = "decimo_terceiro"
        ficha.etapa_decimo_terceiro_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do 13º salário. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/decimo_terceiro.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="decimo_terceiro",
                    url_anterior=url_for(
                        "atendimentos.etapa_ferias",
                        atendimento_id=atendimento.id,
                    ),
                    url_proxima=url_for(
                        "atendimentos.etapa_rescisao",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Dados do 13º salário salvos com sucesso!",
            "success",
        )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_rescisao",
                    atendimento_id=atendimento.id,
                )
            )

        return redirect(
            url_for(
                "atendimentos.etapa_decimo_terceiro",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/decimo_terceiro.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="decimo_terceiro",
            url_anterior=url_for(
                "atendimentos.etapa_ferias",
                atendimento_id=atendimento.id,
            ),
            url_proxima=url_for(
                "atendimentos.etapa_rescisao",
                atendimento_id=atendimento.id,
            ),
        ),
    )

# ============================================================
# ETAPA 10 — RESCISÃO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/rescisao",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def etapa_rescisao(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    if request.method == "POST":
        campos_resposta = [
            "recebeu_extrato_fgts_rescisao",
            "recebeu_comprovante_multa_fgts",
            "multa_fgts_creditada",
            "recebeu_verbas_rescisorias",
            "assinou_termo_rescisao",
            "recebeu_copia_termo_rescisao",
            "recebeu_guias_seguro_desemprego",
            "realizou_exame_demissional",
        ]

        for campo in campos_resposta:
            valor = texto_formulario(
                campo,
            )

            if valor not in FichaTrabalhista.RESPOSTAS:
                valor = None

            setattr(
                ficha,
                campo,
                valor,
            )

        try:
            ficha.data_demissao = data_formulario(
                "data_demissao",
            )

            ficha.data_pagamento_rescisao = data_formulario(
                "data_pagamento_rescisao",
            )

        except ValueError:
            flash(
                "Informe datas válidas para a demissão e o pagamento.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/rescisao.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="rescisao",
                    url_anterior=url_for(
                        "atendimentos.etapa_decimo_terceiro",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        ficha.tipo_rescisao = texto_formulario(
            "tipo_rescisao",
        )

        ficha.observacoes_rescisao = texto_formulario(
            "observacoes_rescisao",
        )

        ficha.observacoes_gerais = texto_formulario(
            "observacoes_gerais",
        )

        ficha.documentos_pendentes = texto_formulario(
            "documentos_pendentes",
        )

        ficha.avaliacao_google_solicitada = (
            request.form.get(
                "avaliacao_google_solicitada",
            )
            == "1"
        )

        ficha.etapa_atual = "rescisao"
        ficha.etapa_rescisao_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados da rescisão. "
                "Verifique as informações e tente novamente.",
                "danger",
            )

            return render_template(
                "atendimentos/trabalhista/rescisao.html",
                **contexto_etapa(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="rescisao",
                    url_anterior=url_for(
                        "atendimentos.etapa_decimo_terceiro",
                        atendimento_id=atendimento.id,
                    ),
                ),
            )

        flash(
            "✅ Ficha trabalhista concluída com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.resumo_ficha_trabalhista",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/rescisao.html",
        **contexto_etapa(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="rescisao",
            url_anterior=url_for(
                "atendimentos.etapa_decimo_terceiro",
                atendimento_id=atendimento.id,
            ),
        ),
    )

# ============================================================
# RESUMO DA FICHA TRABALHISTA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/resumo",
    methods=[
        "GET",
    ],
)
@login_required
def resumo_ficha_trabalhista(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    return render_template(
        "atendimentos/trabalhista/resumo.html",
        atendimento=atendimento,
        ficha=ficha,
        etapas=montar_etapas_navegacao(
            ficha,
            atendimento.id,
        ),
        progresso=calcular_progresso(
            ficha,
        ),
        respostas=FichaTrabalhista.RESPOSTAS,
    )

    

# ============================================================
# ENTRADA E ETAPA 1 DA FICHA DE DIREITO DO CONSUMIDOR
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/consumidor",
    methods=["GET"],
)
@login_required
def ficha_consumidor(atendimento_id):
    return redirect(
        url_for(
            "atendimentos.etapa_atendimento_consumidor",
            atendimento_id=atendimento_id,
        )
    )


@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/consumidor/atendimento",
    methods=["GET", "POST"],
)
@login_required
def etapa_atendimento_consumidor(atendimento_id):
    atendimento = buscar_atendimento_consumidor(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha_consumidor(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_proxima = url_for(
        "atendimentos.etapa_consumidor_consumidor",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        titulo = texto_formulario(
            "titulo",
        )

        status = request.form.get(
            "status",
            Atendimento.STATUS_RASCUNHO,
        ).strip()

        if not titulo:
            flash(
                "Informe o título do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/atendimento.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_proxima,
                ),
            )

        if status not in Atendimento.STATUS:
            status = Atendimento.STATUS_RASCUNHO

        try:
            data_atendimento = data_formulario(
                "data_atendimento",
            )

            horario_atendimento = horario_formulario(
                "horario_atendimento",
            )

        except ValueError:
            flash(
                "Informe uma data e um horário válidos.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/atendimento.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_proxima,
                ),
            )

        if data_atendimento is None:
            flash(
                "Informe a data do atendimento.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/atendimento.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_proxima,
                ),
            )

        tipo_demanda = texto_formulario(
            "tipo_demanda",
        )

        if tipo_demanda not in FichaConsumidor.TIPOS_DEMANDA:
            tipo_demanda = None

        atendimento.titulo = titulo
        atendimento.status = status
        atendimento.data_atendimento = data_atendimento
        atendimento.horario_atendimento = horario_atendimento
        atendimento.resumo_caso = texto_formulario(
            "resumo_caso",
        )
        atendimento.observacoes_internas = texto_formulario(
            "observacoes_internas",
        )

        ficha.cliente_id = atendimento.cliente_id
        ficha.tipo_demanda = tipo_demanda
        ficha.outro_tipo_demanda = texto_formulario(
            "outro_tipo_demanda",
        )
        ficha.motivo_principal = texto_formulario(
            "motivo_principal",
        )
        ficha.existe_urgencia = (
            request.form.get("existe_urgencia") == "on"
        )
        ficha.descricao_urgencia = texto_formulario(
            "descricao_urgencia",
        )
        ficha.existe_processo_anterior = (
            request.form.get("existe_processo_anterior") == "on"
        )
        ficha.numero_processo_anterior = texto_formulario(
            "numero_processo_anterior",
        )
        ficha.vara_processo_anterior = texto_formulario(
            "vara_processo_anterior",
        )
        ficha.comarca_processo_anterior = texto_formulario(
            "comarca_processo_anterior",
        )
        ficha.observacoes_atendimento = texto_formulario(
            "observacoes_atendimento",
        )

        if ficha.tipo_demanda != "OUTRA":
            ficha.outro_tipo_demanda = None

        if not ficha.existe_urgencia:
            ficha.descricao_urgencia = None

        if not ficha.existe_processo_anterior:
            ficha.numero_processo_anterior = None
            ficha.vara_processo_anterior = None
            ficha.comarca_processo_anterior = None

        ficha.etapa_atual = "atendimento"
        ficha.etapa_atendimento_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar o atendimento de Direito do Consumidor.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/atendimento.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="atendimento",
                    url_proxima=url_proxima,
                ),
            )

        acao = request.form.get(
            "acao",
            "salvar",
        )

        if acao == "salvar_proxima":
            return redirect(
                url_for(
                    "atendimentos.etapa_consumidor_consumidor",
                    atendimento_id=atendimento.id,
                )
            )

        flash(
            "✅ Atendimento de Direito do Consumidor salvo com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_atendimento_consumidor",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/consumidor/atendimento.html",
        **contexto_etapa_consumidor(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="atendimento",
            url_proxima=url_proxima,
        ),
    )


# ============================================================
# ETAPA 2 — CONSUMIDOR
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/consumidor/consumidor",
    methods=["GET", "POST"],
)
@login_required
def etapa_consumidor_consumidor(atendimento_id):
    atendimento = buscar_atendimento_consumidor(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha_consumidor(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    url_anterior = url_for(
        "atendimentos.etapa_atendimento_consumidor",
        atendimento_id=atendimento.id,
    )

    if request.method == "POST":
        try:
            consumidor_renda_mensal = decimal_formulario(
                "consumidor_renda_mensal",
            )

        except ValueError:
            flash(
                "Informe uma renda mensal válida.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/consumidor.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="consumidor",
                    url_anterior=url_anterior,
                ),
            )

        ficha.consumidor_estado_civil = texto_formulario(
            "consumidor_estado_civil",
        )
        ficha.consumidor_profissao = texto_formulario(
            "consumidor_profissao",
        )
        ficha.consumidor_renda_mensal = consumidor_renda_mensal
        ficha.consumidor_escolaridade = texto_formulario(
            "consumidor_escolaridade",
        )
        ficha.consumidor_idoso = (
            request.form.get("consumidor_idoso") == "on"
        )
        ficha.consumidor_possui_deficiencia = (
            request.form.get(
                "consumidor_possui_deficiencia"
            ) == "on"
        )
        ficha.consumidor_descricao_deficiencia = texto_formulario(
            "consumidor_descricao_deficiencia",
        )
        ficha.consumidor_vulneravel = (
            request.form.get("consumidor_vulneravel") == "on"
        )
        ficha.consumidor_descricao_vulnerabilidade = texto_formulario(
            "consumidor_descricao_vulnerabilidade",
        )
        ficha.consumidor_dependentes = texto_formulario(
            "consumidor_dependentes",
        )
        ficha.observacoes_consumidor = texto_formulario(
            "observacoes_consumidor",
        )

        if not ficha.consumidor_possui_deficiencia:
            ficha.consumidor_descricao_deficiencia = None

        if not ficha.consumidor_vulneravel:
            ficha.consumidor_descricao_vulnerabilidade = None

        ficha.etapa_atual = "consumidor"
        ficha.etapa_consumidor_concluida = True

        salvar_auditoria(
            atendimento,
            ficha,
        )

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Não foi possível salvar os dados do consumidor.",
                "danger",
            )

            return render_template(
                "atendimentos/consumidor/consumidor.html",
                **contexto_etapa_consumidor(
                    atendimento=atendimento,
                    ficha=ficha,
                    etapa_atual="consumidor",
                    url_anterior=url_anterior,
                ),
            )

        flash(
            "✅ Dados do consumidor salvos com sucesso!",
            "success",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_consumidor_consumidor",
                atendimento_id=atendimento.id,
            )
        )

    return render_template(
        "atendimentos/consumidor/consumidor.html",
        **contexto_etapa_consumidor(
            atendimento=atendimento,
            ficha=ficha,
            etapa_atual="consumidor",
            url_anterior=url_anterior,
        ),
    )


# ============================================================
# GERAÇÃO DE PDF — FICHA TRABALHISTA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/trabalhista/pdf",
    methods=["GET"],
)
@login_required
def gerar_pdf_trabalhista(atendimento_id):
    atendimento = buscar_atendimento_trabalhista(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    try:
        arquivo_pdf = gerar_pdf_ficha_trabalhista(
            atendimento=atendimento,
            ficha=ficha,
        )

        return send_file(
            arquivo_pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nome_pdf_trabalhista(
                atendimento,
            ),
            max_age=0,
        )

    except Exception:
        flash(
            "Não foi possível gerar o PDF da ficha trabalhista. "
            "Verifique os dados e tente novamente.",
            "danger",
        )

        return redirect(
            url_for(
                "atendimentos.resumo_ficha_trabalhista",
                atendimento_id=atendimento.id,
            )
        )


# ============================================================
# GERAÇÃO DE PDF — FICHA PREVIDENCIÁRIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/previdenciaria/pdf",
    methods=["GET"],
)
@login_required
def gerar_pdf_previdenciario(atendimento_id):
    atendimento = buscar_atendimento_previdenciario(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha_previdenciaria(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    try:
        arquivo_pdf = gerar_pdf_ficha_previdenciaria(
            atendimento=atendimento,
            ficha=ficha,
        )

        return send_file(
            arquivo_pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nome_pdf_previdenciario(
                atendimento,
            ),
            max_age=0,
        )

    except Exception:
        flash(
            "Não foi possível gerar o PDF da ficha previdenciária. "
            "Verifique os dados e tente novamente.",
            "danger",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_resumo_previdenciario",
                atendimento_id=atendimento.id,
            )
        )

# ============================================================
# GERAÇÃO DE PDF — FICHA CÍVEL
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/civel/pdf",
    methods=["GET"],
)
@login_required
def gerar_pdf_civel(atendimento_id):
    atendimento = buscar_atendimento_civel(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha_civel(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    try:
        arquivo_pdf = gerar_pdf_ficha_civel(
            atendimento=atendimento,
            ficha=ficha,
        )

        return send_file(
            arquivo_pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nome_pdf_civel(
                atendimento,
            ),
            max_age=0,
        )

    except Exception:
        flash(
            "Não foi possível gerar o PDF da Ficha Cível. "
            "Verifique os dados e tente novamente.",
            "danger",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_analise_civel",
                atendimento_id=atendimento.id,
            )
        )

# ============================================================
# GERAÇÃO DE PDF — FICHA DE DIREITO DE FAMÍLIA
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/familia/pdf",
    methods=["GET"],
)
@login_required
def gerar_pdf_familia(atendimento_id):
    atendimento = buscar_atendimento_familia(
        atendimento_id,
    )

    if atendimento is None:
        return redirect(
            url_for(
                "clientes.listar_clientes",
            )
        )

    ficha = obter_ou_criar_ficha_familia(
        atendimento,
    )

    if ficha is None:
        return redirect(
            url_for(
                "clientes.detalhes_cliente",
                id=atendimento.cliente_id,
            )
        )

    try:
        arquivo_pdf = gerar_pdf_ficha_familia(
            atendimento=atendimento,
            ficha=ficha,
        )

        return send_file(
            arquivo_pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nome_pdf_familia(
                atendimento,
            ),
            max_age=0,
        )

    except Exception:
        flash(
            "Não foi possível gerar o PDF da Ficha de Direito de Família. "
            "Verifique os dados e tente novamente.",
            "danger",
        )

        return redirect(
            url_for(
                "atendimentos.etapa_analise_familia",
                atendimento_id=atendimento.id,
            )
        )

# ============================================================
# EXCLUIR ATENDIMENTO
# ============================================================

@atendimento_bp.route(
    "/atendimentos/<int:atendimento_id>/excluir",
    methods=["POST"],
)
@login_required
def excluir_atendimento(atendimento_id):

    atendimento = Atendimento.query.get_or_404(
        atendimento_id
    )

    try:

        # ----------------------------------------------------
        # EXCLUIR A FICHA RELACIONADA
        # ----------------------------------------------------

        if atendimento.area == Atendimento.AREA_TRABALHISTA:

            ficha = atendimento.ficha_trabalhista

            if ficha is not None:

                db.session.delete(
                    ficha
                )


        elif atendimento.area == Atendimento.AREA_PREVIDENCIARIA:

            ficha = atendimento.ficha_previdenciaria

            if ficha is not None:

                db.session.delete(
                    ficha
                )


        elif atendimento.area == Atendimento.AREA_CIVEL:

            ficha = atendimento.ficha_civel

            if ficha is not None:

                db.session.delete(
                    ficha
                )


        elif atendimento.area == Atendimento.AREA_FAMILIA:

            ficha = atendimento.ficha_familia

            if ficha is not None:

                db.session.delete(
                    ficha
                )


        elif atendimento.area == Atendimento.AREA_CONSUMIDOR:

            ficha = atendimento.ficha_consumidor

            if ficha is not None:

                db.session.delete(
                    ficha
                )


        # ----------------------------------------------------
        # EXCLUIR O ATENDIMENTO
        # ----------------------------------------------------

        db.session.delete(
            atendimento
        )

        db.session.commit()


        flash(
            "Atendimento excluído com sucesso.",
            "success"
        )


    except Exception as erro:

        db.session.rollback()

        print(
            "ERRO AO EXCLUIR ATENDIMENTO:",
            erro
        )

        flash(
            "Não foi possível excluir o atendimento.",
            "danger"
        )


    return redirect(
        request.referrer
        or url_for(
            "dashboard.dashboard"
        )
    )