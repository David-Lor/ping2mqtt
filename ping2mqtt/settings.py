import os
import json
from uuid import uuid4
from socket import gethostname
from typing import List, Optional

import pydantic

from .models import PingHost
from .logging import logger

ENV_FILE = os.getenv("ENV_FILE", ".env")


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class GeneralSettings(BaseSettings):
    hosts_file: str = "hosts"


class MQTTSettings(BaseSettings):
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = None
    transport: str = "tcp"
    base_topic: str = "ping"

    @pydantic.validator("client_id", pre=True)
    def _default_client_id(cls, v):
        if v is None:
            v = f"ping2mqtt@{gethostname()}_{uuid4()}"
        return v

    def format_topic(self, suffix_topic: str):
        result = f"{self.base_topic}/{suffix_topic}"
        while "//" in result:
            result.replace("//", "/")
        return result

    class Config(BaseSettings.Config):
        env_prefix = "MQTT_"


general_settings = GeneralSettings()


def _parse_json_file() -> List[PingHost]:
    filename = general_settings.hosts_file
    if not filename.endswith(".json"):
        filename += ".json"
    logger.debug(f"Loading hosts file {filename} ...")

    with open(filename, "r") as file:
        parsed = json.load(file)
        if not isinstance(parsed, list):
            raise ValueError("JSON file is not an array")

        hosts: List[PingHost] = list()
        for parsed_obj in parsed:
            if not isinstance(parsed_obj, dict):
                raise ValueError("Array contains other types than objects")
            hosts.append(PingHost(**parsed_obj))

        return hosts


def _parse_ndjson_file() -> List[PingHost]:
    filename = general_settings.hosts_file
    if not filename.endswith(".ndjson"):
        filename += ".ndjson"
    logger.debug(f"Loading hosts file {filename} ...")

    with open(filename, "r") as file:
        hosts: List[PingHost] = list()
        while True:
            line = file.readline()
            if not line:
                break

            parsed_line = json.loads(line.strip())
            if not isinstance(parsed_line, dict):
                raise ValueError("Array contains other types than objects")
            hosts.append(PingHost(**parsed_line))

        return hosts


def read_settings_file() -> List[PingHost]:
    if general_settings.hosts_file.endswith(".ndjson"):
        return _parse_ndjson_file()
    if general_settings.hosts_file.endswith(".json"):
        return _parse_json_file()

    try:
        return _parse_ndjson_file()
    except FileNotFoundError:
        return _parse_json_file()
