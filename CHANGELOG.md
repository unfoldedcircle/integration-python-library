# UC Integration API Python wrapper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

_Changes in the next release_

---

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
