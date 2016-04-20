# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

from abc import ABCMeta


class BackendBase(metaclass=ABCMeta):
    """
    Base class for backends of s3tp.
    """

    @abstractmethod
    def recv(self, length):
        """
        Receives at maximum length bytes of data from the backend.
        """
        pass

    @abstractmethod
    def send(self, data):
        """
        Sends the given data via this backend.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Returns True if the backend is connected and able to send and receive
        data at the moment.
        """
        pass
