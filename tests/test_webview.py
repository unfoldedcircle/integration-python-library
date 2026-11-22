"""
Tests for webview entity support, entity lifecycle events, and capability filtering.

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

from ucapi import Entities, EntityTypes, Events, IntegrationAPI, Switch, Webview
from ucapi.api import _WsContext
from ucapi.webview import (
    FIXED_BUTTONS,
    Attributes,
    AuthType,
    Button,
    ButtonActionType,
    ButtonFunction,
    ButtonKey,
    Commands,
    Features,
    Options,
    States,
    UserAgent,
)


def _register_client(
    api: IntegrationAPI,
    remote_address: tuple[str, int],
    supported_types: set[str] | None = None,
) -> tuple[Mock, _WsContext]:
    """Attach a mock websocket client and context directly to IntegrationAPI."""
    ws = Mock()
    ws.remote_address = remote_address
    ctx = _WsContext(
        incoming=asyncio.Queue(),
        outgoing=asyncio.Queue(),
        pending={},
        supported_entity_types=supported_types,
    )
    api._clients.add(ws)  # pylint: disable=protected-access
    api._ws_contexts[ws] = ctx  # pylint: disable=protected-access
    return ws, ctx


class TestWebview(unittest.IsolatedAsyncioTestCase):
    """Test webview entity definitions, serialization, lifecycle events, and filtering."""

    def test_minimal_entity(self):
        """Construct a minimal URL-only webview entity."""
        entity = Webview(
            "simple",
            "Unfolded Circle",
            {Options.URL: "https://www.unfoldedcircle.com"},
        )

        self.assertEqual(entity.id, "simple")
        self.assertEqual(entity.entity_type, EntityTypes.WEBVIEW)
        self.assertEqual(EntityTypes("webview"), EntityTypes.WEBVIEW)
        self.assertEqual(entity.name, {"en": "Unfolded Circle"})
        self.assertEqual(entity.features, [])
        self.assertEqual(entity.attributes, {})
        self.assertEqual(entity.options, {"url": "https://www.unfoldedcircle.com"})
        self.assertIsNone(entity.device_class)
        self.assertEqual(list(Features), [])
        self.assertEqual(FIXED_BUTTONS, ("HOME", "POWER", "VOICE"))
        self.assertEqual(
            [c.value for c in Commands],
            ["open", "reload", "clear_cache", "clear_data"],
        )

    def test_validation_requires_url_option(self):
        """Reject missing or invalid options / url at construction time."""
        with self.assertRaises(TypeError):
            Webview("bad", "Bad", None)  # type: ignore[arg-type]

        for bad_options in (
            {},
            {Options.URL: ""},
            {Options.URL: "   "},
            {Options.URL: 123},
        ):
            with self.subTest(bad_options=bad_options):
                with self.assertRaises(ValueError):
                    Webview("bad", "Bad", bad_options)

    async def test_full_entity_serialization(self):
        """Serialize a fully configured webview entity with all option fields."""
        entity = Webview(
            "dashboard",
            {"en": "Energy Dashboard", "de": "Energie-Dashboard"},
            options={
                Options.URL: "https://dashboard.home.arpa/energy?kiosk=1",
                Options.AUTH: {
                    "type": AuthType.BASIC,
                    "username": "remote",
                    "password": "secret",
                },
                Options.TLS: {
                    "certificate_sha256": "AA:BB",
                    "allow_invalid_certificate": False,
                },
                Options.COOKIES: [
                    {
                        "name": "session",
                        "value": "cookie-secret",
                        "domain": "dashboard.home.arpa",
                        "path": "/",
                        "secure": True,
                        "http_only": True,
                    }
                ],
                Options.USER_AGENT: UserAgent.DESKTOP,
                Options.ZOOM: 75,
                Options.BACKGROUND_COLOR: "#121212",
                Options.SHOW_NAVIGATION: True,
                Options.RELOAD_INTERVAL: 60,
                Options.BUTTONS: {
                    Button.DPAD_UP: {
                        "action": ButtonActionType.FUNCTION,
                        "function": ButtonFunction.SCROLL_UP,
                    },
                    Button.VOLUME_UP: {"action": ButtonActionType.PASS},
                    Button.CHANNEL_UP: {
                        "action": ButtonActionType.KEY,
                        "key": ButtonKey.CHANNEL_UP,
                    },
                },
                Options.DEVICE_API: True,
            },
            attributes={Attributes.STATE: States.ON},
            icon="uc:web",
            description={"en": "Dashboard"},
            area="Living Room",
        )
        entity.device_id = "hub-1"

        entities = Entities("available", asyncio.get_running_loop())
        self.assertTrue(entities.add(entity))
        self.assertEqual(entities.get_ids(), ["dashboard"])

        serialized = json.loads(json.dumps(entities.get_all()))
        self.assertEqual(
            serialized,
            [
                {
                    "entity_id": "dashboard",
                    "entity_type": "webview",
                    "device_id": "hub-1",
                    "features": [],
                    "name": {"en": "Energy Dashboard", "de": "Energie-Dashboard"},
                    "icon": "uc:web",
                    "description": {"en": "Dashboard"},
                    "options": {
                        "url": "https://dashboard.home.arpa/energy?kiosk=1",
                        "auth": {
                            "type": "basic",
                            "username": "remote",
                            "password": "secret",
                        },
                        "tls": {
                            "certificate_sha256": "AA:BB",
                            "allow_invalid_certificate": False,
                        },
                        "cookies": [
                            {
                                "name": "session",
                                "value": "cookie-secret",
                                "domain": "dashboard.home.arpa",
                                "path": "/",
                                "secure": True,
                                "http_only": True,
                            }
                        ],
                        "user_agent": "desktop",
                        "zoom": 75,
                        "background_color": "#121212",
                        "show_navigation": True,
                        "reload_interval": 60,
                        "buttons": {
                            "DPAD_UP": {
                                "action": "function",
                                "function": "scroll_up",
                            },
                            "VOLUME_UP": {"action": "pass"},
                            "CHANNEL_UP": {
                                "action": "key",
                                "key": "ChannelUp",
                            },
                        },
                        "device_api": True,
                    },
                    "area": "Living Room",
                }
            ],
        )

    async def test_entities_store_lifecycle_events(self):
        """Verify notify defaults and event emission on add, update, and remove."""
        entities = Entities("available", asyncio.get_running_loop())
        available_events = []
        removed_events = []
        entities.add_listener(
            Events.ENTITY_AVAILABLE, lambda e: available_events.append(e)
        )
        entities.add_listener(Events.ENTITY_REMOVED, lambda e: removed_events.append(e))

        wv1 = Webview("wv1", "WV 1", {Options.URL: "https://example.com/1"})
        wv2 = Webview("wv2", "WV 2", {Options.URL: "https://example.com/2"})

        # add defaults to notify=False
        self.assertTrue(entities.add(wv1))
        self.assertEqual(available_events, [])

        # duplicate add returns False and does not emit
        self.assertFalse(entities.add(wv1, notify=True))
        self.assertEqual(available_events, [])

        # add with notify=True emits ENTITY_AVAILABLE
        self.assertTrue(entities.add(wv2, notify=True))
        self.assertEqual(available_events, [wv2])

        # update missing entity returns False and does not emit
        missing = Webview("missing", "Missing", {Options.URL: "https://example.com"})
        self.assertFalse(entities.update(missing))
        self.assertEqual(available_events, [wv2])

        # update defaults to notify=True
        wv1_updated = Webview(
            "wv1", "WV 1 New", {Options.URL: "https://example.com/1b"}
        )
        self.assertTrue(entities.update(wv1_updated))
        self.assertEqual(available_events, [wv2, wv1_updated])
        self.assertIs(entities.get("wv1"), wv1_updated)

        # update with notify=False does not emit
        wv1_silent = Webview(
            "wv1", "WV 1 Silent", {Options.URL: "https://example.com/1c"}
        )
        self.assertTrue(entities.update(wv1_silent, notify=False))
        self.assertEqual(available_events, [wv2, wv1_updated])

        # remove missing entity returns False and does not emit
        self.assertFalse(entities.remove("nonexistent", notify=True))
        self.assertEqual(removed_events, [])

        # remove defaults to notify=False
        self.assertTrue(entities.remove("wv2"))
        self.assertEqual(removed_events, [])

        # remove with notify=True emits ENTITY_REMOVED
        self.assertTrue(entities.remove("wv1", notify=True))
        self.assertEqual(removed_events, [wv1_silent])

    async def test_discovery_filters_by_client_capabilities(self):
        """Filter entities by supported_entity_types and return all when unknown."""
        api = IntegrationAPI(asyncio.get_running_loop())
        webview = Webview("wv", "Web", {Options.URL: "https://example.com"})
        switch = Switch("sw", "Switch", [], {})
        api.available_entities.add(webview)
        api.available_entities.add(switch)

        for supported, expected_ids in (
            (["switch", "webview"], ["wv", "sw"]),
            (["switch"], ["sw"]),
            ([], ["wv", "sw"]),
        ):
            with self.subTest(supported=supported):
                ws = Mock()
                ws.remote_address = ("127.0.0.1", 12345)
                with (
                    patch.object(
                        api,
                        "get_supported_entity_types",
                        new_callable=AsyncMock,
                        return_value=supported,
                    ),
                    patch.object(
                        api, "_enqueue_ws_payload", new_callable=AsyncMock
                    ) as send,
                ):
                    await api._process_ws_message(  # pylint: disable=protected-access
                        ws,
                        {"kind": "req", "id": 1, "msg": "get_available_entities"},
                    )

                response = json.loads(json.dumps(send.await_args.args[1]))
                self.assertEqual(response["msg"], "available_entities")
                self.assertEqual(
                    [
                        item["entity_id"]
                        for item in response["msg_data"]["available_entities"]
                    ],
                    expected_ids,
                )

        # Also fall back to returning all entities if get_supported_entity_types fails
        ws = Mock()
        ws.remote_address = ("127.0.0.1", 12346)
        with (
            patch.object(
                api,
                "get_supported_entity_types",
                new_callable=AsyncMock,
                side_effect=asyncio.TimeoutError(),
            ),
            patch.object(api, "_enqueue_ws_payload", new_callable=AsyncMock) as send,
        ):
            await api._process_ws_message(  # pylint: disable=protected-access
                ws,
                {"kind": "req", "id": 2, "msg": "get_available_entities"},
            )

        response = json.loads(json.dumps(send.await_args.args[1]))
        self.assertEqual(
            [item["entity_id"] for item in response["msg_data"]["available_entities"]],
            ["wv", "sw"],
        )

    async def test_per_client_lifecycle_broadcast_and_configured_sync(self):
        """Broadcast entity_available/entity_removed only to capable clients and preserve attributes."""
        api = IntegrationAPI(asyncio.get_running_loop())
        ws_new, _ = _register_client(
            api, ("127.0.0.1", 1001), supported_types={"switch", "webview"}
        )
        ws_old, _ = _register_client(
            api, ("127.0.0.1", 1002), supported_types={"switch"}
        )
        ws_unknown, _ = _register_client(api, ("127.0.0.1", 1003), supported_types=None)

        initial = Webview(
            "dash",
            "Dashboard",
            {
                Options.URL: "https://dashboard.example.com",
                Options.AUTH: {"type": AuthType.BEARER, "token": "tok-1"},
            },
            attributes={Attributes.STATE: States.UNAVAILABLE},
        )
        initial.device_id = "dev-1"
        api.available_entities.add(initial)
        # Simulate subscribed/configured entity with runtime state UNAVAILABLE
        api.configured_entities.add(initial)

        updated = Webview(
            "dash",
            "Dashboard",
            {
                Options.URL: "https://dashboard.example.com",
                Options.AUTH: {"type": AuthType.BEARER, "token": "tok-2"},
            },
        )
        updated.device_id = "dev-1"

        with (
            patch.object(
                api,
                "get_supported_entity_types",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch.object(api, "_enqueue_ws_payload", new_callable=AsyncMock) as send,
        ):
            self.assertTrue(api.available_entities.update(updated))
            # Yield to event loop so AsyncIOEventEmitter task completes
            await asyncio.sleep(0)
            await asyncio.sleep(0)

            # Only ws_new should have received entity_available
            self.assertEqual(send.await_count, 1)
            target_ws, payload = send.await_args.args
            self.assertIs(target_ws, ws_new)
            self.assertEqual(payload["kind"], "event")
            self.assertEqual(payload["msg"], "entity_available")
            self.assertEqual(payload["cat"], "ENTITY")
            self.assertEqual(payload["msg_data"]["entity_id"], "dash")
            self.assertEqual(payload["msg_data"]["options"]["auth"]["token"], "tok-2")

            # Configured entity updated definition while preserving live runtime state
            configured = api.configured_entities.get("dash")
            self.assertIsNotNone(configured)
            self.assertEqual(configured.options["auth"]["token"], "tok-2")
            self.assertEqual(
                configured.attributes[Attributes.STATE], States.UNAVAILABLE
            )

            # Remove with notify=True -> only ws_new receives entity_removed
            send.reset_mock()
            self.assertTrue(api.available_entities.remove("dash", notify=True))
            await asyncio.sleep(0)
            await asyncio.sleep(0)

            self.assertEqual(send.await_count, 1)
            target_ws, payload = send.await_args.args
            self.assertIs(target_ws, ws_new)
            self.assertEqual(payload["kind"], "event")
            self.assertEqual(payload["msg"], "entity_removed")
            self.assertEqual(payload["cat"], "ENTITY")
            self.assertEqual(
                payload["msg_data"],
                {
                    "entity_id": "dash",
                    "entity_type": "webview",
                    "device_id": "dev-1",
                },
            )

        # Ensure ws_old and ws_unknown were never sent events
        self.assertIsNot(ws_old, ws_new)
        self.assertIsNot(ws_unknown, ws_new)


if __name__ == "__main__":
    unittest.main()
