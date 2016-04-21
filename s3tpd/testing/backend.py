# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.
"""
Implements a mocking backend.
"""

from ..backend.backendbase import BackendBase
from .mocking import MockingMixin


class MockBackend(BackendBase, MockingMixin):
    """
    A mocking backend that is programmable to simulate different backend
    behavior to the user.
    """

    def recv(self, length):
        """
        Mocked receive method.
        """
        pass

    def send(self, data):
        """
        Mocked send method.
        """
        pass

    def is_connected(self):
        """
        Mocked is_connected method.
        """
        pass
