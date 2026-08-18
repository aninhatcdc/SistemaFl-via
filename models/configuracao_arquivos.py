from datetime import datetime

from models import db


class ConfiguracaoArquivos(db.Model):
    __tablename__ = "configuracoes_arquivos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # LIMITES
    # ==========================
    tamanho_maximo_mb = db.Column(
        db.Integer,
        nullable=False,
        default=20
    )

    # ==========================
    # EXTENSÕES
    # ==========================
    extensoes_permitidas = db.Column(
        db.Text,
        nullable=False,
        default=(
            "pdf,doc,docx,xls,xlsx,"
            "png,jpg,jpeg,webp,txt"
        )
    )

    # ==========================
    # ORGANIZAÇÃO
    # ==========================
    organizar_por_cliente = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    organizar_por_processo = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # ==========================
    # COMPORTAMENTO
    # ==========================
    permitir_substituir = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    renomear_automaticamente = db.Column(
        db.Boolean,
        nullable=False,
        default=True
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
    def lista_extensoes(self):
        if not self.extensoes_permitidas:
            return []

        return [
            extensao.strip().lower()
            for extensao
            in self.extensoes_permitidas.split(",")
            if extensao.strip()
        ]

    def extensao_permitida(self, nome_arquivo):
        if "." not in nome_arquivo:
            return False

        extensao = (
            nome_arquivo
            .rsplit(".", 1)[1]
            .lower()
        )

        return extensao in self.lista_extensoes