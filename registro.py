"""Configuracion de logging a archivo para diagnosticar errores en produccion."""
import logging
import logging.handlers
import os

LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "app.log")


def configurar_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))

    logging.basicConfig(level=logging.INFO, handlers=[handler])
