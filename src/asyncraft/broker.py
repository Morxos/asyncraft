import asyncio
from typing import List, Dict

from asyncraft.message import Message
from asyncraft.handler import AsyncHandler, SyncHandler
from asyncraft.pool import AbstractPool, Pool


class AbstractBroker:

    async def async_broadcast_message(self, message: Message) -> None:
        """Broadcast a message to all handlers"""
        raise NotImplementedError

    def broadcast_message(self, message: Message) -> None:
        """Broadcast a message to all handlers"""
        raise NotImplementedError

    def register_async_handler(self, handler: AsyncHandler):
        """Register an async handler to the broker, which will be executed in the asyncio event loop"""
        raise NotImplementedError

    def unregister_async_handler(self, handler: AsyncHandler):
        """Unregister an async handler from the broker"""
        raise NotImplementedError

    def register_handler(self, handler: SyncHandler):
        """Register a sync handler to the broker, which will be executed in a thread pool"""
        raise NotImplementedError

    def unregister_handler(self, handler: SyncHandler):
        """Unregister a sync handler from the broker"""
        raise NotImplementedError

    def shutdown(self):
        """Shutdown the broker"""
        raise NotImplementedError


class Broker(AbstractBroker):

    def __init__(self, pool: AbstractPool = None):
        self.sync_handlers: Dict[(int, float, complex, bool, str, tuple, frozenset), List[SyncHandler]] = {}
        self.async_handlers: Dict[(int, float, complex, bool, str, tuple, frozenset), List[AsyncHandler]] = {}
        if pool is None:
            self.pool = Pool()
        else:
            self.pool = pool


    def register_handler(self, handler: SyncHandler):
        for key in handler.keys:
            if key not in self.sync_handlers:
                self.sync_handlers[key] = []
            self.sync_handlers[key].append(handler)

    def unregister_handler(self, handler: SyncHandler):
        for key in handler.keys:
            if key in self.sync_handlers:
                self.sync_handlers[key].remove(handler)

    def register_async_handler(self, handler: AsyncHandler):
        for key in handler.keys:
            if key not in self.async_handlers:
                self.async_handlers[key] = []
            self.async_handlers[key].append(handler)

    def unregister_async_handler(self, handler: AsyncHandler):
        for key in handler.keys:
            if key in self.async_handlers:
                self.async_handlers[key].remove(handler)

    def broadcast_message(self, message: Message) -> None:
        if message is None:
            return
        asyncio.run_coroutine_threadsafe(self.async_broadcast_message(message), asyncio.get_running_loop())

    async def async_broadcast_message(self, message: Message) -> None:
        if message is None:
            return
        message_key = message.key if isinstance(message.key, tuple) else (message.key,)
        for key in message_key:
            if key in self.sync_handlers:
                for handler in self.sync_handlers[key]:
                    await self.pool.execute_handler(handler, message, self.broadcast_message)
            if key in self.async_handlers:
                for handler in self.async_handlers[key]:
                    await self.pool.execute_async_handler(handler, message, self.broadcast_message)

    def shutdown(self):
        self.pool.shutdown()
        self.sync_handlers.clear()
        self.async_handlers.clear()
