import asyncio
import logging
import time
from typing import List, Dict, Union

from asyncraft.message import Message, KeyType
from asyncraft.handler import AsyncHandler, SyncHandler, AbstractHandler
from asyncraft.pool import AbstractPool, Pool


class AbstractBroker:
    loop: asyncio.AbstractEventLoop

    def broadcast_message(self, message: Message) -> None:
        """Broadcast a message to all handlers. Is thread safe."""
        raise NotImplementedError

    def get_next_free_identifier(self, prefix: Union[str, None] = None) -> str:
        """Get the next free identifier"""
        raise NotImplementedError

    def register_handler(self, handler: Union[SyncHandler, AsyncHandler]):
        """Register a sync handler to the broker, which will be executed in a thread pool"""
        raise NotImplementedError

    def unregister_handler(self, handler: Union[str, SyncHandler, AsyncHandler]):
        """Unregister a sync handler from the broker"""
        raise NotImplementedError

    def shutdown(self):
        """Shutdown the broker"""
        raise NotImplementedError


class Broker(AbstractBroker):

    def __init__(self, pool: AbstractPool = None, loop: asyncio.AbstractEventLoop = None):
        self.handlers: Dict[KeyType, List[AbstractHandler]] = {}
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        if pool is None:
            self.pool = Pool(loop=self.loop)
        else:
            self.pool = pool

    def register_handler(self, handler: AbstractHandler):

        for handlers in self.handlers.values():
            for set_handler in handlers:
                if handler.identifier == set_handler:
                    raise ValueError(f"Handler with identifier {handler.identifier} already registered")

        for key in handler.keys:
            if key not in self.handlers:
                self.handlers[key] = []
            self.handlers[key].append(handler)

    def get_next_free_identifier(self, prefix: Union[str, None] = None) -> str:
        if prefix is None:
            prefix = "asyncraft_handler"
        i = 0
        while True:
            found = False
            identifier = f"{prefix}_{i}"
            for handlers in self.handlers.values():
                for handler in handlers:
                    if handler.identifier == identifier:
                        found = True
                        break
                if found:
                    break
            if not found:
                return identifier
            i += 1

    def unregister_handler(self, handler: Union[str, AbstractHandler]):
        if isinstance(handler, AbstractHandler):
            identifier = handler.identifier
        elif isinstance(handler, str):
            identifier = handler
        else:
            raise ValueError(f"Handler must be of type AbstractHandler or str, not {type(handler)}")
        for key in self.handlers:
            self.handlers[key] = [h for h in self.handlers[key] if h.identifier != identifier]

    def broadcast_message(self, message: Message) -> None:
        if message is None:
            return
        already_contacted = set()
        #Needed to contact handlers only once
        message_key = message.key if isinstance(message.key, tuple) else (message.key,)
        found = False
        for key in message_key:
            if key in self.handlers:
                for handler in self.handlers[key]:
                    if handler.identifier in already_contacted:
                        continue
                    if handler.handler_type == "Sync":
                        self.pool.execute_handler(handler, message, self.broadcast_message)
                    elif handler.handler_type == "Async":
                        self.pool.execute_async_handler(handler, message, self.broadcast_message)

                    already_contacted.add(handler.identifier)
                    found = True
        if not found:
            logging.warning(f"No handler found for message {message}")

    def shutdown(self):
        self.pool.shutdown()
        self.handlers.clear()
