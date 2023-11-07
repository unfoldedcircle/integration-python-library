# UC Integration API Python wrapper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

_Changes in the next release_

---

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
