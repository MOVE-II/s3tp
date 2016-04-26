# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.
"""
Implements the base class for backends of s3tp.
"""

from abc import abstractmethod, ABCMeta


class BackendBase(metaclass=ABCMeta):
    """
    Base class for backends of s3tp.
    """

    @abstractmethod
    def recv(self, length):
        """
        Receives at maximum length bytes of data from the backend. Returns the
        received buffer as byte string.
        """
        pass

    @abstractmethod
    def send(self, data):
        """
        Sends the given data via this backend. Returns the amount of bytes that
        have actually been sent.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Returns True if the backend is connected and able to send and receive
        data at the moment. Otherwise False is returned.
        """
        pass
