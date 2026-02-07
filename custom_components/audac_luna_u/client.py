"""Protocol client for the Audac Luna-U ASCII control interface."""
from __future__ import annotations

from dataclasses import dataclass
import asyncio
import logging
from typing import Callable
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


def parse_message(line: str) -> LunaMessage | None:
    raw = line.strip()
    if not raw:
        _LOGGER.debug("parse_message: empty input")
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
        _LOGGER.debug("parse_message: insufficient parts (%d), expected 5+ in: %s", len(parts), raw)
        return None

    destination, source, type_block, arguments, crc = parts[:5]
    type_parts = type_block.split("^")
    msg_type = type_parts[0] if len(type_parts) > 0 else ""
    target = type_parts[1] if len(type_parts) > 1 else ""
    command = type_parts[2] if len(type_parts) > 2 else ""

    _LOGGER.debug(
        "parse_message: dst=%s src=%s type=%s target=%s cmd=%s args=%s",
        destination, source, msg_type, target, command, arguments
    )

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

    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_BASE_DELAY = 1.0
    CONNECTION_TIMEOUT = 10.0
    MAX_PENDING = 50

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
        self._pending: deque[tuple[str, str, str, asyncio.Future]] = deque()
        self._listeners: list[Callable[[LunaMessage], None]] = []
        self._connected = asyncio.Event()

    @property
    def destination(self) -> str:
        return f"LUNA_U>{self._address}"

    @property
    def source(self) -> str:
        return f"CLIENT>{self._source_id}"

    @property
    def connected(self) -> bool:
        """Return whether the client is currently connected."""
        return self._connected.is_set()

    async def _connect_unlocked(self) -> None:
        """Internal connect without lock. Caller must hold _connect_lock."""
        if self._writer and not self._writer.is_closing() and self._connected.is_set():
            return
        # Cancel any stale reader task before creating a new one
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            self._read_task = None
        _LOGGER.debug("Connecting to Luna-U at %s:%s", self._host, self._port)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self._host, self._port),
            timeout=self.CONNECTION_TIMEOUT,
        )
        self._connected.set()
        self._read_task = asyncio.create_task(self._reader_loop())
        _LOGGER.info("Connected to Luna-U at %s:%s", self._host, self._port)

    async def connect(self) -> None:
        """Connect to the Luna-U device."""
        async with self._connect_lock:
            await self._connect_unlocked()

    async def ensure_connected(self) -> None:
        """Ensure connection with automatic reconnection on failure."""
        if self._connected.is_set():
            return
        _LOGGER.debug("Connection lost, attempting to reconnect to %s:%s", self._host, self._port)
        async with self._connect_lock:
            # Re-check after acquiring lock — another coroutine may have reconnected
            if self._connected.is_set():
                return
            # Clean up any stale connection resources before reconnecting
            await self._close_unlocked()
            for attempt in range(self.MAX_RECONNECT_ATTEMPTS):
                try:
                    await self._connect_unlocked()
                    return
                except Exception as exc:
                    delay = self.RECONNECT_BASE_DELAY * (2 ** attempt)
                    _LOGGER.warning(
                        "Connection attempt %d/%d failed: %s. Retrying in %.1fs",
                        attempt + 1, self.MAX_RECONNECT_ATTEMPTS, exc, delay,
                    )
                    if attempt < self.MAX_RECONNECT_ATTEMPTS - 1:
                        await asyncio.sleep(delay)
            raise ConnectionError(
                f"Failed to connect to Luna-U at {self._host}:{self._port} "
                f"after {self.MAX_RECONNECT_ATTEMPTS} attempts"
            )

    async def _close_unlocked(self) -> None:
        """Internal close without lock. Caller must hold _connect_lock."""
        _LOGGER.debug("Closing connection to %s:%s", self._host, self._port)
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
        _LOGGER.debug("Connection closed")

    async def close(self) -> None:
        """Close the connection."""
        async with self._connect_lock:
            await self._close_unlocked()

    async def _reader_loop(self) -> None:
        _LOGGER.debug("Reader loop started")
        try:
            if self._reader is None:
                _LOGGER.warning("Reader loop started but reader is None")
                return
            while True:
                line = await self._reader.readline()
                if not line:
                    _LOGGER.debug("Reader received empty line, connection closed")
                    break
                # Log raw hex bytes for debugging
                hex_data = line.hex()
                _LOGGER.debug("Raw RX (hex): %s", hex_data[:200])  # First 200 chars of hex
                raw_data = line.decode(errors="ignore").strip()
                _LOGGER.debug("Raw RX (text): %s", raw_data[:200])  # First 200 chars of text
                try:
                    msg = parse_message(raw_data)
                except Exception as exc:  # pragma: no cover - defensive
                    _LOGGER.debug("Failed to parse message '%s': %s", raw_data, exc)
                    continue
                if not msg:
                    _LOGGER.debug("parse_message returned None for: %s", raw_data)
                    continue
                self._dispatch_message(msg)
        except asyncio.CancelledError:
            _LOGGER.debug("Reader loop cancelled")
            return
        except Exception as exc:  # pragma: no cover - defensive
            _LOGGER.debug("Reader loop error: %s", exc, exc_info=True)
        finally:
            _LOGGER.debug("Reader loop exiting, clearing connection state")
            self._connected.clear()
            # Fail pending futures
            pending_count = len(self._pending)
            if pending_count > 0:
                _LOGGER.debug("Failing %d pending request(s)", pending_count)
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
            matched: tuple[str, str, str, asyncio.Future] | None = None
            for pending in self._pending:
                expect_type, expect_target, expect_command, fut = pending
                if (
                    expect_type == msg.msg_type
                    and expect_target == msg.target
                    and expect_command == msg.command
                ):
                    matched = pending
                    break
            if matched is not None:
                _LOGGER.debug(
                    "Matched pending request: target=%s cmd=%s",
                    msg.target, msg.command
                )
                self._pending.remove(matched)
                if not matched[3].done():
                    matched[3].set_result(msg)
            else:
                _LOGGER.debug(
                    "No pending request matched response: target=%s cmd=%s (pending count: %d)",
                    msg.target, msg.command, len(self._pending)
                )
        for listener in self._listeners:
            try:
                listener(msg)
            except Exception:  # pragma: no cover - defensive
                _LOGGER.warning("Listener error", exc_info=True)

    def add_listener(self, cb: Callable[[LunaMessage], None]) -> None:
        self._listeners.append(cb)

    def remove_listener(self, cb: Callable[[LunaMessage], None]) -> None:
        """Remove a message listener."""
        if cb in self._listeners:
            self._listeners.remove(cb)

    async def _send(self, payload: str) -> None:
        """Send a command payload to the device."""
        await self.ensure_connected()
        if not self._writer or self._writer.is_closing():
            raise ConnectionError("Not connected")
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
        if len(self._pending) >= self.MAX_PENDING:
            _LOGGER.warning("Too many pending requests (%d)", len(self._pending))
            raise ConnectionError("Too many pending requests")
        payload = build_message(self.destination, self.source, msg_type, target, command, arguments)
        fut = asyncio.get_running_loop().create_future()
        # Per protocol spec, device always responds with GET_RSP for both GET_REQ and SET_REQ
        pending = ("GET_RSP", target, command, fut)
        self._pending.append(pending)
        _LOGGER.debug(
            "Queued request: type=%s target=%s cmd=%s args=%s (pending: %d)",
            msg_type, target, command, arguments, len(self._pending)
        )
        try:
            await self._send(payload)
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            _LOGGER.debug(
                "Request timed out after %.1fs: type=%s target=%s cmd=%s",
                timeout, msg_type, target, command
            )
            raise
        except Exception as exc:
            _LOGGER.debug(
                "Request failed: type=%s target=%s cmd=%s - %s",
                msg_type, target, command, exc
            )
            raise
        finally:
            if pending in self._pending:
                self._pending.remove(pending)
            if not fut.done():
                fut.cancel()

    async def get_value(self, target: str, command: str, timeout: float = 2.5) -> LunaMessage | None:
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
    ) -> LunaMessage | None:
        """Set a value on the device."""
        if wait_for_response:
            return await self.request("SET_REQ", target, command, arguments, timeout=timeout)
        await self.ensure_connected()
        payload = build_message(self.destination, self.source, "SET_REQ", target, command, arguments)
        await self._send(payload)
        return None
