from datetime import datetime

from models import db


class ConfiguracaoEscritorio(db.Model):
    __tablename__ = "configuracoes_escritorio"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # DADOS GERAIS
    # ==========================
    nome_escritorio = db.Column(
        db.String(150),
        nullable=False,
        default="Sistema Jurídico"
    )

    nome_fantasia = db.Column(
        db.String(150)
    )

    cnpj = db.Column(
        db.String(20)
    )

    oab = db.Column(
        db.String(50)
    )

    telefone = db.Column(
        db.String(20)
    )

    whatsapp = db.Column(
        db.String(20)
    )

    email = db.Column(
        db.String(120)
    )

    site = db.Column(
        db.String(150)
    )

    # ==========================
    # ENDEREÇO
    # ==========================
    cep = db.Column(
        db.String(10)
    )

    rua = db.Column(
        db.String(150)
    )

    numero = db.Column(
        db.String(20)
    )

    complemento = db.Column(
        db.String(100)
    )

    bairro = db.Column(
        db.String(100)
    )

    cidade = db.Column(
        db.String(100)
    )

    estado = db.Column(
        db.String(2)
    )

    # ==========================
    # IDENTIDADE VISUAL
    # ==========================
    logo = db.Column(
        db.String(255)
    )

    cor_principal = db.Column(
        db.String(20),
        nullable=False,
        default="#212529"
    )

    cor_secundaria = db.Column(
        db.String(20),
        nullable=False,
        default="#0d6efd"
    )

    # ==========================
    # PREFERÊNCIAS DO SISTEMA
    # ==========================
    itens_por_pagina = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    dias_notificacoes = db.Column(
        db.Integer,
        nullable=False,
        default=7
    )

    exibir_notificacoes_baixa = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    modo_compacto_tabelas = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    pagina_inicial = db.Column(
        db.String(50),
        nullable=False,
        default="dashboard"
    )

    formato_data = db.Column(
        db.String(20),
        nullable=False,
        default="DD/MM/AAAA"
    )

    # ==========================
    # RODAPÉ E DOCUMENTOS
    # ==========================
    texto_rodape = db.Column(
        db.Text
    )

    # ==========================
    # CONTROLE
    # ==========================
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

    # ==========================
    # PROPRIEDADES
    # ==========================
    @property
    def classe_tabela(self):
        if self.modo_compacto_tabelas:
            return "table-sm"

        return ""

    @property
    def formato_data_python(self):
        formatos = {
            "DD/MM/AAAA": "%d/%m/%Y",
            "AAAA-MM-DD": "%Y-%m-%d",
            "MM/DD/AAAA": "%m/%d/%Y"
        }

        return formatos.get(
            self.formato_data,
            "%d/%m/%Y"
        )

    def __repr__(self):
        return (
            f"<ConfiguracaoEscritorio "
            f"id={self.id} "
            f"nome='{self.nome_escritorio}'>"
        )