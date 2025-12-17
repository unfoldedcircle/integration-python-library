"""
Voice streaming primitives.

- VoiceStreamHandler: public callable type for handling a voice session
- VoiceSession: async iterator over audio frames for a single session

:copyright: (c) 2025 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import asyncio
import logging
from asyncio import AbstractEventLoop
from enum import Enum, auto
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

from .api_definitions import AssistantEvent
from .voice_assistant import AudioConfiguration

_LOG = logging.getLogger(__name__)


VoiceSessionKey = tuple[Any, int]
"""Tuple of (websocket, session_id)"""

VoiceStreamHandler = Callable[["VoiceSession"], Optional[Awaitable[None]]]
"""Public type alias for the handler callable.

Accepts a VoiceSession and may be sync or async. The handler is invoked once per voice
stream session.
"""


class VoiceEndReason(Enum):
    """Reasons for ending a voice session."""

    NORMAL = auto()
    """Normal session end."""
    TIMEOUT = auto()
    """Closed due to timeout."""
    REMOTE = auto()
    """Closed remotely, for example by the client disconnecting."""
    LOCAL = auto()
    """Closed locally in integration, for example by a new session request."""
    ERROR = auto()
    """Closed due to an error."""


class VoiceSessionClosed(Exception):
    """Base class for voice session-related exceptions."""

    def __init__(self, reason: VoiceEndReason, error: Exception | None = None):
        """Create a voice session-related exception instance."""
        super().__init__(str(reason))
        self.reason = reason
        self.error = error


class VoiceSessionTimeout(VoiceSessionClosed):
    """Raised when a voice session times out."""


class VoiceSessionRemoteEnd(VoiceSessionClosed):
    """Raised when a voice session ends remotely."""


class VoiceSessionLocalEnd(VoiceSessionClosed):
    """Raised when a voice session ends locally."""


class VoiceSessionError(VoiceSessionClosed):
    """Raised when a voice session ends due to an error."""


class _EndSignal:
    def __init__(self, reason: VoiceEndReason, error: Exception | None = None):
        self.reason = reason
        self.error = error


class VoiceSession:
    """Represents a single remote voice capture session.

    - Provides an async iterator over incoming audio frames (bytes).
    - The session is finished when the iterator completes (sentinel None fed).
    - Frames are delivered over a bounded asyncio.Queue to avoid unbounded memory.
    """

    def __init__(
        self,
        session_id: int,
        entity_id: str,
        config: AudioConfiguration,
        *,
        api,
        websocket,
        loop: AbstractEventLoop,
        max_queue: int = 32,
    ) -> None:
        """Create a voice session instance."""
        self.session_id = session_id
        self.entity_id = entity_id
        self.config = config
        self.ended_by: VoiceEndReason | None = None
        self.end_error: Exception | None = None
        self._api = api
        self._websocket = websocket
        self._loop = loop
        self._q: asyncio.Queue[bytes | _EndSignal] = asyncio.Queue(maxsize=max_queue)
        self._closed = False
        self._drops_logged = 0

    def __aiter__(self) -> AsyncIterator[bytes]:
        """Return an async iterator over audio frames."""
        return self.frames()

    @property
    def key(self) -> VoiceSessionKey:
        """Return the session key to uniquely identify a session."""
        return self._websocket, self.session_id

    async def send_event(self, event: AssistantEvent):
        """Send an assistant event to the session initiator client."""
        await self._api.send_assistant_event(self._websocket, event)

    async def frames(self) -> AsyncIterator[bytes]:
        """
        Asynchronous generator that yields frames of data from an internal queue.

        This method continuously retrieves items from an internal asynchronous queue
        and yields them one by one. When a `None` item is retrieved, it marks the
        generator as closed and exits.

        :yield: Bytes : The next frame of data retrieved from the queue.
        :rtype: AsyncIterator[bytes]
        :raises VoiceSessionTimeout: If the session times out.
        :raises VoiceSessionRemoteEnd: If the session ends remotely.
        :raises VoiceSessionLocalEnd: If the session ends locally.
        :raises VoiceSessionError: If the session ends due to an error.
        """
        while True:
            item = await self._q.get()
            if isinstance(item, _EndSignal):
                self._closed = True
                self.ended_by = item.reason
                self.end_error = item.error
                if item.reason is VoiceEndReason.NORMAL:
                    return  # StopAsyncIteration
                if item.reason is VoiceEndReason.TIMEOUT:
                    raise VoiceSessionTimeout(item.reason)
                if item.reason is VoiceEndReason.REMOTE:
                    raise VoiceSessionRemoteEnd(item.reason)
                if item.reason is VoiceEndReason.LOCAL:
                    raise VoiceSessionLocalEnd(item.reason)
                raise VoiceSessionError(item.reason, item.error)
            yield item  # bytes

    def feed(self, chunk: bytes) -> None:
        """Feed an audio chunk into the session.

        If the queue is full, the chunk is dropped to handle backpressure,
        and a debug log is emitted (throttled).

        :param chunk: Audio data bytes.
        """
        try:
            if self._closed:
                return
            self._q.put_nowait(chunk)
        except asyncio.QueueFull:
            # Drop newest if consumer lags; throttle debug logging.
            if self._drops_logged == 0 or self._drops_logged % 100 == 0:
                _LOG.debug(
                    "VoiceSession %s: dropping audio chunk due to backpressure",
                    self.session_id,
                )
            self._drops_logged += 1

    def end(
        self,
        reason: VoiceEndReason = VoiceEndReason.NORMAL,
        error: Exception | None = None,
    ) -> None:
        """
        Signal the end of the voice session.

        Enqueues a sentinel (_EndSignal) to stop the consumer iterator.
        If the queue is full, attempts to make space for the sentinel.
        """
        if self._closed:
            return
        try:
            self._q.put_nowait(_EndSignal(reason, error))
        except asyncio.QueueFull:
            # Clear one and try to enqueue sentinel
            try:
                _ = self._q.get_nowait()
                self._q.put_nowait(_EndSignal(reason, error))
            except Exception:  # pylint: disable=W0718
                # _should_ not happen, but just in case
                pass
        finally:
            self._closed = True

    @property
    def closed(self) -> bool:
        """Return True if the session has ended."""
        return self._closed
