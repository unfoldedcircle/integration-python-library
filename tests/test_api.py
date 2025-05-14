import unittest
from copy import deepcopy

from ucapi.api import filter_log_msg_data
from ucapi.media_player import Attributes


class TestFilterLogMsgData(unittest.TestCase):

    def test_no_modification_when_no_msg_data(self):
        data = {}
        result = filter_log_msg_data(data)
        self.assertEqual(result, {}, "The result should be an empty dictionary")

    def test_no_changes_when_media_image_url_not_present(self):
        data = {"msg_data": {"attributes": {"state": "playing", "volume": 50}}}
        original = deepcopy(data)

        result = filter_log_msg_data(data)

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
        ] = "data:***"

        result = filter_log_msg_data(data)

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
        ] = "data:***"
        expected_result["msg_data"][1]["attributes"][
            Attributes.MEDIA_IMAGE_URL
        ] = "data:***"

        result = filter_log_msg_data(data)

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

        filter_log_msg_data(data)

        self.assertEqual(
            data, original_data, "The input data should not be modified by the function"
        )
