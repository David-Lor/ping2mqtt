import asyncio
import subprocess
from time import time
from typing import List, Optional

import parse

from .models import PingHost, PingResult
from .logging import logger


class Ping:
    PING_IGNORE_LINES_CONTAINING = {
        "bytes of data.",
        "ping statistics ---",
        "packets transmitted",
        "rtt min/avg/max/mdev"
    }

    def __init__(self, queue: asyncio.Queue):
        self._queue = queue

    @staticmethod
    def is_ping_installed() -> bool:
        """Verify if the "ping" command is available"""
        return subprocess.check_call(["which", "ping"]) == 0

    @staticmethod
    def _assemble_command(host: PingHost) -> str:
        cmd = [
            "LANG=C",  # Avoid issues with decimal points in "ping" command
            "ping", host.host,
            "-i", str(host.interval)
        ]
        if host.interface:
            cmd.extend(["-I", host.interface])
        return " ".join(cmd)

    @classmethod
    def _parse_ping_line(cls, host: PingHost, line: str) -> Optional[PingResult]:
        """Parse a line output from the "ping" command.
        Returns a PingResult object if the line is a valid ping result (either correct or failed ping);
        or None if the line is not important

        Sample of a "ping" command output:

        PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
        64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=15.9 ms
        64 bytes from 8.8.8.8: icmp_seq=2 ttl=116 time=15.9 ms
        64 bytes from 8.8.8.8: icmp_seq=3 ttl=116 time=19.5 ms

        --- 8.8.8.8 ping statistics ---
        3 packets transmitted, 3 received, 0% packet loss, time 4ms
        rtt min/avg/max/mdev = 15.859/17.078/19.510/1.725 ms
        """
        result = parse.search("time={time} ms", line)
        if result:
            result_time = result["time"]
            logger.debug(f"Ping {host.host} = {result_time}")
            return PingResult(
                host=host.host,
                time=result_time
            )

        # NOTE should try to identify why a ping failed?
        #  If is a problem with the ping command itself, might be better to avoid reporting a failed ping?
        if not any(True for chunk in cls.PING_IGNORE_LINES_CONTAINING if chunk in line):
            logger.debug(f"Ping {host.host} = failed")
            return PingResult(
                host=host.host,
                time=PingResult.TIME_FAILED
            )

    async def _ping_host(self, host: PingHost):
        """Run ping against the given host, indefinitely. Ping results are put on the queue"""
        cmd = self._assemble_command(host)
        logger.trace(f"Running ping command: \"{cmd}\"")
        proc = await asyncio.subprocess.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        last_read = 0
        while proc.returncode is None:
            line = (await proc.stdout.readline()).decode().strip()
            logger.trace(f"Ping line received: \"{line}\"")

            result = self._parse_ping_line(host=host, line=line)
            if result is None:
                continue

            current_read, _last_read = time(), last_read
            if current_read - _last_read < host.interval:
                continue

            last_read = current_read
            await self._queue.put(result)

        logger.error(f"Ping command for host {host.host} exited with rc={proc.returncode}")

    async def run(self, hosts: List[PingHost]):
        await asyncio.gather(*[self._ping_host(host) for host in hosts])
