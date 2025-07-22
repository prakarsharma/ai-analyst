import os
import sys
# import logging
from loguru import logger

from utils.config import conf

def init_logger(name:str):
    """
    Initializes the logger with a specified name.
    The logger will log messages to a file and to the console.
    The log file will be stored in the path specified in the configuration.
    The log file will be named 'log_<name>.log'.
    The logger will log messages with the level 'DEBUG' to the file and level 
    'SUCCESS' to the console. Errors will be logged to stderr.
    """
    logger.remove()
    path = conf["logs"]
    os.makedirs(path, exist_ok=True)
    logfile = f"{path}/log_{name}.log"
    logger.add(logfile, 
               colorize=False, 
               format="{time} | {name}:{function}:{line} | {message}", 
               level="DEBUG")
    logger.add(sys.stdout, 
               colorize=False, 
               format="{message}", 
               level="SUCCESS")
    logger.add(sys.stderr, 
               level="ERROR")
    logger.info("Logger initialized with log file: {}", logfile)