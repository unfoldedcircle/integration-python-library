"""
Voice Assistant entity definitions.

This entity enables the Remote to initiate a voice stream from the microphone that is
streamed to the integration as binary WebSocket messages encoded with protobuf
(`IntegrationMessage`). The JSON command only initiates the stream; audio
frames are delivered on the binary channel and handled by IntegrationAPI.

:copyright: (c) 2025 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional

from .api_definitions import CommandHandler
from .entity import Entity, EntityTypes

# Import specific enum constants to avoid pylint no-member on dynamic attributes
from .proto.ucr_integration_voice_pb2 import (  # pylint: disable=no-name-in-module # isort:skip # noqa
    F32 as PB_F32,
    I16 as PB_I16,
    I32 as PB_I32,
    U16 as PB_U16,
    U32 as PB_U32,
)

DEFAULT_AUDIO_CHANNELS = 1
DEFAULT_SAMPLE_RATE = 16000


class States(str, Enum):
    """Voice Assistant entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class Features(str, Enum):
    """Voice Assistant features."""

    TRANSCRIPTION = "transcription"
    """Voice command is transcribed and sent back to the Remote in the
    AssistantEvent::SttResponse event.
    """

    RESPONSE_TEXT = "response_text"
    """Textual response about the performed action with the
    AssistantEvent::TextResponse event.
    """

    RESPONSE_SPEECH = "response_speech"
    """Speech response about the performed action with the
    AssistantEvent::SpeechResponse event.
    """


class Attributes(str, Enum):
    """Voice Assistant entity attributes."""

    STATE = "state"


class Commands(str, Enum):
    """Integration-API Voice Assistant entity commands."""

    VOICE_START = "voice_start"
    """Request to start sending a voice command audio stream to the integration.

    After confirming the command, the audio stream is started and transmitted
    as binary WebSocket messages in protocol buffer format.
    """


class Options(str, Enum):
    """Voice Assistant entity option fields."""

    AUDIO_CFG = "audio_cfg"
    PROFILES = "profiles"
    PREFERRED_PROFILE = "preferred_profile"


# ---------------------------------------------------------------------------
# Data models for options
# ---------------------------------------------------------------------------
class SampleFormat(str, Enum):
    """Audio format specification."""

    I16 = "I16"
    """Signed 16 bit."""

    I32 = "I32"
    """Signed 32 bit."""

    U16 = "U16"
    """Unsigned 16 bit."""

    U32 = "U32"
    """Unsigned 32 bit."""

    F32 = "F32"
    """Float 32 bit."""

    @classmethod
    def from_proto(cls, value: Any) -> Optional["SampleFormat"]:
        """Convert protobuf enum ``SampleFormat`` to Python enum.

        Returns ``None`` when the value is unknown or not available in this
        Python enum (e.g., ``SAMPLE_FORMAT_UNKNOWN``, ``I8``, ``U8``).

        Accepts the following inputs:
        - Protobuf enum value (``pb2.SampleFormat``)
        - Integer value of the protobuf enum
        - String value (e.g., "I16", "U32")
        - ``None``
        """
        if value is None:
            return None

        # Map protobuf values (or their ints) to our Python enum
        mapping: dict[int, SampleFormat] = {
            int(PB_I16): cls.I16,
            int(PB_I32): cls.I32,
            int(PB_U16): cls.U16,
            int(PB_U32): cls.U32,
            int(PB_F32): cls.F32,
        }

        if isinstance(value, int):
            return mapping.get(int(value))

        if isinstance(value, str):
            key = value.strip().upper()
            # Only map to values that exist in this Python enum
            try:
                return cls[key]
            except KeyError:
                return None

        # Fallback for enum-like types (protobuf enum wrappers behave like ints)
        try:
            return mapping.get(int(value))
        except (TypeError, ValueError):
            return None


DEFAULT_SAMPLE_FORMAT = SampleFormat.I16


