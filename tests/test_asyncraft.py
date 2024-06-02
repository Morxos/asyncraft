import asyncio
import logging
import time

import asyncraft
from asyncraft.message import Message

logging.basicConfig(level=logging.DEBUG)


def test_asyncraft():
    asyncraft.init()

    received_sleep_async = False
    received_sleep_sync = False
    call_count = 0

    async def call_back_value_async(message):
        await asyncio.sleep(1)
        nonlocal received_sleep_async
        received_sleep_async = True
        return Message("Key4", "Sleep Finished!")

    def call_back_value_sync(message):
        nonlocal received_sleep_sync
        nonlocal call_count
        received_sleep_sync = True
        call_count += 1
        time.sleep(1)
        return Message("Key2", "Calling async")

    asyncraft.register_handler(asyncraft.SyncHandler(keys=["Key1", "Key3"],
                                                     callback=call_back_value_sync)
                               )

    asyncraft.register_handler(asyncraft.AsyncHandler(keys=["Key2"],
                                                      callback=call_back_value_async)
                               )

    async def main():
        asyncraft.broadcast(Message(("Key1", "Key3"), "Calling sync"))
        await asyncio.sleep(0.5)
        assert received_sleep_sync
        assert not received_sleep_async
        await asyncio.sleep(2)
    gb = asyncraft._global_broker
    asyncraft.start(main())
    assert received_sleep_sync
    assert received_sleep_async
    assert call_count == 1
    asyncraft.shutdown()


def test_asyncraft_cal_and_wait():
    asyncraft.init()
    called = 0

    @asyncraft.asyncraft_handler(keys=["Key2"])
    async def call_back_value_async(message: Message):
        assert message.key == "Key2"
        assert message.value == "Calling async"
        nonlocal called
        called += 1
        return Message("Key4", "Sleep Finished!")

    @asyncraft.asyncraft_handler(keys=["Key1"])
    def call_back_value_sync(message: Message):
        assert message.key == "Key1"
        assert message.value == "Calling sync"
        nonlocal called
        called += 1
        return Message("Key3", "Calling async")

    async def main():
        nonlocal called
        message = await asyncraft.broadcast_and_wait(Message("Key1", "Calling sync"), ["Key3"])
        assert message.key == "Key3"
        assert message.value == "Calling async"
        message = await asyncraft.broadcast_and_wait(Message("Key2", "Calling async"), ["Key4"])
        assert message.key == "Key4"
        assert message.value == "Sleep Finished!"

    asyncraft.start(main())
    assert called == 2
    asyncraft.shutdown()
