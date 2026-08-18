from datetime import datetime

from models import db


class ConfiguracaoFinanceiro(db.Model):
    __tablename__ = "configuracoes_financeiro"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # PADRÕES DOS LANÇAMENTOS
    # ==========================
    categoria_padrao = db.Column(
        db.String(100),
        nullable=False,
        default="Outros"
    )

    forma_pagamento_padrao = db.Column(
        db.String(50),
        nullable=False,
        default="Pix"
    )

    status_padrao = db.Column(
        db.String(30),
        nullable=False,
        default="Pago"
    )

    # ==========================
    # ALERTAS
    # ==========================
    dias_alerta = db.Column(
        db.Integer,
        nullable=False,
        default=7
    )

    avisar_vencimentos = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    destacar_recorrentes = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # ==========================
    # METAS
    # ==========================
    meta_mensal = db.Column(
        db.Numeric(12, 2),
        default=0
    )

    meta_anual = db.Column(
        db.Numeric(12, 2),
        default=0
    )

    # ==========================
    # DASHBOARD
    # ==========================
    mostrar_grafico_categorias = db.Column(
        db.Boolean,
        default=True
    )

    mostrar_comparativo_anual = db.Column(
        db.Boolean,
        default=True
    )

    # ==========================
    # CONTROLE
    # ==========================
    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )