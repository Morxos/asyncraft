import asyncio
import threading
from typing import List, Literal, Union
import logging

from asyncraft.message import KeyType, Message


class AbstractMessageQueue:

    async def put(self, message: Message):
        """Put a message in the queue. Is intended to be mainly called by broker."""
        raise NotImplementedError

    def peek(self) -> Union[Message, None]:
        """Peek at the first message in the queue."""
        raise NotImplementedError

    def get(self, blocking=True) -> Union[Message, None]:
        """Get a message from the queue blocking."""
        raise NotImplementedError

    async def async_get(self, blocking=True) -> Union[Message, None]:
        """Get a message from the queue asynchronously."""
        raise NotImplementedError


class MessageQueue(AbstractMessageQueue):
    def __init__(self, identifier: str, keys: List[KeyType], max_items: int = -1,
                 eviction_policy: Literal["FIFO"] = "FIFO"):
        self.identifier = identifier
        self.queue: List[Message] = []
        self.keys = keys
        self.max_items = max_items
        self.eviction_policy = eviction_policy
        self.get_semaphore = threading.Semaphore(0)
        self.access_semaphore = threading.Semaphore(1)

    async def put(self, message: Message):
        with self.access_semaphore:
            if len(self.queue) >= self.max_items != -1:
                if self.eviction_policy == "FIFO":
                    self.queue.pop(0)
                    logging.warning(f"Queue {self.identifier} is full, evicting oldest message")
                else:
                    raise NotImplementedError
                self.queue.append(message)
            else:
                self.queue.append(message)
                self.get_semaphore.release()

    def peek(self) -> Union[Message, None]:
        with self.access_semaphore:
            if len(self.queue) == 0:
                return None
            return self.queue[0]

    def get(self, blocking=True) -> Union[Message, None]:
        res = self.get_semaphore.acquire(blocking=blocking)
        if not res:
            return None
        with self.access_semaphore:
            return self.queue.pop(0)

    async def async_get(self, blocking=True) -> Union[Message, None]:
        res = await asyncio.get_event_loop().run_in_executor(None, self.get_semaphore.acquire, blocking)
        if not res:
            return None
        with self.access_semaphore:
            return self.queue.pop(0)
