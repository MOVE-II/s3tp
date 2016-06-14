# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
s3tp tool communication protocol
"""

import asyncio
import logging
import traceback

from . import toolmessage as message


class ToolProtocol(asyncio.Protocol):
    """
    asyncio protocol spoken on the communication socket
    This is created for each connection on the socket.
    """

    def __init__(self, daemon):
        self.daemon = daemon

        # internal connection handle id
        self.conn_id = None

        # message buffering
        self.buf = bytearray()
        self.maxbuf = (8 * 1024 * 1024)  # 8 MiB max buffer

        # command queue. gets filled with messages from the
        # tool communication socket.
        self.queue = asyncio.Queue()

        # is the connection still alive?
        self.disconnected = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport
        self.conn_id = self.daemon.get_connection_id()

        self.log("new client connected")

    def data_received(self, data):
        """ The tool sent some data to us. """
        if not data.strip():
            return

        if len(self.buf) + len(data) > self.maxbuf:
            self.log("too much data", logging.ERROR)
            self.close()
            return

        self.buf.extend(data)

        # TODO: check if enough data arrived
        # TODO: multi message construction

        msgbuf = self.buf[:]
        del self.buf[:]

        try:
            msg = message.Message.construct(msgbuf)
            self.queue.put_nowait(msg)

        except Exception as exc:
            self.log("\x1b[31;1mfailed constructing message:\x1b[m",
                     logging.ERROR)
            traceback.print_exc()
            self.close()

    def send(self, msg):
        """ Sends a protocol message to the tool. """

        data = msg.pack()
        self.transport.write(data)

    def close(self):
        """ Terminates the connection """

        self.log("terminating connection..")
        self.transport.close()

    def log(self, msg, level=logging.INFO):
        """ logs something for this connection """
        logging.log(level, "[\x1b[1m%3d\x1b[m] %s" % (self.conn_id, msg))

    async def process_messages(self):
        """
        Fetch messages from the queue and react to their request.
        """

        while not self.disconnected.done():

            queue_task = self.daemon.loop.create_task(self.queue.get())

            try:
                # either the connection was lost or
                # we got a command in the queue
                done, pending = await asyncio.wait(
                    [queue_task, self.disconnected],
                    return_when=asyncio.FIRST_COMPLETED)

            except asyncio.CancelledError:
                if not queue_task.done():
                    queue_task.cancel()

                raise

            for future in done:
                # task produced an exception
                exc = future.exception()
                if exc:
                    for future_pending in pending:
                        future_pending.cancel()

                    raise exc

                message = future.result()

                # connection came to its end
                if message == StopIteration:
                    if not self.disconnected.done():
                        self.disconnected.set_result(message)

                    for future_pending in pending:
                        future_pending.cancel()

                    break

                # regular message
                try:
                    answer = await self.control_message(message)
                    self.send(answer)

                except Exception as exc:
                    self.log("\x1b[31;1merror processing request:\x1b[m",
                             logging.ERROR)
                    traceback.print_exc()

    async def control_message(self, msg):
        """
        Parse and handle tool control messages.
        """

        self.log("processing message: %s" % msg, level=logging.DEBUG)

        answer = message.OK()

        # TODO

        return answer
