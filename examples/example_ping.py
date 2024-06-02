"""This example demonstrates how to use the asyncraft library to create a simple ping-pong system."""
import asyncio
import time
import asyncraft


@asyncraft.asyncraft_handler("Ping", keys=["Ping"])
def ping_handler_function(message):
    """This is a sync handler that will respond to the Pong handler. It will be executed in a separate thread."""
    print(f"Received {message.key} with value {message.value}")
    time.sleep(1)
    return asyncraft.Message("Pong", message.value + 1)


@asyncraft.asyncraft_handler("Pong", keys=["Pong"])
async def pong_handler_function(message):
    """This is an async handler that will respond to the Ping handler. It will be executed in the event loop."""
    print(f"Received {message.key} with value {message.value}")
    await asyncio.sleep(1)
    return asyncraft.Message("Ping", message.value + 1)


async def main():
    asyncraft.broadcast(asyncraft.Message("Ping", 0))
    while True:
        #print("Tick...")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncraft.start(main())
