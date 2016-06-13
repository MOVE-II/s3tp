# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
Code for loading and parsing config options.
"""

import logging
import os

from configparser import ConfigParser
from pathlib import Path

from .backend.tcp import TCPBackend


class Config:
    """ Main configuration file """

    def __init__(self, filename):
        if not Path(filename).exists():
            logging.error(
                "\x1b[31mConfig file '%s' does not exist.\x1b[m" % (
                    filename))
            exit(1)

        raw = ConfigParser()
        raw.read(filename)

        try:
            self.cfglocation = Path(filename).parent

            # main config
            main = raw["s3tpd"]
            backend = main["backend"]
            self.comm_socket = main["comm_socket"]
            self.comm_socket_group = main.get("comm_socket_group")
            self.comm_socket_permissions = main.get("comm_socket_permissions")

            if backend == "tcp":
                self.backend = TCPBackend
            elif backend == "com":
                raise Exception("TODO: com backend")
            else:
                raise Exception("unknown backend %s" % self.backend)

            self.backend_cfg = self.backend.read_config(raw)

        except KeyError as exc:
            logging.error(
                "\x1b[31mConfig file is missing entry: %s\x1b[m" % (exc))
            exit(1)

        self.verify()

    def verify(self):
        """
        Verifies the validity of the loaded attributes
        """

        if (self.comm_socket_permissions and
            not self.comm_socket_permissions.isnumeric()):
            raise ValueError("socket permission must be an octal number")

        return
