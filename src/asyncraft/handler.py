from typing import List, Callable, Any, Literal

from asyncraft.message import Message, KeyType


class AbstractHandler:
    handler_type: Literal["Sync", "Async"]

    def __init__(self, keys: List[KeyType], callback: Callable[[Message], Any] = None,identifier: str = None):
        self.keys = keys
        self.callback = callback
        self.identifier = identifier


class SyncHandler(AbstractHandler):
    handler_type = "Sync"

    def __call__(self, message: Message) -> Message:
        if self.callback is None:
            raise NotImplementedError
        return self.callback(message)


class AsyncHandler(AbstractHandler):
    handler_type = "Async"

    async def __call__(self, message: Message) -> Message:
        if self.callback is None:
            raise NotImplementedError
        return await self.callback(message)
