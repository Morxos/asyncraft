import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from asyncraft.message import Message
from asyncraft.handler import SyncHandler, AsyncHandler


class AbstractPool:

    async def execute_handler(self, handler: SyncHandler, message: Message, result_callback=None) -> None:
        raise NotImplementedError

    async def execute_async_handler(self, handler: AsyncHandler, message: Message, result_callback=None) -> None:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError


class Pool(AbstractPool):

    def __init__(self, max_threads: int | None = None):
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
