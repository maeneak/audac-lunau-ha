"""Protocol client for the Audac Luna-U ASCII control interface."""
from __future__ import annotations

from dataclasses import dataclass
import asyncio
import logging
from typing import Callable, Deque, Optional
from collections import deque

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class LunaMessage:
    destination: str
    source: str
    msg_type: str
    target: str
    command: str
    arguments: str
    crc: str


def build_message(
    destination: str,
    source: str,
    msg_type: str,
    target: str,
    command: str,
    arguments: str = "",
    crc: str = "U",
) -> str:
    type_block = f"{msg_type}^{target}^{command}"
    return f"#|{destination}|{source}|{type_block}|{arguments}|{crc}|"


def parse_message(line: str) -> Optional[LunaMessage]:
    raw = line.strip()
    if not raw:
        return None
    if raw.startswith("#"):
        raw = raw[1:]
    raw = raw.strip("\r\n")
    if raw.endswith("|"):
        raw = raw[:-1]

    parts = raw.split("|")
    if parts and parts[0] == "":
        parts = parts[1:]
    if len(parts) < 5:
        return None

    destination, source, type_block, arguments, crc = parts[:5]
    type_parts = type_block.split("^")
    msg_type = type_parts[0] if len(type_parts) > 0 else ""
    target = type_parts[1] if len(type_parts) > 1 else ""
    command = type_parts[2] if len(type_parts) > 2 else ""

    return LunaMessage(
        destination=destination,
        source=source,
        msg_type=msg_type,
        target=target,
        command=command,
        arguments=arguments,
        crc=crc,
    )


class LunaUClient:
    """Async TCP client for Luna-U."""

    MAX_RECONNECT_ATTEMPTS = 3
    RECONNECT_BASE_DELAY = 1.0

    def __init__(self, host: str, port: int, address: int, source_id: int = 1) -> None:
        self._host = host
        self._port = port
        self._address = address
        self._source_id = source_id

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._read_task: asyncio.Task | None = None
        self._write_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()
        self._pending: Deque[tuple[str, str, str, asyncio.Future]] = deque()
        self._listeners: list[Callable[[LunaMessage], None]] = []
        self._connected = asyncio.Event()
        self._reconnecting = False

    @property
    def destination(self) -> str:
        return f"LUNA_U>{self._address}"

    @property
    def source(self) -> str:
        return f"CLIENT>{self._source_id}"

    async def connect(self) -> None:
        """Connect to the Luna-U device."""
        if self._writer and not self._writer.is_closing() and self._connected.is_set():
            return
        async with self._connect_lock:
            # Double-check after acquiring lock
            if self._writer and not self._writer.is_closing() and self._connected.is_set():
                return
            _LOGGER.debug("Connecting to Luna-U at %s:%s", self._host, self._port)
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
            self._connected.set()
            self._read_task = asyncio.create_task(self._reader_loop())
            _LOGGER.info("Connected to Luna-U at %s:%s", self._host, self._port)

    async def ensure_connected(self) -> None:
        """Ensure connection with automatic reconnection on failure."""
        if self._connected.is_set():
            return
        for attempt in range(self.MAX_RECONNECT_ATTEMPTS):
            try:
                await self.connect()
                return
            except Exception as exc:
                delay = self.RECONNECT_BASE_DELAY * (2 ** attempt)
                _LOGGER.warning(
                    "Connection attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt + 1, self.MAX_RECONNECT_ATTEMPTS, exc, delay
                )
                if attempt < self.MAX_RECONNECT_ATTEMPTS - 1:
                    await asyncio.sleep(delay)
        raise ConnectionError(
            f"Failed to connect to Luna-U at {self._host}:{self._port} "
            f"after {self.MAX_RECONNECT_ATTEMPTS} attempts"
        )

    async def close(self) -> None:
        self._connected.clear()
        if self._read_task:
            self._read_task.cancel()
            self._read_task = None
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:  # pragma: no cover - best effort cleanup
                pass
            self._writer = None
        self._reader = None

    async def _reader_loop(self) -> None:
        try:
            assert self._reader is not None
            while True:
                line = await self._reader.readline()
                if not line:
                    break
                try:
                    msg = parse_message(line.decode(errors="ignore"))
                except Exception as exc:  # pragma: no cover - defensive
                    _LOGGER.debug("Failed to parse message: %s", exc)
                    continue
                if not msg:
                    continue
                self._dispatch_message(msg)
        except asyncio.CancelledError:
            return
        except Exception as exc:  # pragma: no cover - defensive
            _LOGGER.debug("Reader loop error: %s", exc)
        finally:
            self._connected.clear()
            # Fail pending futures
            while self._pending:
                _, _, _, fut = self._pending.popleft()
                if not fut.done():
                    fut.set_exception(ConnectionError("Disconnected"))

    def _dispatch_message(self, msg: LunaMessage) -> None:
        """Dispatch a received message to pending requests and listeners."""
        _LOGGER.debug(
            "RX: type=%s target=%s cmd=%s args=%s",
            msg.msg_type, msg.target, msg.command, msg.arguments
        )
        if msg.msg_type == "GET_RSP":
            for pending in list(self._pending):
                expect_type, expect_target, expect_command, fut = pending
                if (
                    expect_type == msg.msg_type
                    and expect_target == msg.target
                    and expect_command == msg.command
                ):
                    self._pending.remove(pending)
                    if not fut.done():
                        fut.set_result(msg)
                    break
        for listener in self._listeners:
            try:
                listener(msg)
            except Exception:  # pragma: no cover - defensive
                _LOGGER.debug("Listener error", exc_info=True)

    def add_listener(self, cb: Callable[[LunaMessage], None]) -> None:
        self._listeners.append(cb)

    async def _send(self, payload: str) -> None:
        """Send a command payload to the device."""
        await self.ensure_connected()
        assert self._writer is not None
        _LOGGER.debug("TX: %s", payload)
        async with self._write_lock:
            self._writer.write((payload + "\r\n").encode())
            await self._writer.drain()

    async def request(
        self,
        msg_type: str,
        target: str,
        command: str,
        arguments: str = "",
        timeout: float = 2.5,
    ) -> LunaMessage:
        """Send a request and wait for a response."""
        await self.ensure_connected()
        payload = build_message(self.destination, self.source, msg_type, target, command, arguments)
        fut = asyncio.get_running_loop().create_future()
        pending = ("GET_RSP", target, command, fut)
        self._pending.append(pending)
        try:
            await self._send(payload)
            return await asyncio.wait_for(fut, timeout=timeout)
        except Exception:
            if pending in self._pending:
                self._pending.remove(pending)
            if not fut.done():
                fut.cancel()
            raise

    async def get_value(self, target: str, command: str, timeout: float = 2.5) -> Optional[LunaMessage]:
        try:
            return await self.request("GET_REQ", target, command, "", timeout=timeout)
        except asyncio.TimeoutError:
            _LOGGER.debug("Timeout waiting for GET_RSP %s %s", target, command)
            return None

    async def set_value(
        self,
        target: str,
        command: str,
        arguments: str,
        wait_for_response: bool = False,
        timeout: float = 2.5,
    ) -> Optional[LunaMessage]:
        """Set a value on the device."""
        await self.ensure_connected()
        payload = build_message(self.destination, self.source, "SET_REQ", target, command, arguments)
        if not wait_for_response:
            await self._send(payload)
            return None
        return await self.request("SET_REQ", target, command, arguments, timeout=timeout)
