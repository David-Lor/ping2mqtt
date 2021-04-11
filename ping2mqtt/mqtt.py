import asyncio

from asyncio_mqtt import Client

from .models import PingResult
from .settings import MQTTSettings


class MQTT:
    _client: Client

    def __init__(self, settings: MQTTSettings):
        self._client = Client(
            hostname=settings.host,
            port=settings.port,
            username=settings.username,
            password=settings.password,
            client_id=settings.client_id,
            # TODO SSL Support
            transport=settings.transport
        )
        self._publish_queue = asyncio.Queue()

    @property
    def queue(self):
        return self._publish_queue

    async def connect(self):
        await self._client.connect()
        print("MQTT connected!")

    async def publish(self, ping_result: PingResult):
        print("TX", ping_result.host, ping_result.time)
        await self._client.publish(f"test/{ping_result.host}", str(ping_result.time))

    async def run(self):
        while True:
            print("Waiting for queue msg...")
            ping_result: PingResult = await self._publish_queue.get()
            asyncio.create_task(self.publish(ping_result))
