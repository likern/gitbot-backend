import asyncio

store = {}


async def coro():
    print("I'm coro")


async def logging(number, num_retry):
    print(store)
    coroutine = coro()
    identity = id(coroutine)
    print(f"I'm logging {number} with [{identity}]")
    await coroutine

    if identity in store:
        current_retry = store[identity]["current_retry"]
        retry = store[identity]["retry"]
        current_retry = current_retry + 1

        if current_retry > retry:
            return

    else:
        print("else cond")
        store[identity] = {"retry": num_retry, "current_retry": 0}

    await asyncio.sleep(1)
    await logging(number, num_retry)


async def combine():
    await asyncio.gather(
        logging(1, 3), logging(2, 7)
    )


loop = asyncio.get_event_loop()
loop.run_until_complete(logging(1, 3))
