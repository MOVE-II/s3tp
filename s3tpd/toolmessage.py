# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
s3tp tool communication messages
"""

from abc import ABCMeta, abstractmethod

import struct


# maps message ids to message classes
MESSAGE_IDS = dict()


class ProtoNotImplementedError(NotImplementedError):
    """
    Exception thrown when some protocol handling was not yet implemented.
    """
    pass


class MessageMeta(ABCMeta):
    """
    Message metaclass.
    Adds the message types to the lookup dict.
    """
    def __init__(cls, name, bases, classdict):
        super().__init__(name, bases, classdict)
        MESSAGE_IDS[cls.msgid] = cls


class Message(metaclass=MessageMeta):
    """
    Base class for all communication messages.

    The `pack` method creates the buffer to send,
    to transmit, do send(message.pack())
    """

    # message opcode
    msgid = -1

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

        msgid = struct.unpack("! H", msg[:2])[0]

        cls = MESSAGE_IDS.get(msgid)
        if cls:
            return cls(msg)
        else:
            raise ValueError("unknown message opcode '%d'" % clsid)


class NewConnectionRequest(Message):
    msgid = 0


class NewConnectionAck(Message):
    msgid = 1


class NewConnectionNack(Message):
    msgid = 2


class CloseConnectionRequest(Message):
    msgid = 3


class CloseConnectionAck(Message):
    msgid = 4


class CloseConnectionNack(Message):
    msgid = 5


class ListenRequest(Message):
    msgid = 6


class ListenAck(Message):
    msgid = 7


class ListenNack(Message):
    msgid = 8


class WaitForPeerRequest(Message):
    msgid = 9


class WaitForPeerAck(Message):
    msgid = 10


class WaitForPeerNack(Message):
    msgid = 11


class ConnectionRequest(Message):
    msgid = 12


class ConnectAck(Message):
    msgid = 13


class ConnectNack(Message):
    msgid = 14


class RecvRequest(Message):
    msgid = 15


class RecvAck(Message):
    msgid = 16


class RecvNack(Message):
    msgid = 17


class SendRequest(Message):
    msgid = 18


class SendAck(Message):
    msgid = 19


class SendNack(Message):
    msgid = 20
