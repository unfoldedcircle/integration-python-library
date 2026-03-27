"""
Tests for media player entity.
"""

import unittest
from ucapi.media_player import SearchMediaFilter, MediaClass, BrowseMediaItem


class TestMediaPlayer(unittest.TestCase):
    """Media player tests."""

    def test_search_media_filter_media_classes(self):
        """Test SearchMediaFilter media_classes with standard and custom values."""
        # Test with standard MediaClass
        smf = SearchMediaFilter(media_classes=[MediaClass.ALBUM, MediaClass.TRACK])
        self.assertEqual(smf.media_classes, [MediaClass.ALBUM, MediaClass.TRACK])

        # Test with strings that match MediaClass
        smf = SearchMediaFilter(media_classes=["album", "track"])
        self.assertEqual(smf.media_classes, [MediaClass.ALBUM, MediaClass.TRACK])

        # Test with custom string values
        try:
            smf = SearchMediaFilter(media_classes=["custom_class", "another_one"])
            self.assertEqual(smf.media_classes, ["custom_class", "another_one"])
        except ValueError as e:
            self.fail(
                f"SearchMediaFilter raised ValueError for custom media classes: {e}"
            )

    def test_search_media_filter_mixed_classes(self):
        """Test SearchMediaFilter with a mix of MediaClass and custom strings."""
        try:
            smf = SearchMediaFilter(media_classes=[MediaClass.ALBUM, "custom_class"])
            self.assertEqual(smf.media_classes, [MediaClass.ALBUM, "custom_class"])
        except ValueError as e:
            self.fail(
                f"SearchMediaFilter raised ValueError for mixed media classes: {e}"
            )

    def test_search_media_filter_none(self):
        """Test SearchMediaFilter with None media_classes."""
        smf = SearchMediaFilter(media_classes=None)
        self.assertIsNone(smf.media_classes)

    def test_search_media_filter_from_dict(self):
        """Test SearchMediaFilter.from_dict with custom values."""
        data = {
            "media_classes": ["album", "custom_class"],
            "artist": "Some Artist",
            "album": "Some Album",
        }
        try:
            smf = SearchMediaFilter.from_dict(data)
            self.assertEqual(smf.media_classes, [MediaClass.ALBUM, "custom_class"])
            self.assertEqual(smf.artist, "Some Artist")
            self.assertEqual(smf.album, "Some Album")
        except ValueError as e:
            self.fail(
                f"SearchMediaFilter.from_dict raised ValueError for custom media classes: {e}"
            )

    def test_browse_media_item_validation_mandatory(self):
        """Test BrowseMediaItem mandatory field validation."""
        # Valid mandatory fields
        item = BrowseMediaItem(media_id="id1", title="Title")
        self.assertEqual(item.media_id, "id1")
        self.assertEqual(item.title, "Title")

        # media_id empty
        with self.assertRaisesRegex(
            ValueError, "media_id must be at least 1 characters"
        ):
            BrowseMediaItem(media_id="", title="Title")

        # media_id too long
        with self.assertRaisesRegex(
            ValueError, "media_id must be at most 255 characters"
        ):
            BrowseMediaItem(media_id="a" * 256, title="Title")

        # media_id wrong type
        with self.assertRaisesRegex(TypeError, "media_id must be str, got int"):
            BrowseMediaItem(media_id=123, title="Title")

        # title empty
        with self.assertRaisesRegex(ValueError, "title must be at least 1 characters"):
            BrowseMediaItem(media_id="id1", title="")

        # title too long
        with self.assertRaisesRegex(ValueError, "title must be at most 255 characters"):
            BrowseMediaItem(media_id="id1", title="a" * 256)

    def test_browse_media_item_validation_optional(self):
        """Test BrowseMediaItem optional field validation."""
        # subtitle
        with self.assertRaisesRegex(
            ValueError, "subtitle must be at least 1 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", subtitle="")
        with self.assertRaisesRegex(
            ValueError, "subtitle must be at most 255 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", subtitle="a" * 256)

        # artist
        with self.assertRaisesRegex(ValueError, "artist must be at least 1 characters"):
            BrowseMediaItem(media_id="id1", title="Title", artist="")
        with self.assertRaisesRegex(
            ValueError, "artist must be at most 255 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", artist="a" * 256)

        # album
        with self.assertRaisesRegex(ValueError, "album must be at least 1 characters"):
            BrowseMediaItem(media_id="id1", title="Title", album="")
        with self.assertRaisesRegex(ValueError, "album must be at most 255 characters"):
            BrowseMediaItem(media_id="id1", title="Title", album="a" * 256)

        # media_class (only when it's a string)
        # Note: media class is allowed to be empty!
        BrowseMediaItem(media_id="id1", title="Title", media_class="")

        with self.assertRaisesRegex(
            ValueError, "media_class must be at most 255 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", media_class="a" * 256)
        # Verify it accepts MediaClass enum without error
        BrowseMediaItem(media_id="id1", title="Title", media_class=MediaClass.ALBUM)

        # media_type (only when it's a string)
        # Note: media type is allowed to be empty!
        BrowseMediaItem(media_id="id1", title="Title", media_type="")

        with self.assertRaisesRegex(
            ValueError, "media_type must be at most 255 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", media_type="a" * 256)

    def test_browse_media_item_validation_thumbnail(self):
        """Test BrowseMediaItem thumbnail field validation."""
        # Valid length
        BrowseMediaItem(media_id="id1", title="Title", thumbnail="a" * 32768)

        # Too short (empty)
        with self.assertRaisesRegex(
            ValueError, "thumbnail must be at least 1 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", thumbnail="")

        # Too long
        with self.assertRaisesRegex(
            ValueError, "thumbnail must be at most 32768 characters"
        ):
            BrowseMediaItem(media_id="id1", title="Title", thumbnail="a" * 32769)


if __name__ == "__main__":
    unittest.main()
