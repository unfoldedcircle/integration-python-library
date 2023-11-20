# Code Style

This project uses the [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/) as coding convention, with the
following customization:

- Code line length: 88
- Use double quotes as default (don't mix and match for simple quoting, checked with pylint).
- Configuration:
  - `pyproject.toml` for pylint and isort
  - `setup.cfg` for flake8

## Tooling

Install all code linting tools:

```shell
pip3 install -r requirements.txt -r test-requirements.txt
```

Note: once <https://github.com/pypa/pip/issues/11440> is implemented, the requirements files can be removed and
`pyproject.toml` is sufficient.

### Linting

```shell
python3 -m pylint ucapi
```

- The tool is configured in `.pylintrc`.

Linting integration in PyCharm/IntelliJ IDEA:
1. Install plugin [Pylint](https://plugins.jetbrains.com/plugin/11084-pylint)
2. Open Pylint window and run a scan: `Check Module` or `Check Current File`

### Sort Imports

Import statements must be sorted with [isort](https://pycqa.github.io/isort/):

```shell
python3 -m isort ucapi/.
```

- The tool is configured in `pyproject.toml` to use the `black` code-formatting profile.

### Format Code

Source code is formatted with the [Black code formatting tool](https://github.com/psf/black):

```shell
python3 -m black ucapi
```

PyCharm/IntelliJ IDEA integration:
1. Go to `Preferences or Settings -> Tools -> Black`
2. Configure:
- Python interpreter
- Use Black formatter: `On code reformat` & optionally `On save`

## Verify

The following tests are run as GitHub action for each push on the main branch and for pull requests.
They can also be run anytime on a local developer machine:
```shell
python3 -m pylint ucapi
python3 -m flake8 ucapi --count --show-source --statistics
python3 -m isort ucapi/. --check --verbose 
python3 -m black ucapi --check --verbose
```
