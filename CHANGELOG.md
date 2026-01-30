# UC Integration API Python wrapper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

_Changes in the next release_

---

## v0.5.2 - 2026-01-30
### Added
- Add Select Entity support by @JackJPowell ([#44](https://github.com/unfoldedcircle/integration-python-library/pull/44)).
- Add IR Emitter Entity support by @JackJPowell ([#45](https://github.com/unfoldedcircle/integration-python-library/pull/45)).

## v0.5.1 - 2025-12-19
### Added
- Add binary sensor device class and common entity states enum ([#40](https://github.com/unfoldedcircle/integration-python-library/pull/40)).

### Changed
- Optional event loop argument in IntegrationAPI constructor ([#41](https://github.com/unfoldedcircle/integration-python-library/pull/41)).

## v0.5.0 - 2025-12-17
### Breaking Changes
- Enhance entity command handler with WS client connection parameter in `CommandHandler` callback and `Entity.command`
  method to allow clients to send back event messages ([#38](https://github.com/unfoldedcircle/integration-python-library/pull/38)).
  - The implementation is currently backward-compatible but will be removed in a future release.

### Added
- New voice-assistant entity with voice-stream session handling ([#38](https://github.com/unfoldedcircle/integration-python-library/pull/38)).
  - This requires firmware 2.8.2 or newer to work correctly.

### Changed
- Remove logging in Entities.get method if entity doesn't exist. This could lead to excessive logging in some integrations ([#38](https://github.com/unfoldedcircle/integration-python-library/pull/38)).
- Prepare for Python 3.12 and 3.13: replace `asyncio.get_event_loop()` calls in the examples with `asyncio.new_event_loop()` ([#39](https://github.com/unfoldedcircle/integration-python-library/pull/39)).

## v0.4.0 - 2025-11-24
### Breaking Changes
- A WebSocket disconnection no longer emits the `DISCONNECT` event, but the new `CLIENT_DISCONNECTED` event ([#35](https://github.com/unfoldedcircle/integration-python-library/pull/35)).

### Added
- New `CLIENT_CONNECTED` event is emitted when a WebSocket client connects ([#35](https://github.com/unfoldedcircle/integration-python-library/pull/35)).
- WebSocket client identification in disconnect log statements.

### Fixed
- Null reference exception in log filter ([#33](https://github.com/unfoldedcircle/integration-python-library/pull/33)).
- Set changed size during iteration for WS broadcast ([#36](https://github.com/unfoldedcircle/integration-python-library/pull/36)).

## v0.3.2 - 2025-09-17
### Changed
- Add support for IR Emitter EntityType ([#31](https://github.com/unfoldedcircle/integration-python-library/pull/31)).
- Add stop, record and menu for remote entity buttons ([#32](https://github.com/unfoldedcircle/integration-python-library/pull/32)).

## v0.3.1 - 2025-05-14
### Fixed
- Filtered log messages may not modify original data. This sporadically removed media artwork URLs ([#27](https://github.com/unfoldedcircle/integration-python-library/pull/27)).

## v0.3.0 - 2025-04-25
### Added
- New media-player attribute MEDIA_POSITION_UPDATED_AT ([feature-and-bug-tracker#443](https://github.com/unfoldedcircle/feature-and-bug-tracker/issues/443)).
### Changed
- Filter out base64 encoded media-player image fields in entity_states response log messages ([#22](https://github.com/unfoldedcircle/integration-python-library/issues/22)).
- Require websockets version v14 or newer.

## v0.2.0 - 2024-04-28
### Added
- New remote-entity type. Requires remote-core / Core Simulator version 0.43.0 or newer.

## v0.1.7 - 2024-03-13
### Changed
- Filter out base64 encoded media-player image fields in log messages ([#17](https://github.com/unfoldedcircle/integration-python-library/issues/17)).

## v0.1.6 - 2024-03-04
### Added
- Media-player RepeatMode enum and new features: context_menu, settings

## v0.1.5 - 2024-02-28
### Changed
- Allow newer zeroconf versions than 0.120.0 (e.g. pyatv 0.14.5 requires 0.131.0).

## v0.1.4 - 2024-02-27
### Added
- Media-player entity features ([core-api/#32](https://github.com/unfoldedcircle/core-api/issues/32)):
  - new features: numpad, guide, info, eject, open_close, audio_track, subtitle, record.
  - new option: simple_commands for any additional commands not covered by a feature.

### Fixed
- Return entity options in `get_available_entities` response message.

### Changed
- Add `reconfigure` flag in `DriverSetupRequest` message to reconfigure a driver.
- Always notify clients when setting a new device state, even if the state doesn't change.

## v0.1.3 - 2023-11-08
### Fixed
- Environment variable `UC_INTEGRATION_HTTP_PORT` to override server port.

### Changed
- Update zeroconf dependency and remove asyncio library.

## v0.1.2 - 2023-11-07
### Fixed
- Propagate setup error code from driver in setup flow.
- Add delays in setup flow for web-configurator to show error pages.

### Changed
- Replace `SETUP_DRIVER_ABORT` event with new `AbortDriverSetup` class in setup handler callback.

## v0.1.1 - 2023-11-04

First public release on PyPI 🎉

## v0.1.0 - 2023-11-02
### Added
- Type information
- Simple example and initial developer documentation

### Fixed
- mDNS service publishing announces local hostname.
- ENV var handling: `UC_INTEGRATION_INTERFACE` and `UC_INTEGRATION_HTTP_PORT` are optional (#2, #3)
- config_dir_path is always set

### Changed
- driver setup process
- entity command handler
- don't expose AsyncIOEventEmitter for event callbacks
- invalid names in public classes
- logging configuration, configuration must be done in client code
