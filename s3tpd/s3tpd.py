# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.

"""
s3tp daemon state storage
"""

import asyncio
import logging
import os

from .toolprotocol import ToolProtocol


class S3TPD:
    """
    The simple stupid satellite transport protocol
    """

    def __init__(self, loop, config):
        self.loop = loop
        self.cfg = config

        # asyncio task for the running server
        self.server = None

        # protocol tasks currently in the loop
        self.proto_tasks = set()

        self.connection_count = 0

    def launch(self):
        try:
            create_coro = self.loop.create_task(self.create())
            self.loop.run_until_complete(create_coro)

            # run dat shit!
            self.loop.run_forever()

        except (KeyboardInterrupt, SystemExit):
            print("")
            logging.info("exiting...")

        # stop listening
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())

        # cancel protocol handlers
        for proto_task in self.proto_tasks:
            proto_task.cancel()

        self.loop.run_until_complete(
            asyncio.gather(*self.proto_tasks, return_exceptions=True))

        # run the loop one more time to process leftover tasks
        self.loop.stop()
        self.loop.run_forever()
        self.loop.close()

    async def create(self):
        """ create the listening socket """

        def create_proto():
            """ creates the socket communication protocol """
            proto = ToolProtocol(self)

            # create message "worker" task
            proto_task = self.loop.create_task(proto.process_messages())
            self.proto_tasks.add(proto_task)

            def conn_finished(fut):
                """ remove the protocol task from the pending list """
                self.proto_tasks.remove(proto_task)

            proto_task.add_done_callback(
                lambda fut: self.proto_tasks.remove(proto_task))

            return proto

        # create unix socket to listen for tool requests
        logging.warn("listening on '%s'..." % self.cfg.comm_socket)
        self.server = await self.loop.create_unix_server(
            create_proto, self.cfg.comm_socket)

        if self.cfg.comm_socket_group:
            # this only works if the current user is a member of the
            # target group!
            shutil.chown(self.cfg.comm_socket, None,
                         self.cfg.comm_socket_group)

        if self.cfg.comm_socket_permissions:
            mode = int(self.cfg.comm_socket_permissions, 8)
            os.chmod(self.cfg.comm_socket, mode)

        # create backend
        self.connection = self.cfg.backend(self.cfg.backend_cfg, self.loop)
        await self.connection.create()


    def get_connection_id(self):
        """ return the next connection id """

        ret = self.connection_count
        self.connection_count += 1
        return ret
