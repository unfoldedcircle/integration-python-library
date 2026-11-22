#!/usr/bin/env python3
"""
Webview entity example.

Demonstrates:
1. A simple URL-only webview entity.
2. A complex webview entity with Basic authentication credentials, TLS exception,
   cookies, custom user agent, zoom, navigation controls, reload interval, button
   mappings, and device API enabled.
3. Rotating credentials after connecting to the Remote by updating the entity
   definition, which broadcasts an ``entity_available`` event.
"""

import asyncio
import logging
import time

import ucapi
from ucapi.webview import (
    Attributes,
    AuthType,
    Button,
    ButtonActionType,
    ButtonFunction,
    ButtonKey,
    Options,
    States,
    UserAgent,
)

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)


def create_dashboard_webview(password: str) -> ucapi.Webview:
    """Create the complex dashboard webview entity with the given password."""
    return ucapi.Webview(
        "dashboard_webview",
        {
            "en": "Energy Dashboard",
            "de": "Energie-Dashboard",
        },
        options={
            Options.URL: "https://dashboard.home.arpa/energy?kiosk=1",
            Options.AUTH: {
                "type": AuthType.BASIC,
                "username": "remote",
                "password": password,
            },
            Options.TLS: {
                "allow_invalid_certificate": True,
            },
            Options.COOKIES: [
                {
                    "name": "theme",
                    "value": "dark",
                    "http_only": False,
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
                Button.DPAD_DOWN: {
                    "action": ButtonActionType.FUNCTION,
                    "function": ButtonFunction.SCROLL_DOWN,
                },
                Button.VOLUME_UP: {"action": ButtonActionType.PASS},
                Button.VOLUME_DOWN: {"action": ButtonActionType.PASS},
                Button.CHANNEL_UP: {
                    "action": ButtonActionType.KEY,
                    "key": ButtonKey.CHANNEL_UP,
                },
            },
            Options.DEVICE_API: True,
        },
        attributes={Attributes.STATE: States.ON},
        icon="uc:web",
        description={
            "en": "Local home energy monitoring dashboard",
            "de": "Lokales Energie-Dashboard",
        },
        area="Living Room",
    )


@api.listens_to(ucapi.Events.CONNECT)
async def on_connect() -> None:
    """Handle Remote connect event and rotate dashboard credentials."""
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)

    # Simulate rotating / refreshing login credentials after connecting to the Remote.
    # `available_entities.update(...)` updates the entity definition and broadcasts an
    # `entity_available` event to connected Remotes supporting Integration-API >= 0.18.0.
    rotated_password = f"rotated-secret-{int(time.time() * 1000)}"
    updated_dashboard = create_dashboard_webview(rotated_password)
    api.available_entities.update(updated_dashboard)
    print("Updated dashboard webview credentials via entity_available event")


@api.listens_to(ucapi.Events.DISCONNECT)
async def on_disconnect() -> None:
    """Handle Remote disconnect event."""
    await api.set_device_state(ucapi.DeviceStates.DISCONNECTED)


@api.listens_to(ucapi.Events.SUBSCRIBE_ENTITIES)
async def on_subscribe_entities(entity_ids: list[str]) -> None:
    """Handle entity subscriptions."""
    for entity_id in entity_ids:
        print(f"Subscribed entity: {entity_id}")


@api.listens_to(ucapi.Events.UNSUBSCRIBE_ENTITIES)
async def on_unsubscribe_entities(entity_ids: list[str]) -> None:
    """Handle entity unsubscriptions."""
    for entity_id in entity_ids:
        print(f"Unsubscribed entity: {entity_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # 1. Simple webview entity with URL only
    simple_webview = ucapi.Webview(
        "simple_webview",
        "Unfolded Circle",
        options={Options.URL: "https://www.unfoldedcircle.com"},
    )
    api.available_entities.add(simple_webview)

    # 2. Complex webview entity with login credentials and additional options
    api.available_entities.add(create_dashboard_webview("initial-secret-password"))

    print("Available entities:", api.available_entities.get_ids())

    loop.run_until_complete(api.init("webview.json"))
    loop.run_forever()
