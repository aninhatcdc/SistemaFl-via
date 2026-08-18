from waitress import serve

from app import app


if __name__ == "__main__":
    print("=" * 50)
    print("Sistema Jurídico")
    print("Servidor iniciado com Waitress")
    print("Acesse:")
    print("http://127.0.0.1:5000")
    print("=" * 50)

    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=8
    )