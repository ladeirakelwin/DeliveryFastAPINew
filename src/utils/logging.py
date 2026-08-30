import os
import sys
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    logger.remove()

    # Check environment (default to 'dev' if not set)
    env = os.getenv("APP_ENV", "dev").lower()
    is_dev = env != "prod"

    # Configure handler based on environment
    logger.add(
        sys.stderr,
        level="DEBUG" if is_dev else "INFO",
        backtrace=is_dev,  # True for dev, False for prod
        diagnose=is_dev,  # True for dev, False for prod (Prevents leaking variables)
    )

    # Intercept Uvicorn and FastAPI logs
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logger.info(is_dev)
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
