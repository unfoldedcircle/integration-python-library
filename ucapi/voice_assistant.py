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

from ucapi.api_definitions import CommandHandler
from ucapi.entity import Entity, EntityTypes


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

    I16 = "i16"
    """Signed 16 bit."""

    I32 = "i32"
    """Signed 32 bit."""

    U16 = "u16"
    """Unsigned 16 bit."""

    U32 = "u32"
    """Unsigned 32 bit."""

    F32 = "f32"
    """Float 32 bit."""


@dataclass(slots=True)
class AudioConfiguration:
    """Audio stream specification.

    - Number of audio channels. Default: 1
    - Audio sample rate in Hz. This should be one of the commonly used sample
      rates: 8000, 11025, 16000, 22050, 24000, 44100. Other sample rates might
      not be supported.
    - Audio sample format.
    """

    channels: int = 1
    """Number of audio channels. Default: 1."""

    sample_rate: int = 16000
    """Audio sample rate in Hz (commonly 16000 by default for voice use cases)."""

    sample_format: SampleFormat = SampleFormat.I16
    """Audio sample format."""


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
