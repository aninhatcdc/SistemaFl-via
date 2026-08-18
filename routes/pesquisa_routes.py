import unicodedata

from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import (
    current_user,
    login_required
)

from models import db
from models.agenda import EventoAgenda
from models.cliente import Cliente
from models.documento import Documento
from models.financeiro import LancamentoFinanceiro
from models.processo import Processo


pesquisa_bp = Blueprint(
    "pesquisa",
    __name__,
    url_prefix="/pesquisa"
)


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def normalizar_termo(valor):
    """
    Remove acentos e transforma o texto
    em letras minúsculas.

    Exemplo:
    Ana Flávia -> ana flavia
    """

    if valor is None:
        return ""

    texto_normalizado = unicodedata.normalize(
        "NFKD",
        str(valor)
    )

    texto_sem_acentos = "".join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(
            caractere
        )
    )

    return texto_sem_acentos.lower()


def contem_sem_acentos(
    campo,
    termo_like
):
    """
    Cria uma condição de pesquisa que
    ignora acentos e diferenças entre
    maiúsculas e minúsculas.
    """

    return db.func.sem_acentos(
        db.func.coalesce(
            campo,
            ""
        )
    ).like(
        termo_like
    )


# =====================================
# PESQUISA GLOBAL
# =====================================
@pesquisa_bp.route("/")
@login_required
def pesquisa_global():
    termo = request.args.get(
        "q",
        ""
    ).strip()

    clientes = []
    processos = []
    documentos = []
    eventos = []
    financeiro = []

    termo_minimo = 2

    if (
        termo
        and len(termo) >= termo_minimo
    ):
        termo_normalizado = normalizar_termo(
            termo
        )

        termo_like = (
            f"%{termo_normalizado}%"
        )

        # =====================================
        # CLIENTES
        # =====================================
        clientes = (
            Cliente.query
            .filter(
                db.or_(
                    contem_sem_acentos(
                        Cliente.nome,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.cpf,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.rg,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.telefone,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.whatsapp,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.email,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.area_juridica,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.responsavel,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.observacoes,
                        termo_like
                    )
                )
            )
            .order_by(
                Cliente.nome.asc()
            )
            .limit(
                20
            )
            .all()
        )

        # =====================================
        # PROCESSOS
        # =====================================
        processos = (
            Processo.query
            .outerjoin(
                Cliente,
                Processo.cliente_id
                == Cliente.id
            )
            .filter(
                db.or_(
                    contem_sem_acentos(
                        Processo.numero,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.area,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.tribunal,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.comarca,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.vara,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.situacao,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.advogado,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.observacoes,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.nome,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.cpf,
                        termo_like
                    )
                )
            )
            .order_by(
                Processo.criado_em.desc()
            )
            .limit(
                20
            )
            .all()
        )

        # =====================================
        # DOCUMENTOS
        # =====================================
        documentos = (
            Documento.query
            .outerjoin(
                Cliente,
                Documento.cliente_id
                == Cliente.id
            )
            .filter(
                db.or_(
                    contem_sem_acentos(
                        Documento.nome_arquivo,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Documento.tipo,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Documento.descricao,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.nome,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.cpf,
                        termo_like
                    )
                )
            )
            .order_by(
                Documento.criado_em.desc()
            )
            .limit(
                20
            )
            .all()
        )

        # =====================================
        # AGENDA
        # =====================================
        eventos = (
            EventoAgenda.query
            .outerjoin(
                Cliente,
                EventoAgenda.cliente_id
                == Cliente.id
            )
            .outerjoin(
                Processo,
                EventoAgenda.processo_id
                == Processo.id
            )
            .filter(
                db.or_(
                    contem_sem_acentos(
                        EventoAgenda.titulo,
                        termo_like
                    ),
                    contem_sem_acentos(
                        EventoAgenda.tipo,
                        termo_like
                    ),
                    contem_sem_acentos(
                        EventoAgenda.descricao,
                        termo_like
                    ),
                    contem_sem_acentos(
                        EventoAgenda.local,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.nome,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Cliente.cpf,
                        termo_like
                    ),
                    contem_sem_acentos(
                        Processo.numero,
                        termo_like
                    )
                )
            )
            .order_by(
                EventoAgenda.data.desc(),
                EventoAgenda.horario.desc()
            )
            .limit(
                20
            )
            .all()
        )

        # =====================================
        # FINANCEIRO
        # =====================================
        if current_user.pode_acessar_financeiro:
            financeiro = (
                LancamentoFinanceiro.query
                .outerjoin(
                    Cliente,
                    LancamentoFinanceiro.cliente_id
                    == Cliente.id
                )
                .outerjoin(
                    Processo,
                    LancamentoFinanceiro.processo_id
                    == Processo.id
                )
                .filter(
                    db.or_(
                        contem_sem_acentos(
                            LancamentoFinanceiro.tipo,
                            termo_like
                        ),
                        contem_sem_acentos(
                            LancamentoFinanceiro.descricao,
                            termo_like
                        ),
                        contem_sem_acentos(
                            LancamentoFinanceiro.categoria,
                            termo_like
                        ),
                        contem_sem_acentos(
                            LancamentoFinanceiro.status,
                            termo_like
                        ),
                        contem_sem_acentos(
                            LancamentoFinanceiro.forma_pagamento,
                            termo_like
                        ),
                        contem_sem_acentos(
                            LancamentoFinanceiro.observacoes,
                            termo_like
                        ),
                        contem_sem_acentos(
                            Cliente.nome,
                            termo_like
                        ),
                        contem_sem_acentos(
                            Cliente.cpf,
                            termo_like
                        ),
                        contem_sem_acentos(
                            Processo.numero,
                            termo_like
                        )
                    )
                )
                .order_by(
                    LancamentoFinanceiro.competencia_ano.desc(),
                    LancamentoFinanceiro.competencia_mes.desc()
                )
                .limit(
                    20
                )
                .all()
            )

    total_resultados = (
        len(
            clientes
        )
        + len(
            processos
        )
        + len(
            documentos
        )
        + len(
            eventos
        )
        + len(
            financeiro
        )
    )

    return render_template(
        "pesquisa/resultados.html",
        termo=termo,
        termo_minimo=termo_minimo,
        clientes=clientes,
        processos=processos,
        documentos=documentos,
        eventos=eventos,
        financeiro=financeiro,
        total_resultados=total_resultados
    )