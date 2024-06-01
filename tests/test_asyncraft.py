import asyncio
import threading
import time

import asyncraft
from asyncraft.message import Message


def test_asyncraft():
    asyncraft.reset()

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

    asyncraft.register_async_handler(asyncraft.AsyncHandler(keys=["Key2"],
                                                            callback=call_back_value_async)
                                     )

    async def main():
        asyncraft.broadcast_message(Message(("Key1", "Key3"), "Calling sync"))
        await asyncio.sleep(0.5)
        assert received_sleep_sync
        assert not received_sleep_async
        await asyncio.sleep(2)

    asyncio.run(main())
    assert received_sleep_sync
    assert received_sleep_async
    assert call_count == 1


def test_asyncraft_cal_and_wait():
    asyncraft.reset()
    called = 0


    async def call_back_value_async(message):
        nonlocal called
        called += 1
        return Message("Key4", "Sleep Finished!")

    def call_back_value_sync(message):
        nonlocal called
        called += 1
        return Message("Key3", "Calling async")

    asyncraft.register_handler(asyncraft.SyncHandler(keys=["Key1"],
                                                     callback=call_back_value_sync)
                               )

    asyncraft.register_async_handler(asyncraft.AsyncHandler(keys=["Key2"],
                                                            callback=call_back_value_async)
                                     )

    async def main():
        message = await asyncraft.broadcast_and_wait(Message(("Key1"), "Calling sync"), ["Key3"])
        assert message.key == "Key3"
        assert message.value == "Calling async"
        message = await asyncraft.broadcast_and_wait(Message(("Key2"), "Calling sync"), ["Key4"])
        assert message.key == "Key4"
        assert message.value == "Sleep Finished!"

    asyncio.run(main())
    assert called == 2
