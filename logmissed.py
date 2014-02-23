import sys
import logging
import logging.handlers
import logging.config
import datetime

DISABLE__STD = False

logging.config.fileConfig('missed.conf')
logger = logging.getLogger(__name__)

intelliDialogue_verbose = False


def log(s):
    if intelliDialogue_verbose:
        logger.info(str(s))


def say(s):
    if intelliDialogue_verbose:
        print str(s)


def ssay(s):
    if intelliDialogue_verbose:
        print str(datetime.datetime.now()) + ': ' + str(s)
        logger.info(s)


def log_error(s):
    if intelliDialogue_verbose:
        print str(datetime.datetime.now()) + ': ' + str(s)
        logger.error(s)


def log_warning(s):
    if intelliDialogue_verbose:
        print str(datetime.datetime.now()) + ': ' + str(s)
        logger.warning(s)


def log_debug(s):
    if intelliDialogue_verbose:
        print str(datetime.datetime.now()) + ': ' + str(s)
        logger.debug(s)


def std_write(s):
    if (intelliDialogue_verbose) and (not DISABLE__STD):
        sys.stdout.write(str(s))
        sys.stdout.flush()
