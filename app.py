import os
import sqlite3
import unicodedata

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    LoginManager,
    current_user,
    logout_user
)

from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from models import db

from models.agenda import EventoAgenda
from models.atendimento import Atendimento
from models.cliente import Cliente
from models.configuracao import ConfiguracaoEscritorio
from models.configuracao_arquivos import ConfiguracaoArquivos
from models.configuracao_financeiro import ConfiguracaoFinanceiro
from models.documento import Documento
from models.financeiro import LancamentoFinanceiro
from models.ficha_trabalhista import FichaTrabalhista
from models.processo import Processo
from models.usuario import Usuario
from models.ficha_civel import FichaCivel
from models.ficha_familia import FichaFamilia
from models.ficha_consumidor import FichaConsumidor
from models.documento_modelo import DocumentoModelo
from models.documento_gerado import DocumentoGerado

from routes.gerador_documentos_routes import (
    gerador_documentos_bp
)
from routes.agenda_routes import agenda_bp
from routes.atendimento_routes import atendimento_bp
from routes.auth_routes import auth_bp
from routes.cliente_routes import cliente_bp
from routes.configuracao_arquivos_routes import (
    configuracao_arquivos_bp
)
from routes.configuracao_financeiro_routes import (
    configuracao_financeiro_bp
)
from routes.configuracao_preferencias_routes import (
    preferencias_bp
)
from routes.configuracao_routes import configuracao_bp
from routes.dashboard_routes import dashboard_bp
from routes.documento_routes import documento_bp
from routes.financeiro_routes import financeiro_bp
from routes.notificacao_routes import notificacao_bp
from routes.pesquisa_routes import pesquisa_bp
from routes.processo_routes import processo_bp
from routes.usuario_routes import usuario_bp

from services.notificacoes import obter_resumo_notificacoes


# =====================================
# CRIAÇÃO DA APLICAÇÃO
# =====================================
app = Flask(
    __name__
)

app.config.from_object(
    Config
)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    app.config.get(
        "SECRET_KEY",
        "sistema_juridico_2026"
    )
)


# =====================================
# BANCO DE DADOS
# =====================================
db.init_app(
    app
)


# =====================================
# NORMALIZAÇÃO DA PESQUISA
# =====================================
def remover_acentos(valor):
    """
    Remove acentos e transforma o texto
    em letras minúsculas para pesquisas.

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


def registrar_funcoes_sqlite(
    conexao_banco,
    registro_conexao
):
    """
    Registra a função sem_acentos no SQLite.
    """

    if isinstance(
        conexao_banco,
        sqlite3.Connection
    ):
        conexao_banco.create_function(
            "sem_acentos",
            1,
            remover_acentos
        )


# =====================================
# FLASK-LOGIN
# =====================================
login_manager = LoginManager()

login_manager.init_app(
    app
)

login_manager.login_view = (
    "auth.login"
)

login_manager.login_message = (
    "Faça login para acessar o sistema."
)

login_manager.login_message_category = (
    "warning"
)


@login_manager.user_loader
def carregar_usuario(usuario_id):
    try:
        return db.session.get(
            Usuario,
            int(
                usuario_id
            )
        )

    except (
        TypeError,
        ValueError
    ):
        return None


# =====================================
# BLUEPRINTS
# =====================================
app.register_blueprint(
    dashboard_bp
)

app.register_blueprint(
    cliente_bp
)

app.register_blueprint(
    atendimento_bp
)

app.register_blueprint(
    processo_bp
)

app.register_blueprint(
    documento_bp
)

app.register_blueprint(
    agenda_bp
)

app.register_blueprint(
    financeiro_bp
)

app.register_blueprint(
    configuracao_bp
)

app.register_blueprint(
    preferencias_bp
)

app.register_blueprint(
    configuracao_financeiro_bp
)

app.register_blueprint(
    configuracao_arquivos_bp
)

app.register_blueprint(
    auth_bp
)

app.register_blueprint(
    usuario_bp
)

app.register_blueprint(
    pesquisa_bp
)

app.register_blueprint(
    notificacao_bp
)

app.register_blueprint(
    gerador_documentos_bp
)


# =====================================
# ADMINISTRADOR INICIAL
# =====================================
def criar_administrador_inicial():
    """
    Cria o primeiro administrador apenas quando
    ainda não existe nenhum usuário no banco.

    Depois que o primeiro usuário for criado,
    o sistema nunca criará outro administrador
    automaticamente.
    """

    quantidade_usuarios = (
        Usuario.query.count()
    )

    if quantidade_usuarios > 0:
        return

    email_admin = os.environ.get(
        "ADMIN_EMAIL",
        "admin@escritorio.com"
    ).strip().lower()

    senha_admin = os.environ.get(
        "ADMIN_SENHA",
        "admin123"
    )

    nome_admin = os.environ.get(
        "ADMIN_NOME",
        "Administrador do Sistema"
    ).strip() or "Administrador do Sistema"

    administrador = Usuario(
        nome=nome_admin,
        email=email_admin,
        telefone="",
        cargo="Administrador do Sistema",
        perfil=Usuario.PERFIL_ADMIN,
        ativo=True
    )

    administrador.definir_senha(
        senha_admin
    )

    try:
        db.session.add(
            administrador
        )

        db.session.commit()

        print(
            "========================================"
        )

        print(
            "Administrador inicial criado com sucesso."
        )

        print(
            f"Nome: {nome_admin}"
        )

        print(
            f"E-mail: {email_admin}"
        )

        print(
            "Altere a senha após o primeiro acesso."
        )

        print(
            "========================================"
        )

    except SQLAlchemyError as erro:
        db.session.rollback()

        print(
            "Não foi possível criar o "
            "administrador inicial."
        )

        print(
            f"Erro: {erro}"
        )


# =====================================
# INICIALIZAÇÃO DO BANCO
# =====================================
with app.app_context():
    if not event.contains(
        db.engine,
        "connect",
        registrar_funcoes_sqlite
    ):
        event.listen(
            db.engine,
            "connect",
            registrar_funcoes_sqlite
        )

    db.create_all()

    criar_administrador_inicial()


# =====================================
# PROTEÇÃO DE USUÁRIO DESATIVADO
# =====================================
@app.before_request
def verificar_usuario_ativo():
    rotas_liberadas = {
        "auth.login",
        "auth.logout",
        "static"
    }

    if request.endpoint in rotas_liberadas:
        return None

    if (
        current_user.is_authenticated
        and not current_user.ativo
    ):
        logout_user()

        flash(
            "Seu usuário foi desativado. "
            "Entre em contato com o administrador.",
            "warning"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )

    return None


# =====================================
# DADOS GLOBAIS DOS TEMPLATES
# =====================================
@app.context_processor
def carregar_dados_globais():
    configuracao = (
        ConfiguracaoEscritorio.query
        .order_by(
            ConfiguracaoEscritorio.id.asc()
        )
        .first()
    )

    resumo_notificacoes = {
        "notificacoes": [],
        "total": 0,
        "alta": 0,
        "media": 0,
        "baixa": 0
    }

    if current_user.is_authenticated:
        resumo_notificacoes = (
            obter_resumo_notificacoes()
        )

    return {
        "configuracao_global": configuracao,
        "notificacoes_globais": resumo_notificacoes
    }


# =====================================
# ERRO 403
# =====================================
@app.errorhandler(
    403
)
def erro_403(erro):
    return (
        render_template(
            "errors/403.html"
        ),
        403
    )


# =====================================
# EXECUÇÃO
# =====================================
if __name__ == "__main__":
    print(
        "Execute o sistema utilizando o arquivo servidor.py"
    )