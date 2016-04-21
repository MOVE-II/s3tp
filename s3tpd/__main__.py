# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
main module invocation entry point
"""


import argparse
import asyncio
import logging
import os

from .config import Config
from .s3tpd import S3TPD
from .util import log_setup


def main():
    cmd = argparse.ArgumentParser()
    cmd.add_argument("-c", "--config", default="/etc/s3tp/s3tpd.conf",
                     help="configuration file name")
    cmd.add_argument("-d", "--debug", action="store_true",
                     help="enable asyncio debugging")
    cmd.add_argument("-v", "--verbose", action="count", default=0,
                     help="increase program verbosity")
    cmd.add_argument("-q", "--quiet", action="count", default=0,
                     help="decrease program verbosity")

    args = cmd.parse_args()

    print("\x1b[1;32ms3tpd initializing...\x1b[m")

    # set up log level
    log_setup(args.verbose - args.quiet)

    loop = asyncio.get_event_loop()

    # enable asyncio debugging
    loop.set_debug(args.debug)

    try:
        # load all config files
        cfg = Config(args.config)

        # remove the old socket or create the folder
        try:
            os.unlink(cfg.comm_socket)
        except OSError:
            if os.path.exists(cfg.comm_socket):
                raise
            else:
                sockdir = os.path.dirname(cfg.comm_socket)
                if not os.path.exists(sockdir):
                    try:
                        logging.info(
                            "creating socket directory '%s'" % sockdir)
                        os.makedirs(sockdir, exist_ok=True)
                    except PermissionError as exc:
                        raise exc from None

        logging.error("\x1b[1;32ms3tpd starting...\x1b[m")

        daemon = S3TPD(loop, cfg)
        daemon.launch()

    except Exception:
        logging.exception("\x1b[31;1mfatal internal exception\x1b[m")

    logging.info("cleaning up...")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    print("\nkthxbai")
