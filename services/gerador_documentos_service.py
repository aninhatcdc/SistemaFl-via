import os
import re
import unicodedata

from datetime import date, datetime
from decimal import Decimal

from docxtpl import DocxTemplate


# =====================================
# FORMATAÇÃO DE TEXTOS
# =====================================
def texto_seguro(valor, padrao=""):
    """
    Converte valores para texto sem retornar None.
    """

    if valor is None:
        return padrao

    return str(valor).strip()


def formatar_data(valor):
    """
    Converte datas para o formato brasileiro.

    Exemplo:
    29/07/2026
    """

    if not valor:
        return ""

    if isinstance(valor, datetime):
        valor = valor.date()

    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    return texto_seguro(valor)


def formatar_moeda(valor):
    """
    Converte números para moeda brasileira.

    Exemplo:
    R$ 1.250,00
    """

    if valor in (None, ""):
        return ""

    try:
        numero = Decimal(str(valor))

        valor_formatado = (
            f"{numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {valor_formatado}"

    except (
        ValueError,
        TypeError,
        ArithmeticError
    ):
        return texto_seguro(valor)


# =====================================
# FORMATAÇÃO DE DOCUMENTOS
# =====================================
def formatar_cpf(cpf):
    """
    Retorna o CPF informado.

    A função não altera o valor porque o cadastro
    do cliente já pode possuir a pontuação correta.
    """

    return texto_seguro(cpf)


def montar_endereco_cliente(cliente):
    """
    Monta o endereço completo do cliente usando
    apenas os campos que estiverem preenchidos.
    """

    if not cliente:
        return ""

    primeira_parte = []

    if cliente.rua:
        primeira_parte.append(
            texto_seguro(cliente.rua)
        )

    if cliente.numero:
        primeira_parte.append(
            texto_seguro(cliente.numero)
        )

    endereco = ", ".join(
        primeira_parte
    )

    if cliente.complemento:
        if endereco:
            endereco += ", "

        endereco += texto_seguro(
            cliente.complemento
        )

    partes_finais = []

    if cliente.bairro:
        partes_finais.append(
            texto_seguro(cliente.bairro)
        )

    cidade_estado = ""

    if cliente.cidade:
        cidade_estado = texto_seguro(
            cliente.cidade
        )

    if cliente.estado:
        if cidade_estado:
            cidade_estado += "/"

        cidade_estado += texto_seguro(
            cliente.estado
        ).upper()

    if cidade_estado:
        partes_finais.append(
            cidade_estado
        )

    if cliente.cep:
        partes_finais.append(
            f"CEP {texto_seguro(cliente.cep)}"
        )

    if partes_finais:
        complemento_endereco = " - ".join(
            partes_finais
        )

        if endereco:
            endereco += " - "

        endereco += complemento_endereco

    return endereco


def montar_qualificacao_cliente(cliente):
    """
    Monta uma qualificação simples do cliente.

    Esse texto poderá ser usado em documentos
    que necessitem da qualificação completa.
    """

    if not cliente:
        return ""

    partes = []

    if cliente.nome:
        partes.append(
            texto_seguro(cliente.nome)
        )

    if cliente.estado_civil:
        partes.append(
            texto_seguro(cliente.estado_civil)
        )

    if cliente.profissao:
        partes.append(
            texto_seguro(cliente.profissao)
        )

    if cliente.rg:
        partes.append(
            f"portador(a) do RG nº "
            f"{texto_seguro(cliente.rg)}"
        )

    if cliente.cpf:
        partes.append(
            f"inscrito(a) no CPF sob o nº "
            f"{formatar_cpf(cliente.cpf)}"
        )

    endereco = montar_endereco_cliente(
        cliente
    )

    if endereco:
        partes.append(
            f"residente e domiciliado(a) em "
            f"{endereco}"
        )

    return ", ".join(partes)


# =====================================
# NOMES DE ARQUIVOS
# =====================================
def remover_acentos(texto):
    if not texto:
        return ""

    texto_normalizado = unicodedata.normalize(
        "NFKD",
        str(texto)
    )

    return "".join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(
            caractere
        )
    )


