"""This example demonstrates how to use the MessageQueue class and how one can use it to read and write messages."""
import asyncio
import time
import asyncraft
from asyncraft.queues import MessageQueue


async def async_reader(queue: MessageQueue):
    """This function will read messages asynchronously."""
    while True:
        message = await queue.async_get(blocking=True)
        print(f"Reading async {message.key} with value {message.value}")
        await asyncio.sleep(0.1)


def reader(queue: MessageQueue):
    """This function will read messages in another thread."""
    while True:
        message = queue.get(blocking=True)
        print(f"Reading threaded {message.key} with value {message.value}")
        time.sleep(0.1)


async def async_producer():
    """This function will produce messages asynchronously."""
    while True:
        print("Async Producing...")
        asyncraft.broadcast(asyncraft.Message("Key1", "From async producer"))
        await asyncio.sleep(1)


def producer():
    """This function will produce messages synchronously."""
    while True:
        print("Threaded Producing...")
        asyncraft.broadcast(asyncraft.Message("Key", "From thread producer"))
        time.sleep(1)


async def main():
    await asyncio.gather(
        async_reader(queue),
        async_producer(),
        asyncio.to_thread(reader, queue),
        asyncio.to_thread(producer)
    )


if __name__ == "__main__":
    queue = MessageQueue(["Key", "Key1"])
    asyncraft.register_queue(queue)
    asyncraft.start(main())
