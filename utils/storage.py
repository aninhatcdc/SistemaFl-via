import os
from pathlib import Path

from flask import current_app


def storage_root():
    """
    Diretório persistente para arquivos enviados/gerados.

    Local: diretório do projeto.
    Render: configure STORAGE_ROOT=/var/data.
    """
    configurado = os.environ.get("STORAGE_ROOT", "").strip()

    if configurado:
        raiz = Path(configurado)
    else:
        raiz = Path(current_app.root_path)

    raiz.mkdir(parents=True, exist_ok=True)
    return raiz


def storage_path(*partes):
    caminho = storage_root().joinpath(*partes)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return caminho


def caminho_storage_relativo(caminho):
    """Converte uploads/... em caminho absoluto no storage persistente."""
    if not caminho:
        return None

    caminho = str(caminho).replace("\\", "/").lstrip("/")

    if caminho.startswith("uploads/"):
        return storage_root() / caminho

    return storage_root() / caminho
