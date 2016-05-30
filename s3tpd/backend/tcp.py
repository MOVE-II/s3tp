# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.
"""
Implements a tcp backend for s3tp.
"""

import socket
from .backendbase import BackendBase


class TcpBackend(BackendBase):
    """
    A s3tp backend that uses as TCP socket for underlying communication.
    """

    def __init__(self):
        """
        Constructor that initializes a new socket.
        """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._is_connected = False

    def listen_for_peer(self, host, port):
        """
        Listens on the given host and port for a peer. Blocks until a peer
        connects.
        """
        self._sock.bind((host, port))
        self._sock.listen(1)

        conn, _ = self._sock.accept()
        self._sock.close()
        self._is_connected = True
        self._sock = conn

    def connect_to_peer(self, host, port):
        """
        Connects to a listening peer on the given host and port.
        """
        self._sock.connect((host, port))

    def close(self):
        """
        Closes the underlying tcp connection.
        """
        self._is_connected = False
        self._sock.close()

    def recv(self, length):
        """
        See superclass.
        """
        return self._sock.recv(length)

    def send(self, data):
        """
        See superclass
        """
        return self._sock.send(data)

    def is_connected(self):
        """
        See superclass.
        """
        return self._is_connected
