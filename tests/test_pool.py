import asyncio

import pytest

from asyncraft.handler import SyncHandler, AsyncHandler
from asyncraft.message import Message
from asyncraft.pool import Pool


@pytest.fixture
def pool():
    pool = Pool()
    yield pool
    pool.shutdown()


def test_sync_handler(pool):
    handler = SyncHandler(keys=["Test"],
                          callback=lambda message: Message("Test1" + message.key, "Value1" + message.value))
    message = Message("Test", "Value")
    call_back_value = None

    async def run():
        def callback(message):
            nonlocal call_back_value
            call_back_value = message

        await pool.execute_handler(handler, message, callback)
        #Without callback
        await pool.execute_handler(handler, message)
        pool.shutdown()

    asyncio.run(run())
    assert call_back_value == Message("Test1Test", "Value1Value")


def test_async_handler(pool):
    async def handler_function(message: Message):
        return Message("Test1" + message.key, "Value1" + message.value)

    handler = AsyncHandler(keys=["Test"],
                           callback=handler_function)
    message = Message("Test", "Value")
    call_back_value = None

    async def run():
        def callback(message):
            nonlocal call_back_value
            call_back_value = message

        await pool.execute_async_handler(handler, message, callback)
        #Without callback
        await pool.execute_async_handler(handler, message)
        pool.shutdown()

    asyncio.run(run())
    assert call_back_value == Message("Test1Test", "Value1Value")
