# Asyncraft: Simple event/message passing library with asyncio and threading support
A simple event/message passing library for Python 3.8+ supporting asyncio and threading.
<br>For examples, see the [examples](examples) directory.
### Installation
```bash
pip install asyncraft
```
### Messages
Messages are the first major part of the Asyncraft library. They are used to send data between different parts of the program.
Keys are used for identifying handlers, which should process the given message. Further, Asyncraft supports messages with multiple keys.
```python
import asyncraft
...
# Create a message
message = asyncraft.Message(key='key', value='value')
# Broadcast the message (threadsafe)
asyncraft.broadcast(message)
...
```
### Handlers
The second major part of the Asyncraft library are handlers.
Handlers are used for processing messages.
They can be synchronous or asynchronous.
Synchronous handlers are executed in a separate thread, while asynchronous handlers are executed in an asyncio event loop.
```python
import asyncraft
from asyncraft.handler import SyncHandler, AsyncHandler
...
# Create a sync handler with decorator.
# All sync handlers will be executed in a separate thread of a thread pool.
@asyncraft.asyncraft_handler("handler_0", keys=["key"])
def handler_0(message):
    print(message)
    #Handlers can return a message
    return asyncraft.Message(key='key1', value='value1')
...

# Create an async handler with decorator
# All async handlers will be executed in an asyncio event loop.
@asyncraft.asyncraft_handler("handler_1", keys=["key"])
async def handler_1(message):
    print(message)
...

# Create a sync handler without decorator
# First define the callback function
def handler_2_function(message):
    print(message)
#Then create the handler
handler = SyncHandler("handler_2", keys=["key"], callback=handler_2_function)
#Register the handler
asyncraft.register_handler(handler)

...

# Create an async handler without decorator
#First again define the callback function
async def handler_3_function(message):
    print(message)
#Then create the handler
handler = AsyncHandler("handler_3", keys=["key"], callback=handler_3_function)
#Register the handler
asyncraft.register_handler(handler)
...
```
### Queues
Another major part of Asyncraft are queues.
Queues listen to keys and store messages before they are processed further.
```python
from asyncraft import MessageQueue
from asyncraft import Message
import asyncraft
...
#Create a queue which listenes to keys 'Key' and 'Key1'.
#All messages with at least one of those keys will be stored in the queue.
queue = MessageQueue("queue_1", ["Key", "Key1"])
#Register the queue
asyncraft.register_queue(queue)
...
#Get the next message from the queue. If the queue is empty, block until a message is available.
message: Message = queue.get(blocking=True)
...
#Get the next message from the queue in an async context. If the queue is empty, block until a message is available.
message: Message = queue.async_get(blocking=True) 
...
```
### Broadcast and wait for response
The broadcast_and_wait function can be used to send a message and wait for a response.
```python
import asyncraft
from asyncraft import Message
...
# Create a message
message = Message(key='key', value='value')
# Broadcast the message and wait for a response.
# The response will be the first message with the key 'key1' that is received.
# If no response is received within 10 seconds, None will be returned.
response: Message = asyncraft.broadcast_and_wait(message,["key1"], timeout=10)
```
### Examples
The following examples demonstrate how to use Asyncraft.
#### Ping-Pong
This example demonstrates how to use Asyncraft to create a simple ping-pong system.
```python
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
```
#### Queue
This example demonstrates how to use the MessageQueue class and how one can use it to read and write messages.
```python
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
    queue = MessageQueue("queue1", ["Key", "Key1"])
    asyncraft.register_queue(queue)
    asyncraft.start(main())
```
### License
This project is licensed under the terms of the MIT license.