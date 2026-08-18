from datetime import datetime

from models import db


class LancamentoFinanceiro(db.Model):
    __tablename__ = "lancamentos_financeiros"

    id = db.Column(db.Integer, primary_key=True)

    # Receita ou Despesa
    tipo = db.Column(
        db.String(20),
        nullable=False,
        default="Despesa"
    )

    # Nome do gasto ou lançamento
    descricao = db.Column(
        db.String(255),
        nullable=False
    )

    categoria = db.Column(
        db.String(100)
    )

    valor = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    # Mês e ano a que o valor pertence
    competencia_mes = db.Column(
        db.Integer,
        nullable=False
    )

    competencia_ano = db.Column(
        db.Integer,
        nullable=False
    )

    # Data real do pagamento ou recebimento
    data_pagamento = db.Column(
        db.Date
    )

    forma_pagamento = db.Column(
        db.String(50)
    )

    # Pago, Pendente ou Previsto
    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pendente"
    )

    recorrente = db.Column(
        db.Boolean,
        default=False
    )

    observacoes = db.Column(
        db.Text
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=True
    )

    processo_id = db.Column(
        db.Integer,
        db.ForeignKey("processos.id"),
        nullable=True
    )

    cliente = db.relationship(
        "Cliente",
        backref="lancamentos_financeiros"
    )

    processo = db.relationship(
        "Processo",
        backref="lancamentos_financeiros"
    )

    @property
    def mes_nome(self):
        meses = [
            "",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"
        ]

        if 1 <= self.competencia_mes <= 12:
            return meses[self.competencia_mes]

        return "-"