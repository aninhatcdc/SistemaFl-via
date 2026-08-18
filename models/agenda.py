from datetime import datetime

from models import db


class EventoAgenda(db.Model):
    __tablename__ = "eventos_agenda"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    horario = db.Column(
        db.Time
    )

    descricao = db.Column(
        db.Text
    )

    local = db.Column(
        db.String(150)
    )

    concluido = db.Column(
        db.Boolean,
        default=False
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
        backref="eventos_agenda"
    )

    processo = db.relationship(
        "Processo",
        backref="eventos_agenda"
    )