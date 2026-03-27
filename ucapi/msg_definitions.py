"""
Internal WebSocket message structure definitions.

See Integration-API for more information:
https://github.com/unfoldedcircle/core-api/tree/main/integration-api

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import dataclass, field

from .api_definitions import Paging
from .media_player import BrowseOptions, SearchMediaFilter, SearchOptions


@dataclass(kw_only=True)
class BrowseMediaMsgData(BrowseOptions):
    """
    Browsing media request message.

    Attributes:
        entity_id (str):
            media-player entity ID to browse.
    """

    entity_id: str
    paging: Paging | dict | None = field(default=None)

    def __post_init__(self):  # pylint: disable=W0246
        """Encode custom fields."""
        paging = self.paging
        if paging is None:
            self.paging = Paging()
        elif isinstance(paging, dict):
            self.paging = Paging.from_dict(paging)


@dataclass(kw_only=True)
class SearchMediaMsgData(SearchOptions):
    """
    Search media request message.

    Attributes:
        entity_id (str):
            media-player entity ID to browse.
        query (str):
            Free text search query.
        filter (SearchMediaFilter|None):
            Additional user filter to limit the search scope.
    """

    entity_id: str
    query: str
    filter: SearchMediaFilter | None = None
    paging: Paging | dict | None = field(default=None)

    def __post_init__(self):
        """Encode custom fields."""
        paging = self.paging
        if paging is None:
            self.paging = Paging()
        elif isinstance(paging, dict):
            self.paging = Paging.from_dict(paging)

        filter_value = self.filter
        if isinstance(filter_value, dict):
            self.filter = SearchMediaFilter.from_dict(filter_value)
