import logging
import sys

logger = logging.getLogger('main')

logger.setLevel(logging.INFO)

logger.addHandler(logging.StreamHandler(sys.stdout))


__all__ = [
    logger
]