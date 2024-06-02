import asyncio
from asyncraft.handler import SyncHandler, AsyncHandler
from asyncraft.message import Message
from asyncraft.pool import Pool


def test_sync_handler():
    handler = SyncHandler("Sync", keys=["Test"],
                          callback=lambda message: Message("Test1" + message.key, "Value1" + message.value))
    message = Message("Test", "Value")
    call_back_value = None

    async def run():
        def callback(message):
            nonlocal call_back_value
            call_back_value = message

        pool = Pool(loop=asyncio.get_event_loop())
        pool.execute_handler(handler, message, callback)
        #Without callback
        pool.execute_handler(handler, message)
        await asyncio.sleep(1)
        pool.shutdown()

    asyncio.run(run())
    assert call_back_value == Message("Test1Test", "Value1Value")


def test_async_handler():
    async def handler_function(message: Message):
        return Message("Test1" + message.key, "Value1" + message.value)

    handler = AsyncHandler("Async", keys=["Test"],
                           callback=handler_function)
    message = Message("Test", "Value")
    call_back_value = None

    async def run():
        def callback(message):
            nonlocal call_back_value
            call_back_value = message

        pool = Pool(loop=asyncio.get_event_loop())
        pool.execute_async_handler(handler, message, callback)
        #Without callback
        pool.execute_async_handler(handler, message)
        await asyncio.sleep(1)
        pool.shutdown()

    asyncio.run(run())
    assert call_back_value == Message("Test1Test", "Value1Value")
