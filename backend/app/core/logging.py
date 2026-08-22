import logging
import os
import sys


def setup_logging():
    log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence overly verbose external loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger("gold_fundamental")
