from loguru import logger
import logging
from datetime import datetime


def get_loguru_logger():
    logger.remove()
    logger.add("logs/pd_chat_{time}.log", format = "{time} | {message}")
    return logger


def get_logger(debug_mode:bool=False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger = logging.getLogger(f"pd_chat_log_{timestamp}")
    if debug_mode:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger.setLevel(level)
    logger.propagate = False
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    fHandler = logging.FileHandler(f"logs/pd_chat_{timestamp}.log")
    fHandler.setLevel(logging.DEBUG)
    logfile_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    fHandler.setFormatter(logfile_format)
    logger.addHandler(fHandler)
    return logger
