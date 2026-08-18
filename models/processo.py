from datetime import datetime, date
from models import db


class Processo(db.Model):
    __tablename__ = "processos"

    id = db.Column(db.Integer, primary_key=True)

    numero = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(50))
    tribunal = db.Column(db.String(100))
    comarca = db.Column(db.String(100))
    vara = db.Column(db.String(100))
    situacao = db.Column(db.String(50))

    data_entrada = db.Column(db.Date)
    proximo_prazo = db.Column(db.Date)

    advogado = db.Column(db.String(100))
    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    @property
    def dias_para_prazo(self):
        """
        Retorna a quantidade de dias restantes para o próximo prazo.

        Exemplo:
        -5 = prazo vencido há 5 dias
         0 = vence hoje
         1 = vence amanhã
         7 = vence em uma semana
        """

        if not self.proximo_prazo:
            return None

        return (self.proximo_prazo - date.today()).days