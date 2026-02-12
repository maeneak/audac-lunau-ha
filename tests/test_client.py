from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from custom_components.audac_luna_u import client as client_module
from custom_components.audac_luna_u.client import (
    LunaMessage,
    LunaUClient,
    build_message,
    parse_message,
)


class DummyWriter:
    def __init__(self) -> None:
        self.closed = False
        self.buffer = b""

    def is_closing(self) -> bool:
        return self.closed

    def write(self, data: bytes) -> None:
        self.buffer += data

    async def drain(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


class DummyReader:
    def __init__(self, lines: list[bytes]) -> None:
        self._lines = lines

    async def readline(self) -> bytes:
        if self._lines:
            return self._lines.pop(0)
        return b""


def test_build_message() -> None:
    assert (
        build_message("LUNA_U>1", "CLIENT>1", "GET_REQ", "ALL_ZONES", "VOLUME")
        == "#|LUNA_U>1|CLIENT>1|GET_REQ^ALL_ZONES^VOLUME||U|"
    )


def test_parse_message_valid() -> None:
    msg = parse_message("#|LUNA_U>1|CLIENT>1|GET_RSP^ALL_ZONES^VOLUME|-10^-9|U|")
    assert msg is not None
    assert msg.msg_type == "GET_RSP"
    assert msg.target == "ALL_ZONES"
    assert msg.command == "VOLUME"
    assert msg.arguments == "-10^-9"


def test_parse_message_invalid() -> None:
    assert parse_message("") is None
    assert parse_message("#|broken|message|") is None


@pytest.mark.asyncio
async def test_connect_unlocked_noop_when_already_connected() -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    client._writer = DummyWriter()
    client._connected.set()
    await client._connect_unlocked()
    assert client.connected is True


@pytest.mark.asyncio
async def test_connect_unlocked_creates_reader_task(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    dummy_reader = DummyReader([])
    dummy_writer = DummyWriter()

    async def fake_open_connection(*_args, **_kwargs):
        return dummy_reader, dummy_writer

    monkeypatch.setattr(client_module.asyncio, "open_connection", fake_open_connection)

    task = asyncio.create_task(asyncio.sleep(0))

    def fake_create_task(coro):
        coro.close()
        return task

    monkeypatch.setattr(client_module.asyncio, "create_task", fake_create_task)

    await client._connect_unlocked()
    assert client.connected is True
    assert client._reader is dummy_reader
    assert client._writer is dummy_writer
    task.cancel()


@pytest.mark.asyncio
async def test_close_unlocked_cleans_resources() -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    client._connected.set()
    client._writer = DummyWriter()
    client._read_task = asyncio.create_task(asyncio.sleep(1))
    await client._close_unlocked()
    assert client.connected is False
    assert client._reader is None
    assert client._writer is None
    assert client._read_task is None


@pytest.mark.asyncio
async def test_ensure_connected_retries_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    attempts = 0

    async def fake_connect_unlocked() -> None:
        nonlocal attempts
        attempts += 1
        raise OSError("device offline")

    async def fake_close_unlocked() -> None:
        return None

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(client, "_connect_unlocked", fake_connect_unlocked)
    monkeypatch.setattr(client, "_close_unlocked", fake_close_unlocked)
    monkeypatch.setattr(client_module.asyncio, "sleep", fake_sleep)

    with pytest.raises(ConnectionError, match="after 5 attempts"):
        await client.ensure_connected()

    assert attempts == client.MAX_RECONNECT_ATTEMPTS


@pytest.mark.asyncio
async def test_ensure_connected_succeeds_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    attempts = 0

    async def fake_connect_unlocked() -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise OSError("offline")
        client._connected.set()

    async def fake_close_unlocked() -> None:
        return None

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(client, "_connect_unlocked", fake_connect_unlocked)
    monkeypatch.setattr(client, "_close_unlocked", fake_close_unlocked)
    monkeypatch.setattr(client_module.asyncio, "sleep", fake_sleep)

    await client.ensure_connected()
    assert client.connected is True
    assert attempts == 3


@pytest.mark.asyncio
async def test_reader_loop_with_none_reader() -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    await client._reader_loop()
    assert client.connected is False


@pytest.mark.asyncio
async def test_reader_loop_dispatches_and_fails_pending() -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    lines = [
        b"\x00\x01#|LUNA_U>1|CLIENT>1|GET_RSP^ALL_ZONES^VOLUME|-10|U|\r\n",
        b"binary-only\r\n",
        b"#|broken|message|\r\n",
        b"",
    ]
    client._reader = DummyReader(lines)
    dispatched: list[LunaMessage] = []
    original_dispatch = client._dispatch_message

    def wrapped_dispatch(msg: LunaMessage) -> None:
        dispatched.append(msg)
        original_dispatch(msg)

    client._dispatch_message = wrapped_dispatch  # type: ignore[method-assign]
    loop = asyncio.get_running_loop()
    matched_fut = loop.create_future()
    stale_fut = loop.create_future()
    client._pending.append(("GET_RSP", "ALL_ZONES", "VOLUME", matched_fut))
    client._pending.append(("GET_RSP", "ALL_ZONES", "MUTE", stale_fut))

    await client._reader_loop()

    assert dispatched
    assert matched_fut.done()
    assert matched_fut.result().command == "VOLUME"
    assert stale_fut.done()
    assert isinstance(stale_fut.exception(), ConnectionError)


@pytest.mark.asyncio
async def test_dispatch_message_and_listeners() -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    fut = asyncio.get_running_loop().create_future()
    client._pending.append(("GET_RSP", "ALL_ZONES", "VOLUME", fut))
    seen: list[LunaMessage] = []

    def ok_listener(msg: LunaMessage) -> None:
        seen.append(msg)

    def bad_listener(_msg: LunaMessage) -> None:
        raise RuntimeError("boom")

    client.add_listener(ok_listener)
    client.add_listener(bad_listener)
    msg = LunaMessage("", "", "GET_RSP", "ALL_ZONES", "VOLUME", "-10", "U")
    client._dispatch_message(msg)

    assert fut.done() and fut.result() == msg
    assert seen and seen[0] == msg

    client.remove_listener(bad_listener)
    client.remove_listener(lambda _m: None)


@pytest.mark.asyncio
async def test_send_not_connected_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())
    client._writer = None
    with pytest.raises(ConnectionError, match="Not connected"):
        await client._send("payload")


@pytest.mark.asyncio
async def test_send_writes_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    writer = DummyWriter()
    client._writer = writer
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())
    await client._send("payload")
    assert writer.buffer == b"payload\r\n"


