import asyncio
import time

import asyncraft


def ping_handler_function(message):
    """This is a sync handler that will respond to the Pong handler."""
    print(f"Received {message.key} with value {message.value}")
    time.sleep(1)
    return asyncraft.Message("Pong", "Pong!")


ping_handler = asyncraft.SyncHandler(keys=["Ping"], callback=ping_handler_function)
asyncraft.register_handler(ping_handler)


async def pong_handler_function(message):
    """This is an async handler that will respond to the Ping handler."""
    print(f"Received {message.key} with value {message.value}")
    await asyncio.sleep(1)
    return asyncraft.Message("Ping", "Ping!")


pong_handler = asyncraft.AsyncHandler(keys=["Pong"], callback=pong_handler_function)
asyncraft.register_async_handler(pong_handler)


async def main():
    asyncraft.broadcast_message(asyncraft.Message("Ping", "Ping!"))

    while True:
        print("Tick...")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
