from loguru import logger


def get_logger():
    logger.remove()
    logger.add("logs/pd_chat_{time}.log", format = "{time} | {message}")
    return logger
