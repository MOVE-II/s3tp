# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.
"""
Implements a tcp backend for s3tp.
"""

import asyncio
import logging

from .backendbase import BackendBase
from ..util import Namespace


class TCPClientProto(asyncio.Protocol):
    """
    Simple protocol for transmitting messages via TCP.
    This is the client part of the connection.
    """

    def __init__(self, backend):
        self.backend = backend

    def connection_made(self, transport):
        self.transport = transport
        logging.info("connected to server")


class TCPServerProto(asyncio.Protocol):
    """
    Simple protocol for transmitting messages via TCP.
    This is the server part of the connection.
    """

    def __init__(self, backend):
        self.backend = backend

    def connection_made(self, transport):
        self.transport = transport
        logging.info("a client connected")


class TCPBackend(BackendBase):
    """
    A s3tp backend that uses as TCP socket for underlying communication.
    """

    def __init__(self, cfg, loop):
        """
        Constructor that initializes a new socket.
        """
        self.cfg = cfg
        self.loop = loop

        self.transport = None
        self.protocol = None
        self.server = None

    def recv(self, length):
        raise Exception("TODO")

    def send(self, data):
        raise Exception("TODO")

    def is_connected(self):
        raise Exception("TODO")

    @classmethod
    def read_config(cls, cfg):
        ret = Namespace()

        tcpcfg = cfg["tcp"]

        mode = tcpcfg["mode"]
        if mode in {"server", "client"}:
            ret.mode = mode
        else:
            raise Exception("invalid tcp backend mode: %s" % mode)

        ret.host = tcpcfg["host"]
        ret.port = tcpcfg["port"]

        return ret

    async def create(self):
        logging.info("creating TCP backend...")

        if self.cfg.mode == "server":
            logging.info("starting to listen...")
            self.server = await self.loop.create_server(
                lambda: TCPServerProto(self),
                host=self.cfg.host, port=self.cfg.port)

        elif self.cfg.mode == "client":
            logging.info("connecting to server...")
            self.transport, self.protocol = await self.loop.create_connection(
                lambda: TCPClientProto(self),
                host=self.cfg.host, port=self.cfg.port)
