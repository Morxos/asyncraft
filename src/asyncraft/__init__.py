import asyncio
import threading
from typing import Union, List, Coroutine, Any

from asyncraft.broker import Broker, AbstractBroker
from asyncraft.handler import AsyncHandler, SyncHandler
from asyncraft.message import Message, KeyType
from asyncraft.queues import MessageQueue

_event_loop: Union[None, asyncio.AbstractEventLoop] = None
_global_broker: Union[AbstractBroker, None] = None


def start(runnable: Coroutine[Any, Any, None]):
    """Start the global broker."""
    global _global_broker
    if _global_broker is None:
        raise ValueError("Broker not initialized.")
    loop = _global_broker.loop
    loop.run_until_complete(runnable)


def broadcast(message: Message) -> None:
    """Broadcast a message to all handlers, subscribing to one of the message keys."""
    _global_broker.broadcast_message(message)


async def broadcast_and_wait(message: Message, return_keys: List[KeyType],
                             timeout: Union[None, float] = None) -> Message:
    """Broadcast a message to all handlers, subscribing to the message keys, and waiting for the first response."""
    semaphore = threading.Semaphore(0)
    return_message: Union[Message, None] = None

    async def callback(message: Message):
        nonlocal return_message
        return_message = message
        semaphore.release()

    local_handler = AsyncHandler(identifier=_global_broker.get_next_free_identifier(), keys=return_keys,
                                 callback=callback)
    _global_broker.register_handler(local_handler)
    _global_broker.broadcast_message(message)
    await asyncio.get_event_loop().run_in_executor(None, semaphore.acquire, True, timeout)
    _global_broker.unregister_handler(local_handler)
    return return_message


def register_handler(handler: Union[SyncHandler, AsyncHandler]):
    """Register a sync handler to the broker, which will be executed in a thread pool."""
    _global_broker.register_handler(handler)


def asyncraft_handler(identifier: str, keys: List[KeyType]):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            register_handler(AsyncHandler(identifier=identifier, keys=keys, callback=func))
        else:
            register_handler(SyncHandler(identifier=identifier, keys=keys, callback=func))
        return func

    return decorator


def register_queue(queue: MessageQueue):
    """Register a message queue to the broker, which can be used to receive messages."""
    async_handler = AsyncHandler(identifier=queue.identifier, keys=queue.keys, callback=queue.put)
    register_handler(async_handler)


def reset(new_event_loop: bool = False):
    """Reset the global broker. Removes all handlers and creates a new event loop if desired. Use with caution."""
    global _global_broker
    global _event_loop
    if _global_broker is not None:
        _global_broker.shutdown()

    try:
        asyncio.get_running_loop()
        event_loop_exists = True

    except RuntimeError:
        event_loop_exists = False

    if new_event_loop or not event_loop_exists:
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
    _event_loop = asyncio.get_event_loop()
    _global_broker = Broker()
    _global_broker.loop = _event_loop


#Initializes the global broker
reset()
