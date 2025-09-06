#!/usr/bin/env python3
"""
server.py

Entrypoint para rodar a aplicação Flask com suporte opcional ao ngrok.

- Desenvolvimento local:
    python server.py

- Produção com gunicorn:
    gunicorn server:application --workers 3 --bind 0.0.0.0:8000

- Se quiser expor via ngrok (temporário):
    defina NGROK_AUTOSTART=1 no seu .env
"""

import os
import logging
import signal
import sys

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Importa app e db
try:
    from app import app, db
except Exception as e:
    print("❌ Erro ao importar app/db do app.py:", e)
    raise

# Expor application para WSGI servers (gunicorn, uwsgi)
application = app

# Configurações
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
USE_WAITRESS = os.getenv("USE_WAITRESS", "0") in ("1", "true", "True")
USE_NGROK = os.getenv("NGROK_AUTOSTART", "0") in ("1", "true", "True")

# Logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("server")

def ensure_database():
    """Cria tabelas no banco se não existirem"""
    with app.app_context():
        logger.info("🔧 Checando banco de dados...")
        db.create_all()
        logger.info("✅ Banco pronto.")

def run_with_waitress(host: str, port: int):
    """Roda com waitress se instalado"""
    from waitress import serve
    logger.info("🚀 Iniciando com Waitress em %s:%s", host, port)
    serve(application, host=host, port=port)

def run_dev(host: str, port: int, debug: bool):
    """Roda com servidor nativo Flask"""
    logger.info("🚀 Iniciando Flask dev em %s:%s (debug=%s)", host, port, debug)
    application.run(host=host, port=port, debug=debug)

def start_ngrok(port: int):
    """Inicia ngrok e mostra a URL pública"""
    try:
        from pyngrok import ngrok
    except ImportError:
        logger.error("⚠️ pyngrok não instalado. Rode: pip install pyngrok")
        return None

    logger.info("🔌 Abrindo túnel ngrok na porta %s...", port)
    url = ngrok.connect(port, "http")
    logger.info("🌐 Ngrok ativo: %s", url.public_url)
    print("\n🌍 Seu site público (ngrok):", url.public_url, "\n")
    return url.public_url

def handle_signal(signum, frame):
    logger.info("🛑 Sinal recebido (%s). Encerrando...", signum)
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("🔥 Servidor inicializando...")
    ensure_database()

    public_url = None
    if USE_NGROK:
        public_url = start_ngrok(PORT)

    if USE_WAITRESS:
        run_with_waitress(HOST, PORT)
    else:
        run_dev(HOST, PORT, DEBUG)

if __name__ == "__main__":
    main()
