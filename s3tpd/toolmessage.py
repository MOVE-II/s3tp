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

    def dump(self, eventid0, eventid1):
        """
        construct the general message header and add the payload
        """

        # message layout:
        # 2 opcode
        # 2 eventid (first2)
        # 2 eventid (second2)
        # payload

        opcode = self.msgid
        if opcode not in MESSAGE_IDS:
            raise ValueError("unknown opcode!")

        header = struct.pack("! HHH", opcode, eventid0, eventid1)

        return header + self.pack()

    @abstractmethod
    def pack(self):
        """
        Pack this message to a binary buffer.
        """
        pass

    @classmethod
    def construct(msg):
        """
        Constructs a Message object from raw input data.
        """

        msgid = struct.unpack("! H", msg[:2])[0]

        # TODO: event ids

        cls = MESSAGE_IDS.get(msgid)
        if cls:
            return cls(*cls.unpack(msg[6:]))
        else:
            raise ValueError("unknown message opcode '%d'" % clsid)

    @staticmethod
    @abstractmethod
    def unpack(msg):
        """
        return a list of constructor arguments extracted from raw data
        """
        pass


class NackMessage(Message):
    """
    Report a non-successful command.
    """
    dataformat = "! H"

    def __init__(self, error_code):
        self.error_code = error_code

    def pack(self):
        return struct.pack(self.dataformat, self.error_code)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class EmptyMessage(Message):
    """
    A message with no payload.
    """

    def __init__(self):
        pass

    def pack(self):
        return b""

    @staticmethod
    def unpack(msg):
        return []


class NewConnectionRequest(EmptyMessage):
    """
    A tool requests a new connection handle.
    """

    msgid = 0


class NewConnectionAck(Message):
    """
    the daemon created the new connection handle and passes back the id
    """

    msgid = 1
    dataformat = "! H"

    def __init__(self, connection_id):
        self.connection_id = connection_id

    def pack(self):
        return struct.pack(self.dataformat, self.connection_id)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class NewConnectionNack(NackMessage):
    """
    The daemon failed to create the connection handle
    and tells the tool why it failed.
    """

    msgid = 2


class CloseConnectionRequest(Message):
    """
    The tool requests to close a connection.
    """

    msgid = 3
    dataformat = "! H"

    def __init__(self, connection_id):
        self.connection_id = connection_id

    def pack(self):
        return struct.pack(self.dataformat, self.connection_id)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class CloseConnectionAck(EmptyMessage):
    """
    The daemon confirms that the connection was closed.
    """

    msgid = 4


class CloseConnectionNack(NackMessage):
    """
    The daemon reports that the connection could not be closed
    because of some reason.
    """

    msgid = 5


class ListenRequest(Message):
    """
    The tool requests that on some connection it wants to listen.
    """

    msgid = 6
    dataformat = "! H H"

    def __init__(self, connection_id, listen_port):
        self.connection_id = connection_id
        self.listen_port = listen_port

    def pack(self):
        return struct.pack(self.dataformat, self.connection_id,
                           self.listen_port)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class ListenAck(EmptyMessage):
    """
    The daemon reports that the listen request was successful and
    the port is now listening.
    """

    msgid = 7


class ListenNack(NackMessage):
    """
    It could not be listened on the requested port.
    """

    msgid = 8


class WaitForPeerRequest(Message):
    """
    Request that the tool wants to wait until the peer is available.
    TODO: timeout?
    """

    msgid = 9
    dataformat = "! H"

    def __init__(self, connection_id):
        self.connection_id = connection_id

    def pack(self):
        return struct.pack(self.dataformat, self.connection_id)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class WaitForPeerAck(Message):
    """
    The tool gets notified that waiting for the peer suceeded.
    """

    msgid = 10
    dataformat = "! H"

    def __init__(self, peer_port):
        self.peer_port = peer_port

    def pack(self):
        return struct.pack(self.dataformat, self.peer_port)

    @classmethod
    def unpack(msg):
        return struct.unpack(cls.dataformat, msg)


class WaitForPeerNack(NackMessage):
    """
    The tool is notified that Waiting for the peer failed.
    """

    msgid = 11


class ConnectRequest(Message):
    """
    The tool requests to connect to th epeer on a port.
    TODO: timeout?
    """

    msgid = 12
    dataformat = "! H H"

    def __init__(self, connection_id, destination_port):
        self.connection_id = connection_id
        self.destination_port = destination_port

    def pack(self):
        return struct.pack(self.dataformat,
                           self.connection_id,
                           self.destination_port)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class ConnectAck(Message):
    """
    The connection was established.
    """

    msgid = 13
    dataformat = "! H"

    def __init__(self, local_port):
        self.local_port = local_port

    def pack(self):
        return struct.pack(self.dataformat, self.local_port)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class ConnectNack(NackMessage):
    """
    The connection attempt failed.
    """

    msgid = 14


class RecvRequest(Message):
    """
    The tool requests that it wants to receive some data on a connection.
    """

    msgid = 15
    dataformat = "! H H"

    def __init__(self, connection_id, expected_length):
        self.connection_id = connection_id
        self.destination_port = expected_length

    def pack(self):
        return struct.pack(self.dataformat, self.connection_id,
                           self.expected_length)

    @classmethod
    def unpack(cls, msg):
        return struct.unpack(cls.dataformat, msg)


class RecvAck(Message):
    """
    The daemon got some data and provides it to the tool now.
    """

    msgid = 16

    def __init__(self, data):
        self.data = data

    def pack(self):
        return struct.pack("! H {}s".format(len(self.data)),
                           len(self.data),
                           self.data)

    @staticmethod
    def unpack(msg):
        size = struct.unpack("! H", msg[:2])[0]
        return struct.unpack("! {}s".format(size), msg[2:(size + 2)])


class RecvNack(NackMessage):
    """
    The daemon could not receive data from the peer.
    """

    msgid = 17


class SendRequest(Message):
    """
    A tool wants to send some data over a connection.
    """

    msgid = 18

    def __init__(self, connection_id, data):
        self.connection_id = connection_id
        self.data = data

    def pack(self):
        return struct.pack("! H H {}s".format(len(self.data)),
                           self.connection_id,
                           len(self.data),
                           self.data)

    @staticmethod
    def unpack(msg):
        self.connection_id, size = struct.unpack("! H H", msg[:4])
        return struct.unpack("! {}s".format(size), msg[4:(size + 4)])


class SendAck(EmptyMessage):
    """
    Data was sent successfully.
    """
    msgid = 19


class SendNack(NackMessage):
    """
    Data submission failed.
    """
    msgid = 20
