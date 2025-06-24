import os
import sys
# import logging
from loguru import logger

from utils.config import conf

def init_logger(name:str):
    logger.remove()
    path = conf["logs"]
    os.makedirs(path, exist_ok=True)
    logfile = f"{path}/log_{name}.log"
    logger.add(logfile, 
               colorize=True, 
               format="{time} | {name}:{function}:{line} | {message}", 
               level="DEBUG")
    logger.add(sys.stdout, 
               colorize=True, 
               format="<green>{time}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <yellow>{message}</yellow>", 
               level="SUCCESS")
    logger.add(sys.stderr, 
               level="ERROR")
    logger.info("Logger initialized with log file: {}", logfile)