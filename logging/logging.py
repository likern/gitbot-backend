import asyncio


class LoggingPolicy:
    def __init__(self, retry=False, min_retry=0, max_retry=0, retry_delay=0, timeout=0):
        self._retry = retry
        self._min_retry = min_retry
        self._max_retry = max_retry
        self._retry_delay = retry_delay
        self._timeout = timeout


class AsyncLogging:
    def __init__(self, motor_client, *, database: str, collection: str,
                 machine_id: str, policy: LoggingPolicy = LoggingPolicy()):
        self._asyncio_loop = asyncio.get_running_loop()
        self._motor_client = motor_client
        self._database = database
        self._collection = collection
        self._policy = policy
        self._client = self._motor_client[self._database][self._collection]
        self._base_log_object = {
            "machine_id": None,
            "level": None,
            "message": None,
            "full_message": None
        }
        self.

    async def info():
        pass

    async def debug():
        pass

    async def warning():
        pass

    async def critical():
        pass

    async def log_data(data, *, level):
        json = {
            "machine_id": MACHINE_ID,
            "level"
        }
        await db.logs.insert_one(data)

    async def _logging(self, data: dict):
        coro = self._client.insert_one(data)
        try:
            await asyncio.wait_for(coro, self._policy._timeout)
        except asyncio.TimeoutError:
            asyncio.sleep(self._policy._retry_delay)
            asyncio.create_task(coro)

    async def logging(self, data: dict):
        try:
            await asyncio.wait_for(self._logging(data), self._policy._timeout)
        except asyncio.TimeoutError:
            asyncio.sleep(self._policy._retry_delay)
            asyncio.create_task(coro)
