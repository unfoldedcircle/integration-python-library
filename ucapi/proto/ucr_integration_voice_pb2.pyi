from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SampleFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SAMPLE_FORMAT_UNKNOWN: _ClassVar[SampleFormat]
    I8: _ClassVar[SampleFormat]
    I16: _ClassVar[SampleFormat]
    I32: _ClassVar[SampleFormat]
    U8: _ClassVar[SampleFormat]
    U16: _ClassVar[SampleFormat]
    U32: _ClassVar[SampleFormat]
    F32: _ClassVar[SampleFormat]

class AudioFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUDIO_FORMAT_UNKNOWN: _ClassVar[AudioFormat]
    PCM: _ClassVar[AudioFormat]
SAMPLE_FORMAT_UNKNOWN: SampleFormat
I8: SampleFormat
I16: SampleFormat
I32: SampleFormat
U8: SampleFormat
U16: SampleFormat
U32: SampleFormat
F32: SampleFormat
AUDIO_FORMAT_UNKNOWN: AudioFormat
PCM: AudioFormat

class IntegrationMessage(_message.Message):
    __slots__ = ("voice_begin", "voice_data", "voice_end")
    VOICE_BEGIN_FIELD_NUMBER: _ClassVar[int]
    VOICE_DATA_FIELD_NUMBER: _ClassVar[int]
    VOICE_END_FIELD_NUMBER: _ClassVar[int]
    voice_begin: RemoteVoiceBegin
    voice_data: RemoteVoiceData
    voice_end: RemoteVoiceEnd
    def __init__(self, voice_begin: _Optional[_Union[RemoteVoiceBegin, _Mapping]] = ..., voice_data: _Optional[_Union[RemoteVoiceData, _Mapping]] = ..., voice_end: _Optional[_Union[RemoteVoiceEnd, _Mapping]] = ...) -> None: ...

class AudioConfiguration(_message.Message):
    __slots__ = ("channels", "sample_rate", "sample_format", "format")
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    channels: int
    sample_rate: int
    sample_format: SampleFormat
    format: AudioFormat
    def __init__(self, channels: _Optional[int] = ..., sample_rate: _Optional[int] = ..., sample_format: _Optional[_Union[SampleFormat, str]] = ..., format: _Optional[_Union[AudioFormat, str]] = ...) -> None: ...

class RemoteVoiceBegin(_message.Message):
    __slots__ = ("session_id", "configuration")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    session_id: int
    configuration: AudioConfiguration
    def __init__(self, session_id: _Optional[int] = ..., configuration: _Optional[_Union[AudioConfiguration, _Mapping]] = ...) -> None: ...

class RemoteVoiceData(_message.Message):
    __slots__ = ("session_id", "samples")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    session_id: int
    samples: bytes
    def __init__(self, session_id: _Optional[int] = ..., samples: _Optional[bytes] = ...) -> None: ...

class RemoteVoiceEnd(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: int
    def __init__(self, session_id: _Optional[int] = ...) -> None: ...
