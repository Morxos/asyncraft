from asyncraft.broker import Broker
from asyncraft.handler import AsyncHandler, SyncHandler
from asyncraft.message import Message

_global_broker = Broker()


def broadcast_message(message: Message) -> None:
    _global_broker.broadcast_message(message)


def register_async_handler(async_handler: AsyncHandler):
    _global_broker.register_async_handler(async_handler)


def register_handler(handler: SyncHandler):
    _global_broker.register_handler(handler)


def reset():
    global _global_broker
    _global_broker.shutdown()
    _global_broker = Broker()
