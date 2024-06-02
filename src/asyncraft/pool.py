import asyncio
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union

from asyncraft.message import Message
from asyncraft.handler import SyncHandler, AsyncHandler


class AbstractPool:

    def execute_handler(self, handler: SyncHandler, message: Message, result_callback=None) -> None:
        """Execute a sync handler with a message and a result callback. If no result callback is provided, the handler
        will be executed without a callback."""
        raise NotImplementedError

    def execute_async_handler(self, handler: AsyncHandler, message: Message, result_callback=None) -> None:
        """Execute an async handler with a message and a result callback. If no result callback is provided, the handler
        will be executed without a callback."""
        raise NotImplementedError

    def shutdown(self) -> None:
        """Shutdown the pool"""
        raise NotImplementedError


class Pool(AbstractPool):

    def __init__(self, max_threads: Union[int, None] = None,loop: asyncio.AbstractEventLoop = None):
        self.max_threads = max_threads
        self.executor = ThreadPoolExecutor(max_threads)
        self.loop = loop

    def execute_handler(self, handler: SyncHandler, message: Message, result_callback=None):
        try:
            if result_callback is not None:
                def runnable(handler: SyncHandler, message: Message, result_callback):
                    result_message: Message = handler(message)
                    result_callback(result_message)
                self.executor.submit(runnable, handler, message, result_callback)
            else:
                self.executor.submit(handler, message)
        except Exception as e:
            logging.error(f"Error in handler {handler.identifier}: {e}")

    def execute_async_handler(self, handler: AsyncHandler, message: Message, result_callback=None):
        try:
            if result_callback is not None:
                async def runnable(handler: AsyncHandler, message: Message, result_callback):
                    result_message: Message = await handler(message)
                    result_callback(result_message)
                asyncio.run_coroutine_threadsafe(runnable(handler, message, result_callback), self.loop)
            else:
                asyncio.run_coroutine_threadsafe(handler(message), self.loop)
        except Exception as e:
            logging.error(f"Error in handler {handler.identifier}: {e}")

    def shutdown(self) -> None:
        self.executor.shutdown()
