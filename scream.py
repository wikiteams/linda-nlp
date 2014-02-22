import sys
import logging
import logging.handlers
import logging.config
import datetime

DISABLE__STD = False

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

intelliTag_verbose = True


def log(s):
    if intelliTag_verbose:
        logger.info(s)


def say(s):
    if intelliTag_verbose:
        print s


def ssay(s):
    if intelliTag_verbose:
        print datetime.datetime.now() + ': ' + s
        logger.info(s)


def log_error(s):
    if intelliTag_verbose:
        print datetime.datetime.now() + ': ' + s
        logger.error(s)


def log_warning(s):
    if intelliTag_verbose:
        print datetime.datetime.now() + ': ' + s
        logger.warning(s)


def log_debug(s):
    if intelliTag_verbose:
        print datetime.datetime.now() + ': ' + s
        logger.debug(s)


def std_write(s):
    if (intelliTag_verbose) and (not DISABLE__STD):
        sys.stdout.write(s)
        sys.stdout.flush()