def nome_arquivo_seguro(texto):
    """
    Remove caracteres inválidos para nomes
    de arquivos do Windows.
    """

    texto = remover_acentos(
        texto_seguro(texto)
    )

    texto = re.sub(
        r'[<>:"/\\|?*]',
        "",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto or "Documento"


# =====================================
# CONTEXTO DO DOCUMENTO
# =====================================
def montar_contexto_documento(
    cliente,
    processo=None,
    usuario=None,
    configuracao=None,
    dados_extras=None
):
    """
    Monta todas as variáveis disponíveis para
    preenchimento dos modelos do Word.
    """

    contexto_cliente = {
        "id": cliente.id if cliente else "",
        "nome": texto_seguro(
            cliente.nome if cliente else ""
        ),
        "cpf": formatar_cpf(
            cliente.cpf if cliente else ""
        ),
        "rg": texto_seguro(
            cliente.rg if cliente else ""
        ),
        "data_nascimento": formatar_data(
            cliente.data_nascimento
            if cliente
            else None
        ),
        "estado_civil": texto_seguro(
            cliente.estado_civil
            if cliente
            else ""
        ),
        "profissao": texto_seguro(
            cliente.profissao
            if cliente
            else ""
        ),
        "telefone": texto_seguro(
            cliente.telefone
            if cliente
            else ""
        ),
        "whatsapp": texto_seguro(
            cliente.whatsapp
            if cliente
            else ""
        ),
        "email": texto_seguro(
            cliente.email
            if cliente
            else ""
        ),
        "cep": texto_seguro(
            cliente.cep
            if cliente
            else ""
        ),
        "rua": texto_seguro(
            cliente.rua
            if cliente
            else ""
        ),
        "numero": texto_seguro(
            cliente.numero
            if cliente
            else ""
        ),
        "complemento": texto_seguro(
            cliente.complemento
            if cliente
            else ""
        ),
        "bairro": texto_seguro(
            cliente.bairro
            if cliente
            else ""
        ),
        "cidade": texto_seguro(
            cliente.cidade
            if cliente
            else ""
        ),
        "estado": texto_seguro(
            cliente.estado
            if cliente
            else ""
        ).upper(),
        "endereco_completo": (
            montar_endereco_cliente(
                cliente
            )
        ),
        "qualificacao_completa": (
            montar_qualificacao_cliente(
                cliente
            )
        ),
        "area_juridica": texto_seguro(
            cliente.area_juridica
            if cliente
            else ""
        ),
        "origem_cliente": texto_seguro(
            cliente.origem_cliente
            if cliente
            else ""
        ),
        "responsavel": texto_seguro(
            cliente.responsavel
            if cliente
            else ""
        )
    }

    contexto_processo = {
        "id": (
            processo.id
            if processo
            else ""
        ),
        "numero": texto_seguro(
            processo.numero
            if processo
            else ""
        ),
        "area": texto_seguro(
            processo.area
            if processo
            else ""
        ),
        "tribunal": texto_seguro(
            processo.tribunal
            if processo
            else ""
        ),
        "comarca": texto_seguro(
            processo.comarca
            if processo
            else ""
        ),
        "vara": texto_seguro(
            processo.vara
            if processo
            else ""
        ),
        "situacao": texto_seguro(
            processo.situacao
            if processo
            else ""
        ),
        "data_entrada": formatar_data(
            processo.data_entrada
            if processo
            else None
        ),
        "proximo_prazo": formatar_data(
            processo.proximo_prazo
            if processo
            else None
        ),
        "advogado": texto_seguro(
            processo.advogado
            if processo
            else ""
        ),
        "observacoes": texto_seguro(
            processo.observacoes
            if processo
            else ""
        )
    }

    contexto_usuario = {
        "id": (
            usuario.id
            if usuario
            else ""
        ),
        "nome": texto_seguro(
            usuario.nome
            if usuario
            else ""
        ),
        "email": texto_seguro(
            usuario.email
            if usuario
            else ""
        ),
        "telefone": texto_seguro(
            usuario.telefone
            if usuario
            else ""
        ),
        "cargo": texto_seguro(
            usuario.cargo
            if usuario
            else ""
        )
    }

    contexto_escritorio = {
        "nome": texto_seguro(
            getattr(
                configuracao,
                "nome_escritorio",
                ""
            )
            if configuracao
            else ""
        ),
        "oab": texto_seguro(
            getattr(
                configuracao,
                "oab",
                ""
            )
            if configuracao
            else ""
        ),
        "telefone": texto_seguro(
            getattr(
                configuracao,
                "telefone",
                ""
            )
            if configuracao
            else ""
        ),
        "email": texto_seguro(
            getattr(
                configuracao,
                "email",
                ""
            )
            if configuracao
            else ""
        ),
        "endereco": texto_seguro(
            getattr(
                configuracao,
                "endereco",
                ""
            )
            if configuracao
            else ""
        )
    }

    hoje = date.today()

    contexto = {
        "cliente": contexto_cliente,
        "processo": contexto_processo,
        "usuario": contexto_usuario,
        "escritorio": contexto_escritorio,
        "data_atual": formatar_data(
            hoje
        ),
        "dia_atual": hoje.strftime("%d"),
        "mes_atual": hoje.strftime("%m"),
        "ano_atual": hoje.strftime("%Y")
    }

    if dados_extras:
        contexto.update(
            dados_extras
        )

    return contexto


# =====================================
# GERAÇÃO DO DOCX
# =====================================
def gerar_documento_docx(
    caminho_modelo,
    caminho_destino,
    contexto
):
    """
    Gera um novo documento DOCX a partir
    do modelo oficial do escritório.
    """

    if not caminho_modelo:
        raise ValueError(
            "O caminho do modelo não foi informado."
        )

    if not os.path.isfile(
        caminho_modelo
    ):
        raise FileNotFoundError(
            "O arquivo do modelo não foi encontrado: "
            f"{caminho_modelo}"
        )

    if not caminho_modelo.lower().endswith(
        ".docx"
    ):
        raise ValueError(
            "Neste momento, somente modelos DOCX "
            "podem ser preenchidos automaticamente."
        )

    pasta_destino = os.path.dirname(
        caminho_destino
    )

    if pasta_destino:
        os.makedirs(
            pasta_destino,
            exist_ok=True
        )

    documento = DocxTemplate(
        caminho_modelo
    )

    documento.render(
        contexto,
        autoescape=True
    )

    documento.save(
        caminho_destino
    )

    return caminho_destino