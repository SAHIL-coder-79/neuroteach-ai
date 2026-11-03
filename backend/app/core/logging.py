import logging
import sys

def setup_logging(debug: bool = True):
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Suppress verbose noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger("neuroteach")