@dataclass(slots=True)
class AudioConfiguration:
    """Audio stream specification.

    - Number of audio channels. Default: 1
    - Audio sample rate in Hz. This should be one of the commonly used sample
      rates: 8000, 11025, 16000, 22050, 24000, 44100. Other sample rates might
      not be supported.
    - Audio sample format.
    """

    channels: int = DEFAULT_AUDIO_CHANNELS
    """Number of audio channels. Default: 1."""

    sample_rate: int = DEFAULT_SAMPLE_RATE
    """Audio sample rate in Hz (commonly 16000 by default for voice use cases)."""

    sample_format: SampleFormat = DEFAULT_SAMPLE_FORMAT
    """Audio sample format."""

    @staticmethod
    def _to_int(value: Any, default: int) -> int:
        """Best-effort conversion to ``int`` with a sensible default.

        Accepts ``int``/``str``/``None`` and returns ``default`` if conversion
        fails or value is falsy.
        """
        if value is None:
            return default
        try:
            if isinstance(value, bool):  # avoid bool being a subclass of int
                return default
            if isinstance(value, (int,)):
                return int(value) or default
            if isinstance(value, str):
                s = value.strip()
                return int(s) if s else default
        except (TypeError, ValueError):
            return default
        return default

    @classmethod
    def from_proto(cls, value: Any) -> Optional["AudioConfiguration"]:
        """Convert protobuf ``AudioConfiguration`` (or mapping) to Python model.

        - ``None`` returns ``None``
        - Protobuf message: reads fields and converts types
        - ``dict``/``mapping``: accepts keys ``channels``, ``sample_rate``,
          ``sample_format`` (strings/ints acceptable)

        The protobuf field ``format`` (``AudioFormat``) is currently ignored in
        the Python model.
        """
        if value is None:
            return None

        # Extract raw field values from either a proto message or a dict-like
        if (
            hasattr(value, "__class__")
            and value.__class__.__name__ == "AudioConfiguration"
        ):
            # Likely a protobuf message instance
            ch = getattr(value, "channels", DEFAULT_AUDIO_CHANNELS)
            sr = getattr(value, "sample_rate", DEFAULT_SAMPLE_RATE)
            sf = getattr(value, "sample_format", None)
        elif isinstance(value, dict):
            ch = value.get("channels", DEFAULT_AUDIO_CHANNELS)
            sr = value.get("sample_rate", DEFAULT_SAMPLE_RATE)
            sf = value.get("sample_format", None)
        else:
            # Unsupported type
            return None

        channels = cls._to_int(ch, DEFAULT_AUDIO_CHANNELS)
        sample_rate = cls._to_int(sr, DEFAULT_SAMPLE_RATE)
        sample_format = SampleFormat.from_proto(sf) or DEFAULT_SAMPLE_FORMAT

        return cls(
            channels=channels,
            sample_rate=sample_rate,
            sample_format=sample_format,
        )


@dataclass(slots=True)
class VoiceAssistantProfile:
    """Voice Assistant profile.

    Represents one selectable profile, e.g., a language-specific recognition
    profile.
    """

    id: str
    """Profile identifier."""

    name: str
    """Friendly name to show in UI."""

    language: Optional[str] = None
    """Optional language code if the profile represents a specific language for
    speech recognition.
    """

    transcription: Optional[bool] = None
    """Supports voice command transcription. Entity feature is used if not
    specified.
    """

    response_text: Optional[bool] = None
    """Supports textual response about the performed action. Entity feature is
    used if not specified.
    """

    response_speech: Optional[bool] = None
    """Supports speech response about the performed action. Entity feature is
    used if not specified.
    """


@dataclass(slots=True)
class VoiceAssistantEntityOptions:
    """Voice Assistant entity options."""

    audio_cfg: Optional[AudioConfiguration] = None
    """Audio stream specification."""

    profiles: Optional[list[VoiceAssistantProfile]] = field(default=None)
    """Available profiles."""

    preferred_profile: Optional[str] = None
    """Preferred profile identifier."""


class VoiceAssistant(Entity):
    """
    Voice Assistant entity class.

    See docs for more information:
    <https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_voice_assistant.md>
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        features: list[Features],
        attributes: dict[str, Any],
        options: dict[str, Any] | VoiceAssistantEntityOptions | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ) -> None:
        """Create a voice-assistant entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: voice assistant features
        :param attributes: voice assistant attributes
        :param options: voice assistant options
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.VOICE_ASSISTANT,
            [f.value if isinstance(f, Enum) else f for f in features],
            attributes,
            options=(
                options
                if isinstance(options, dict)
                else (None if options is None else asdict(options))
            ),
            area=area,
            cmd_handler=cmd_handler,
        )
