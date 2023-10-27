# Python API wrapper for the UC Integration API

This is a Python library that can be used for Python based integrations. It wraps the UC Integration API.

It's a pre-alpha release. Missing features will be added continuously. Based on the NodeJS implementation.

Not supported:

- secure WebSocket

Requires Python 3.10 or newer

---

### Local testing:
```shell
python3 setup.py bdist_wheel
pip3 install --force-reinstall dist/ucapi-$VERSION-py3-none-any.whl
```

## Code Style

- Code line length: 120
- Use double quotes as default (don't mix and match for simple quoting, checked with pylint).

Install tooling:
```shell
pip3 install -r test-requirements.txt
```

### Verify

The following tests are run as GitHub action for each push on the main branch and for pull requests.
They can also be run anytime on a local developer machine:
```shell
python -m pylint ucapi
python -m flake8 ucapi --count --show-source --statistics
python -m isort ucapi/. --check --verbose 
python -m black ucapi --check --verbose --line-length 120
```

Linting integration in PyCharm/IntelliJ IDEA:
1. Install plugin [Pylint](https://plugins.jetbrains.com/plugin/11084-pylint)
2. Open Pylint window and run a scan: `Check Module` or `Check Current File`

### Format Code
```shell
python -m black ucapi --line-length 120
```

PyCharm/IntelliJ IDEA integration:
1. Go to `Preferences or Settings -> Tools -> Black`
2. Configure:
- Python interpreter
- Use Black formatter: `On code reformat` & optionally `On save`
- Arguments: `--line-length 120`

### Sort Imports

```shell
python -m isort ucapi/.
```
