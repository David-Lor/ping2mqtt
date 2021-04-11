import asyncio
from json import JSONDecodeError

from .mqtt import MQTT
from .ping import Ping
from .settings import MQTTSettings, read_settings_file
from .logging import logger


async def amain():
    hosts = []
    try:
        hosts = read_settings_file()
    except FileNotFoundError:
        logger.error("No hosts file found")
        exit(1)
    except (ValueError, JSONDecodeError):
        logger.exception("Invalid format of hosts file")
        exit(1)
    if not hosts:
        logger.error("No hosts defined")
        exit(1)

    mqtt = MQTT(MQTTSettings())
    await mqtt.connect()
    asyncio.create_task(mqtt.run())

    ping = Ping(mqtt.queue)
    await ping.run(hosts)
    # TODO more clean exit


def main():
    asyncio.run(amain())
