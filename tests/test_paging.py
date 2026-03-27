"""Unit tests for Paging and Pagination classes."""

import json
import unittest
from dataclasses import asdict

from ucapi.api_definitions import Pagination, Paging


class TestPaging(unittest.TestCase):
    """Test cases for the Paging class."""

    def test_paging_default(self):
        """Test default Paging instantiation."""
        paging = Paging()
        self.assertEqual(paging.page, 1)
        self.assertEqual(paging.limit, 10)
        self.assertEqual(paging.offset, 0)

    def test_paging_custom(self):
        """Test custom Paging instantiation."""
        paging = Paging(page=2, limit=20)
        self.assertEqual(paging.page, 2)
        self.assertEqual(paging.limit, 20)
        self.assertEqual(paging.offset, 20)

    def test_paging_invalid_page(self):
        """Test validation for invalid page number."""
        with self.assertRaises(ValueError) as cm:
            Paging(page=0)
        self.assertIn("Invalid page: 0", str(cm.exception))

        with self.assertRaises(ValueError):
            Paging(page=-1)

    def test_paging_invalid_limit(self):
        """Test validation for invalid limit."""
        with self.assertRaises(ValueError) as cm:
            Paging(limit=0)
        self.assertIn("Invalid limit: 0", str(cm.exception))

        with self.assertRaises(ValueError):
            Paging(limit=-1)
        with self.assertRaises(ValueError):
            Paging(limit=10000)

    def test_paging_from_dict(self):
        """Test constructing Paging from a dictionary."""
        data = {"page": 3, "limit": 50}
        paging = Paging.from_dict(data)
        self.assertEqual(paging.page, 3)
        self.assertEqual(paging.limit, 50)

    def test_paging_from_dict_defaults(self):
        """Test constructing Paging from an empty dictionary using defaults."""
        paging = Paging.from_dict({})
        self.assertEqual(paging.page, 1)
        self.assertEqual(paging.limit, 10)

    def test_paging_serialization(self):
        """Test Paging JSON serialization."""
        paging = Paging(page=2, limit=25)
        serialized = asdict(paging)
        self.assertEqual(serialized, {"page": 2, "limit": 25})

        # Verify JSON round-trip
        json_str = json.dumps(serialized)
        self.assertEqual(json.loads(json_str), {"page": 2, "limit": 25})


class TestPagination(unittest.TestCase):
    """Test cases for the Pagination class."""

    def test_pagination_instantiation(self):
        """Test Pagination instantiation with all fields."""
        pagination = Pagination(page=1, limit=10, count=100)
        self.assertEqual(pagination.page, 1)
        self.assertEqual(pagination.limit, 10)
        self.assertEqual(pagination.count, 100)

    def test_pagination_no_count(self):
        """Test Pagination instantiation without count."""
        pagination = Pagination(page=2, limit=20)
        self.assertEqual(pagination.page, 2)
        self.assertEqual(pagination.limit, 20)
        self.assertIsNone(pagination.count)

    def test_pagination_invalid_page(self):
        """Test validation for invalid page number."""
        with self.assertRaises(ValueError) as cm:
            Pagination(page=0, limit=10)
        self.assertIn("page must be >= 1", str(cm.exception))

    def test_pagination_invalid_limit(self):
        """Test validation for invalid limit."""
        with self.assertRaises(ValueError) as cm:
            Pagination(page=1, limit=-1)
        self.assertIn("Invalid limit", str(cm.exception))

    def test_pagination_limit_out_of_range(self):
        """Test validation for invalid limit."""
        with self.assertRaises(ValueError) as cm:
            Pagination(page=1, limit=10000)
        self.assertIn("Invalid limit", str(cm.exception))

    def test_pagination_invalid_count(self):
        """Test validation for invalid count."""
        with self.assertRaises(ValueError) as cm:
            Pagination(page=1, limit=10, count=-1)
        self.assertIn("count cannot be negative", str(cm.exception))

    def test_pagination_serialization(self):
        """Test Pagination JSON serialization."""
        pagination = Pagination(page=1, limit=10, count=100)
        serialized = asdict(pagination)
        self.assertEqual(serialized, {"page": 1, "limit": 10, "count": 100})

    def test_pagination_serialization_no_count(self):
        """Test Pagination JSON serialization when count is None."""
        pagination = Pagination(page=2, limit=20)
        json_data = asdict(pagination)

        # Note: In JS/TS, undefined keys are omitted during JSON.stringify.
        # In Python, None becomes `null` in JSON.
        # This is not an issue: the Remote core service treats `null` as "not existing".
        self.assertIn("count", json_data)
        self.assertIsNone(json_data["count"])


if __name__ == "__main__":
    unittest.main()
