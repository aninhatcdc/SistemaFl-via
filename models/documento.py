from datetime import datetime
from models import db


class Documento(db.Model):
    __tablename__ = "documentos"

    id = db.Column(db.Integer, primary_key=True)

    nome_arquivo = db.Column(db.String(200), nullable=False)
    caminho_arquivo = db.Column(db.String(300), nullable=False)
    tipo = db.Column(db.String(50))
    descricao = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )