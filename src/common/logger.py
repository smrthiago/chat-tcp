"""
Sistema de logging estruturado em JSON.

Dois handlers:
- Arquivo: formato JSON (machine-readable, para análise)
- Console: formato legível (human-readable, para desenvolvimento)
"""
import logging
import json
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from src.common.config import Config


class JSONFormatter(logging.Formatter):
    """
    Formatter customizado que serializa cada log record como JSON.
    Facilita parsing automático e integração com ferramentas de observabilidade.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "event": record.funcName,
            "message": record.getMessage(),
        }

        # Dados extras opcionais passados via extra={"data": {...}}
        if hasattr(record, "data"):
            log_data["data"] = record.data

        # Inclui informação de exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str, log_level: str = None) -> logging.Logger:
    """
    Configura e retorna logger com handlers para arquivo (JSON) e console.

    Args:
        name: Nome do logger (ex: 'server', 'client')
        log_level: Nível de log. Default: lido de Config.LOG_LEVEL

    Returns:
        logging.Logger: Logger configurado e pronto para uso.
    """
    logger = logging.getLogger(name)

    # Evita duplicação de handlers em imports repetidos
    if logger.handlers:
        return logger

    level_str = log_level or Config.LOG_LEVEL
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(logging.DEBUG)  # Logger captura tudo; handlers filtram

    os.makedirs(Config.LOG_DIR, exist_ok=True)

    # ── Handler de arquivo (JSON rotativo) ──────────────────────────────────
    log_path = os.path.join(Config.LOG_DIR, f"{name}.log")
    fh = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB por arquivo
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(JSONFormatter())

    # ── Handler de console (texto colorido simplificado) ────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
