# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
s3tp tool communication messages
"""

from abc import abstractmethod


class ProtoNotImplementedError(NotImplementedError):
    """
    Exception thrown when some protocol handling was not yet implemented.
    """
    pass


class Message:
    """
    Base class for all communication messages.

    The `pack` method creates the buffer to send,
    to transmit, do send(message.pack())
    """

    def __init__(self):
        pass

    @abstractmethod
    def pack(self):
        """
        Pack this message to a binary buffer.
        """
        pass

    @staticmethod
    def construct(msg):
        """
        Constructs a Message object from raw input data.
        """

        clsid = msg['clsid']
        cls = MESSAGE_IDS[clsid]
        if cls:
            return cls(msg)
        else:
            raise ValueError("unknown message type '%d'" % clsid)


class OK(Message):
    """
    Confirm something
    """
    def __init__(self):
        pass


class SendRequest(Message):
    """
    Request to send data
    """
    def __init__(self, data):
        self.data = data


class RecvRequest(Message):
    """
    Request to receive data
    """
    def __init__(self, maxlen):
        self.maxlen = maxlen


class SendDone(Message):
    """
    Confirm the data enqueuing
    """
    def __init__(self):
        pass


class RecvData(Message):
    """
    Provide data
    """
    def __init__(self, data):
        self.data = data
