from typing import List, Callable, Any

from asyncraft.message import Message


class SyncHandler:
    def __init__(self, keys: List[int | float | str | bool | tuple | frozenset], callback: Callable[[Message], Any] = None):
        self.keys = keys
        self.callback = callback

    def __call__(self, message: Message) -> Message:
        if self.callback is None:
            raise NotImplementedError
        return self.callback(message)


class AsyncHandler:
    def __init__(self, keys: List[int | float | str | bool | tuple | frozenset], callback: Callable[[Message], Any] = None):
        self.keys = keys
        self.callback = callback

    async def __call__(self, message: Message) -> Message:
        if self.callback is None:
            raise NotImplementedError
        return await self.callback(message)
