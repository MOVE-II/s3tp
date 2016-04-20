# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

from s3tpd.testing.mocking import MockingMixing


class MockBackend(MockingMixing):
    """
    A mocking backend that is programmable to simulate different backend
    behavior to the user.
    """

    def recv(self, length):
        pass

    def send(self, data):
        pass

    def is_connected(self):
        pass
