import unittest
from copy import deepcopy

from ucapi.api import sanitize_json_message
from ucapi.media_player import Attributes


class TestSanitizeJsonMessage(unittest.TestCase):

    def test_no_modification_when_no_msg_data(self):
        data = {}
        result = sanitize_json_message(data)
        self.assertEqual(result, {}, "The result should be an empty dictionary")

    def test_no_changes_when_media_image_url_not_present(self):
        data = {"msg_data": {"attributes": {"state": "playing", "volume": 50}}}
        original = deepcopy(data)

        result = sanitize_json_message(data)

        self.assertEqual(
            result,
            original,
            "The result should be the same as the input when no filtered attributes are present",
        )

    def test_filtering_media_image_url_in_dict(self):
        data = {
            "msg_data": {
                "attributes": {
                    "state": "playing",
                    Attributes.MEDIA_IMAGE_URL: "data:image/png;base64,encodeddata",
                }
            }
        }
        expected_result = deepcopy(data)
        expected_result["msg_data"]["attributes"][
            Attributes.MEDIA_IMAGE_URL
        ] = "data:..."

        result = sanitize_json_message(data)

        self.assertEqual(
            result, expected_result, "The MEDIA_IMAGE_URL attribute should be filtered"
        )

    def test_filtering_media_image_url_in_list(self):
        data = {
            "msg_data": [
                {
                    "attributes": {
                        "state": "paused",
                        Attributes.MEDIA_IMAGE_URL: "data:image/png;base64,exampledata",
                    }
                },
                {
                    "attributes": {
                        "state": "playing",
                        Attributes.MEDIA_IMAGE_URL: "data:image/jpg;base64,exampledata",
                    }
                },
                {"attributes": {"state": "stopped"}},
            ]
        }
        expected_result = deepcopy(data)
        expected_result["msg_data"][0]["attributes"][
            Attributes.MEDIA_IMAGE_URL
        ] = "data:..."
        expected_result["msg_data"][1]["attributes"][
            Attributes.MEDIA_IMAGE_URL
        ] = "data:..."

        result = sanitize_json_message(data)

        self.assertEqual(
            result,
            expected_result,
            "All MEDIA_IMAGE_URL attributes in the list should be filtered",
        )

    def test_input_is_not_modified(self):
        data = {
            "msg_data": {
                "attributes": {
                    Attributes.MEDIA_IMAGE_URL: "data:image/png;base64,encodeddata"
                }
            }
        }
        original_data = deepcopy(data)

        sanitize_json_message(data)

        self.assertEqual(
            data, original_data, "The input data should not be modified by the function"
        )

    def test_generic_sensitive_keys_redaction(self):
        sensitive_keys = [
            "token",
            "token_id",
            "access_token",
            "refresh_token",
            "id_token",
            "authorization_code",
            "client_secret",
            "secret",
            "auth_url",
            "client_data",
            "password",
            "header_value",
        ]

        for key in sensitive_keys:
            msg = {key: "sensitive-value", "other": "public-value"}
            sanitized = sanitize_json_message(msg)
            self.assertEqual(
                sanitized[key], "***REDACTED***", f"{key} should be redacted"
            )
            self.assertEqual(
                sanitized["other"], "public-value", "public fields should remain intact"
            )

    def test_webview_secrets_redaction(self):
        msg = {
            "kind": "event",
            "msg": "entity_available",
            "msg_data": {
                "entity_id": "dashboard",
                "entity_type": "webview",
                "options": {
                    "url": "https://dashboard.example.com",
                    "auth": {
                        "type": "header",
                        "username": "alice",
                        "password": "secret-password",
                        "token": "secret-token",
                        "header_name": "X-API-Key",
                        "header_value": "secret-api-key",
                    },
                    "cookies": [
                        {
                            "name": "session",
                            "value": "secret-cookie-value",
                            "domain": "dashboard.example.com",
                            "http_only": True,
                        },
                        {"name": "theme", "value": "dark"},
                    ],
                },
                "attributes": {
                    "value": 42,
                },
            },
        }
        original = deepcopy(msg)
        sanitized = sanitize_json_message(msg)

        self.assertEqual(msg, original, "Original message must not be mutated")
        opts = sanitized["msg_data"]["options"]
        self.assertEqual(opts["url"], "https://dashboard.example.com")
        self.assertEqual(opts["auth"]["username"], "alice")
        self.assertEqual(opts["auth"]["header_name"], "X-API-Key")
        self.assertEqual(opts["auth"]["password"], "***REDACTED***")
        self.assertEqual(opts["auth"]["token"], "***REDACTED***")
        self.assertEqual(opts["auth"]["header_value"], "***REDACTED***")
        self.assertEqual(opts["cookies"][0]["name"], "session")
        self.assertEqual(opts["cookies"][0]["value"], "***REDACTED***")
        self.assertEqual(opts["cookies"][0]["domain"], "dashboard.example.com")
        self.assertEqual(opts["cookies"][1]["name"], "theme")
        self.assertEqual(opts["cookies"][1]["value"], "***REDACTED***")
        # Unrelated "value" fields (e.g. number/sensor attributes) must NOT be redacted
        self.assertEqual(sanitized["msg_data"]["attributes"]["value"], 42)

    def test_recursive_redaction(self):
        msg = {
            "level1": {
                "token": "secret1",
                "level2": {"secret": "secret2", "public": "data"},
            },
            "array": [{"refresh_token": "secret3"}, "plain-string"],
        }
        sanitized = sanitize_json_message(msg)
        self.assertEqual(sanitized["level1"]["token"], "***REDACTED***")
        self.assertEqual(sanitized["level1"]["level2"]["secret"], "***REDACTED***")
        self.assertEqual(sanitized["level1"]["level2"]["public"], "data")
        self.assertEqual(sanitized["array"][0]["refresh_token"], "***REDACTED***")
        self.assertEqual(sanitized["array"][1], "plain-string")
