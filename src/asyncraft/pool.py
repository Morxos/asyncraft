import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union

from asyncraft.message import Message
from asyncraft.handler import SyncHandler, AsyncHandler


class AbstractPool:

    async def execute_handler(self, handler: SyncHandler, message: Message, result_callback=None) -> None:
        """Execute a sync handler with a message and a result callback. If no result callback is provided, the handler
        will be executed without a callback."""
        raise NotImplementedError

    async def execute_async_handler(self, handler: AsyncHandler, message: Message, result_callback=None) -> None:
        """Execute an async handler with a message and a result callback. If no result callback is provided, the handler
        will be executed without a callback."""
        raise NotImplementedError

    def shutdown(self) -> None:
        """Shutdown the pool"""
        raise NotImplementedError


class Pool(AbstractPool):

    def __init__(self, max_threads: Union[int, None] = None):
        self.max_threads = max_threads
        self.executor = ThreadPoolExecutor(max_threads)

    async def execute_handler(self, handler: SyncHandler, message: Message, result_callback=None):
        if result_callback is not None:
            result_message: Message = await asyncio.get_event_loop().run_in_executor(self.executor, handler, message)
            result_callback(result_message)
        else:
            self.executor.submit(handler, message)

    async def execute_async_handler(self, handler: AsyncHandler, message: Message, result_callback=None):
        if result_callback is not None:
            result_message: Message = await asyncio.create_task(handler(message))
            result_callback(result_message)
        else:
            asyncio.create_task(handler(message))

    def shutdown(self) -> None:
        self.executor.shutdown()
