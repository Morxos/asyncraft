import asyncio
import threading
from typing import Union, List

from asyncraft.broker import Broker
from asyncraft.handler import AsyncHandler, SyncHandler
from asyncraft.message import Message, KeyType
from asyncraft.queues import MessageQueue

_global_broker = Broker()


def broadcast_message(message: Message) -> None:
    """Broadcast a message to all handlers, subscribing to one of the message keys."""
    _global_broker.broadcast_message(message)


async def broadcast_and_wait(message: Message, return_keys: List[KeyType],
                                   timeout: Union[None, float] = None) -> Message:
    """Broadcast a message to all handlers, subscribing to the message keys, and waiting for the first response."""
    semaphore = threading.Semaphore(0)
    return_message: Union[Message, None] = None

    def callback(message: Message):
        nonlocal return_message
        return_message = message
        semaphore.release()

    local_handler = AsyncHandler(keys=return_keys, callback=callback)
    _global_broker.register_async_handler(local_handler)
    _global_broker.broadcast_message(message)
    await asyncio.get_event_loop().run_in_executor(None, semaphore.acquire, True, timeout)
    _global_broker.unregister_async_handler(local_handler)
    print(f"Returning message {return_message}")
    return return_message



def register_async_handler(async_handler: AsyncHandler):
    """Register an async handler to the broker, which will be executed in the asyncio event loop."""
    _global_broker.register_async_handler(async_handler)


def register_handler(handler: SyncHandler):
    """Register a sync handler to the broker, which will be executed in a thread pool."""
    _global_broker.register_handler(handler)


def register_queue(queue: MessageQueue):
    """Register a message queue to the broker, which can be used to receive messages."""
    async_handler = AsyncHandler(keys=queue.keys, callback=queue.put)
    register_async_handler(async_handler)


def reset():
    """Reset the global broker."""
    global _global_broker
    _global_broker.shutdown()
    _global_broker = Broker()
