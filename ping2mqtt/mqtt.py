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
        self._settings = settings

    @property
    def queue(self):
        return self._publish_queue

    async def connect(self):
        await self._client.connect()
        print("MQTT connected!")

    async def _publish(self, topic: str, payload: str):
        print(f"MQTT PUB @ {topic}: {payload}")
        await self._client.publish(topic, payload)

    async def _publish_ping_result(self, ping_result: PingResult):
        topic = self._settings.format_topic(ping_result.host)
        payload = str(ping_result.time)
        await self._publish(topic, payload)

    async def run(self):
        while True:
            ping_result: PingResult = await self._publish_queue.get()
            asyncio.create_task(self._publish_ping_result(ping_result))
