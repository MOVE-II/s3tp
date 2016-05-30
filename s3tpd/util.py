# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

import logging


def clamp(number, smallest, largest):
    """ return number but limit it to the inclusive given value range """
    return max(smallest, min(number, largest))


def log_setup(setting, default=1):
    """
    Perform setup for the logger.
    Run before any logging.log thingy is called.

    if setting is 0: the default is used, which is WARNING.
    else: setting + default is used.
    """

    levels = (logging.ERROR, logging.WARNING, logging.INFO,
              logging.DEBUG, logging.NOTSET)

    factor = clamp(default + setting, 0, len(levels) - 1)
    level = levels[factor]

    logging.basicConfig(level=level, format="[%(asctime)s] %(message)s")
    logging.error("loglevel: %s" % logging.getLevelName(level))
