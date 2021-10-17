'''The module containing objects that manage logging.'''

import logging
import datetime


# ----------------------------------------------------------------------------

LEVELS = {"NOTSET":logging.NOTSET, "DEBUG":logging.DEBUG, "INFO":logging.INFO, 
"WARNING":logging.WARNING, "ERROR":logging.ERROR, "CRITICAL":logging.CRITICAL, 
"NONE":logging.CRITICAL+1}

# Conventions for logging levels, from least severe to most severe:
# DEBUG = Detailed information regarding running of application.
# INFO = Confirmation of functions working as expected and/or log of tasks performed.
# WARNING = Note of something unusual; but function still works as expected.
# ERROR = Problem occured. Function unable to achieve outcome.
# CRITICAL = System crash or other urgent matters.
#
# NOTSET is the default. It returns all messages.
# NONE is a setting which returns no messages.

LOGTIME = str(datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S'))

# ----------------------------------------------------------------------------

def get(name: str, level: str = "NOTSET"):
    '''Returns a pre-configured Logger object, used for writing logs.

    For Logger methods, see https://docs.python.org/3/library/logging.html#logging.Logger
    
    For logging level explaination, see mods/log.py itself.

    name = Name of the logger.
    level = Minimum level of logging messages to report: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"
    '''
    logger = logging.getLogger(name=name)
    
    handler = logging.StreamHandler()
    handler_file = logging.FileHandler(filename=f"logs/{LOGTIME}.log", encoding="utf-8")
    formatter =  logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S %z")
    level = LEVELS[level]

    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler_file.setLevel(level)
    handler_file.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(handler_file)

    return logger


def check(name: str):
    '''Returns whether or not a logger of a particular name already exists.'''
    result = name in logging.Logger.manager.loggerDict
    return result


# ----------------------------------------------------------------------------