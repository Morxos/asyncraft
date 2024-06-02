import asyncio
import time

import asyncraft
from asyncraft import MessageQueue
from asyncraft.message import Message

total_count = 2000


def test_queue():
    asyncraft.init()
    queue = MessageQueue(["Key", "Key1"])
    asyncraft.register_queue(queue)

    async def reader_1():
        """This reader will read from the queue asynchronously."""
        read_messages = set()
        nonlocal queue
        reader_1_count = 0
        while reader_1_count < total_count / 4:
            message = await queue.async_get()
            read_messages.add(message.value)
            reader_1_count += 1
        while reader_1_count < total_count / 2:
            message = await queue.async_get(blocking=False)
            if message is not None:
                reader_1_count += 1
                read_messages.add(message.value)
        print("Reader 1 finished")
        return read_messages

    def reader_2():
        """This reader will read from the queue via threading."""

        read_messages = set()
        nonlocal queue
        reader_2_count = 0
        while reader_2_count < total_count / 4:
            message = queue.get()
            read_messages.add(message.value)
            reader_2_count += 1
        while reader_2_count < total_count / 2:
            message = queue.get(blocking=False)
            if message is not None:
                reader_2_count += 1
                read_messages.add(message.value)
        print("Reader 2 finished")
        return read_messages

    async def producer():
        """This producer will write to the queue."""
        for i in range(total_count):
            asyncraft.broadcast(Message(("Key", "Key1"), i))

            await asyncio.sleep(0)

    async def run():
        reads1, reads2, _ = await asyncio.gather(reader_1(), asyncio.get_running_loop().run_in_executor(None, reader_2),
                                                 producer())
        assert len(reads1) + len(reads2) == total_count
        assert reads1.intersection(reads2) == set()

    asyncraft.start(run())
