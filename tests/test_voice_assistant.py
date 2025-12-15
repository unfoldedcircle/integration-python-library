import unittest

from ucapi.voice_assistant import (
    DEFAULT_AUDIO_CHANNELS,
    DEFAULT_SAMPLE_FORMAT,
    DEFAULT_SAMPLE_RATE,
    AudioConfiguration,
    SampleFormat,
)
from ucapi.proto import ucr_integration_voice_pb2 as pb2


class TestVoiceAssistantConversions(unittest.TestCase):
    def test_sample_format_from_proto_supported(self):
        self.assertEqual(SampleFormat.from_proto(pb2.I16), SampleFormat.I16)
        self.assertEqual(SampleFormat.from_proto(int(pb2.U32)), SampleFormat.U32)
        self.assertEqual(SampleFormat.from_proto("f32"), SampleFormat.F32)

    def test_sample_format_from_proto_unsupported_to_none(self):
        # Values that do not exist in local enum should map to None
        self.assertIsNone(SampleFormat.from_proto(pb2.I8))
        self.assertIsNone(SampleFormat.from_proto(pb2.U8))
        self.assertIsNone(SampleFormat.from_proto("i8"))
        self.assertIsNone(SampleFormat.from_proto("unknown"))

    def test_audio_cfg_from_proto_message(self):
        msg = pb2.AudioConfiguration(
            channels=2,
            sample_rate=22050,
            sample_format=pb2.I32,
            format=pb2.PCM,
        )
        cfg = AudioConfiguration.from_proto(msg)

        self.assertIsInstance(cfg, AudioConfiguration)
        self.assertEqual(cfg.channels, 2)
        self.assertEqual(cfg.sample_rate, 22050)
        self.assertEqual(cfg.sample_format, SampleFormat.I32)

    def test_audio_cfg_from_dict_and_string_coercions(self):
        cfg = AudioConfiguration.from_proto(
            {
                "channels": "2",
                "sample_rate": "16000",
                "sample_format": "u16",
            }
        )
        self.assertEqual(cfg.channels, 2)
        self.assertEqual(cfg.sample_rate, 16000)
        self.assertEqual(cfg.sample_format, SampleFormat.U16)

    def test_audio_cfg_defaults_and_unsupported_sample_format(self):
        # Provide garbage values to trigger defaults
        cfg = AudioConfiguration.from_proto(
            {
                "channels": "x",
                "sample_rate": "",
                "sample_format": pb2.U8,  # unsupported in local enum
            }
        )
        self.assertEqual(cfg.channels, DEFAULT_AUDIO_CHANNELS)
        self.assertEqual(cfg.sample_rate, DEFAULT_SAMPLE_RATE)
        # Unsupported sample_format falls back to default
        self.assertEqual(cfg.sample_format, DEFAULT_SAMPLE_FORMAT)

    def test_audio_cfg_from_proto_none(self):
        self.assertIsNone(AudioConfiguration.from_proto(None))


if __name__ == "__main__":
    unittest.main()
