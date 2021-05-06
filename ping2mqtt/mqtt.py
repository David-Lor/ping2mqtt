import asyncio
import ssl

from asyncio_mqtt import Client

from .models import PingResult
from .settings import MQTTSettings
from .logging import logger


class MQTT:
    _client: Client

    def __init__(self, settings: MQTTSettings):
        self._client = Client(
            hostname=settings.host,
            port=settings.port,
            username=settings.username,
            password=settings.password,
            client_id=settings.client_id,
            transport=settings.transport
        )
        if settings.ssl_enabled:
            # noinspection PyProtectedMember
            self._client._client.tls_set(
                ca_certs=settings.ssl_ca_certs,
                certfile=settings.ssl_certfile,
                keyfile=settings.ssl_keyfile,
                tls_version=ssl.PROTOCOL_TLS,
                cert_reqs=ssl.CERT_REQUIRED
            )
        self._publish_queue = asyncio.Queue()
        self._settings = settings

    @property
    def queue(self):
        return self._publish_queue

    async def connect(self):
        await self._client.connect()
        logger.info("MQTT connected")

    async def _publish(self, topic: str, payload: str):
        logger.debug(f"MQTT pub @ \"{topic}\" : \"{payload}\"")
        await self._client.publish(topic, payload)

    async def _publish_ping_result(self, ping_result: PingResult):
        topic = self._settings.format_topic(ping_result.host)
        payload = str(ping_result.time) if not ping_result.failed else self._settings.failed_ping_payload
        await self._publish(topic, payload)

    async def run(self):
        while True:
            ping_result: PingResult = await self._publish_queue.get()
            asyncio.create_task(self._publish_ping_result(ping_result))