@pytest.mark.asyncio
async def test_request_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())

    async def fake_send(_payload: str) -> None:
        client._dispatch_message(LunaMessage("", "", "GET_RSP", "ALL_ZONES", "VOLUME", "-20", "U"))

    monkeypatch.setattr(client, "_send", fake_send)
    msg = await client.request("GET_REQ", "ALL_ZONES", "VOLUME")
    assert msg.arguments == "-20"
    assert len(client._pending) == 0


@pytest.mark.asyncio
async def test_request_too_many_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())
    loop = asyncio.get_running_loop()
    for _ in range(client.MAX_PENDING):
        client._pending.append(("GET_RSP", "A", "B", loop.create_future()))

    with pytest.raises(ConnectionError, match="Too many pending requests"):
        await client.request("GET_REQ", "ALL_ZONES", "VOLUME")


@pytest.mark.asyncio
async def test_request_timeout_cleans_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())
    monkeypatch.setattr(client, "_send", AsyncMock())

    async def fake_wait_for(_fut, timeout=None):
        raise asyncio.TimeoutError

    monkeypatch.setattr(client_module.asyncio, "wait_for", fake_wait_for)

    with pytest.raises(asyncio.TimeoutError):
        await client.request("GET_REQ", "ALL_ZONES", "VOLUME")
    assert len(client._pending) == 0


@pytest.mark.asyncio
async def test_get_value_timeout_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)

    async def fake_request(*_args, **_kwargs):
        raise asyncio.TimeoutError

    monkeypatch.setattr(client, "request", fake_request)
    assert await client.get_value("ALL_ZONES", "VOLUME") is None


@pytest.mark.asyncio
async def test_set_value_wait_for_response(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    expected = LunaMessage("", "", "GET_RSP", "T", "C", "1", "U")
    monkeypatch.setattr(client, "request", AsyncMock(return_value=expected))

    result = await client.set_value("T", "C", "1", wait_for_response=True)
    assert result == expected


@pytest.mark.asyncio
async def test_set_value_fire_and_forget(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LunaUClient("127.0.0.1", 5001, 1)
    monkeypatch.setattr(client, "ensure_connected", AsyncMock())
    send = AsyncMock()
    monkeypatch.setattr(client, "_send", send)

    result = await client.set_value("T", "C", "1", wait_for_response=False)
    assert result is None
    send.assert_awaited_once()
