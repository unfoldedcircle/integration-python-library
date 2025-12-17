# Python API wrapper for the UC Integration API
[![PyPi](https://img.shields.io/pypi/v/ucapi.svg)](https://pypi.org/project/ucapi)
[![License](https://img.shields.io/github/license/unfoldedcircle/integration-python-library.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This library simplifies writing Python-based integrations for the [Unfolded Circle Remote devices](https://www.unfoldedcircle.com/)
by wrapping the [WebSocket Integration API](https://github.com/unfoldedcircle/core-api/tree/main/integration-api)
and supporting the [available entities](https://unfoldedcircle.github.io/core-api/entities/).

> [!NOTE]
> Please note that this library is more of a convenience Python wrapper for the WebSocket Integreation-API than a
> full-featured SDK. It is based on our [Node.js integration library](https://github.com/unfoldedcircle/integration-node-library).

> [!IMPORTANT]
> This is our first Python project, and we don't see ourselves as Python professionals.  
> Therefore, the library is most likely not yet that Pythonic!  
> We are still learning and value your feedback on how to improve it :-)

Not yet supported:

- Secure WebSocket
- Token-based authentication

Requirements:
- Python 3.11 or newer

Integrations using this library:
  - [Android TV integration](https://github.com/unfoldedcircle/integration-androidtv)
  - [Apple TV integration](https://github.com/unfoldedcircle/integration-appletv)
  - [Denon AVR integration](https://github.com/unfoldedcircle/integration-denonavr)

## Installation

Use pip:
```shell
pip3 install ucapi
```

See [examples directory](https://github.com/aitatoi/integration-python-library/blob/main/examples) for some minimal integration driver examples.

### Environment Variables

Certain features can be configured by environment variables:

| Variable                 | Values           | Description                                                                                                          |
|--------------------------|------------------|----------------------------------------------------------------------------------------------------------------------|
| UC_CONFIG_HOME           | _directory path_ | Configuration directory to save the user configuration from the driver setup.<br>Default: $HOME or current directory |
| UC_INTEGRATION_INTERFACE | _address_        | Listening interface for WebSocket server.<br>Default: `0.0.0.0`                                                      |
| UC_INTEGRATION_HTTP_PORT | _number_         | WebSocket listening port.<br>Default: `port` field in driver metadata json file, if not specified: `9090`            |
| UC_MDNS_LOCAL_HOSTNAME   | _hostname_       | Published local hostname in mDNS service announcement.<br>Default: _short hostname_ with `.local` domain.            |
| UC_DISABLE_MDNS_PUBLISH  | `true` / `false` | Disables mDNS service advertisement.<br>Default: `false`                                                             |

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags and releases on this repository](https://github.com/unfoldedcircle/integration-python-library/releases).

## Changelog

The major changes found in each new release are listed in the [changelog](https://github.com/aitatoi/integration-python-library/blob/main/CHANGELOG.md)
and under the GitHub [releases](https://github.com/unfoldedcircle/integration-python-library/releases).

## Contributions

Please read our [contribution guidelines](https://github.com/aitatoi/integration-python-library/blob/main/CONTRIBUTING.md)
before opening a pull request.

## License

This project is licensed under the [**Mozilla Public License 2.0**](https://choosealicense.com/licenses/mpl-2.0/).
See the [LICENSE](https://github.com/aitatoi/integration-python-library/blob/main/LICENSE) file for details.
