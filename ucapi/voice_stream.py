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
from typing import AsyncIterator, Awaitable, Callable, Optional

from ucapi.voice_assistant import AudioConfiguration

_LOG = logging.getLogger(__name__)


VoiceStreamHandler = Callable[["VoiceSession"], Optional[Awaitable[None]]]
"""Public type alias for the handler callable.

Accepts a VoiceSession and may be sync or async. The handler is invoked once per voice
stream session.
"""


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
        loop: AbstractEventLoop,
        max_queue: int = 32,
    ) -> None:
        """Create a voice session instance."""
        self.session_id = session_id
        self.entity_id = entity_id
        self.config = config
        self._loop = loop
        self._q: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=max_queue)
        self._closed = False
        self._drops_logged = 0

    def __aiter__(self) -> AsyncIterator[bytes]:
        """Return an async iterator over audio frames."""
        return self.frames()

    async def frames(self) -> AsyncIterator[bytes]:
        """
        Asynchronous generator that yields frames of data from an internal queue.

        This method continuously retrieves items from an internal asynchronous queue
        and yields them one by one. When a `None` item is retrieved, it marks the
        generator as closed and exits.

        :yield: Bytes : The next frame of data retrieved from the queue.
        :rtype: AsyncIterator[bytes]
        """
        while True:
            item = await self._q.get()
            if item is None:
                self._closed = True
                return
            yield item

    def feed(self, chunk: bytes) -> None:
        """Feed an audio chunk into the session.

        If the queue is full, the chunk is dropped to handle backpressure,
        and a debug log is emitted (throttled).

        :param chunk: Audio data bytes.
        """
        try:
            self._q.put_nowait(chunk)
        except asyncio.QueueFull:
            # Drop newest if consumer lags; throttle debug logging.
            if self._drops_logged == 0 or self._drops_logged % 100 == 0:
                _LOG.debug(
                    "VoiceSession %s: dropping audio chunk due to backpressure",
                    self.session_id,
                )
            self._drops_logged += 1

    def end(self) -> None:
        """
        Signal the end of the voice session.

        Enqueues a sentinel (None) to stop the consumer iterator.
        If the queue is full, attempts to make space for the sentinel.
        """
        if not self._closed:
            try:
                self._q.put_nowait(None)
            except asyncio.QueueFull:
                # Clear one and try to enqueue sentinel
                try:
                    _ = self._q.get_nowait()
                    self._q.put_nowait(None)
                except Exception:  # pylint: disable=W0718
                    self._closed = True

    @property
    def closed(self) -> bool:
        """Return True if the session has ended."""
        return self._closed
