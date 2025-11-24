# Development Setup

This library requires Python 3.10 or newer.

Install build tools:
```shell
pip3 install build setuptools setuptools_scm
```

Build:
```shell
python -m build
```

Local installation:
```shell
pip3 install --force-reinstall dist/ucapi-$VERSION-py3-none-any.whl
```

## Protobuf

1. Optional (recommended): install the Python plugin toolchain for consistent results:
   ```bash
   python3 -m pip install --upgrade grpcio-tools protobuf
   ```
2. From the project root, run:
   ```bash
   python3 scripts/compile_protos.py
   ```
   - This will generate `ucapi/proto/ucr_integration_voice_pb2.py` (and `.pyi` if supported).
3. Add and commit the generated files to Git:
   ```bash
   git add ucapi/proto/ucr_integration_voice_pb2.py ucapi/proto/ucr_integration_voice_pb2.pyi || true
   git commit -m "Generate protobuf Python modules for voice integration"
   ```

Notes:
- The library does not re-generate at build time; we ship the generated code with the package.
- If you prefer using system `protoc`, ensure it’s on `PATH`; the script will fall back to it automatically.
- Imports at runtime (if/when needed) will look like:
  ```python
  from ucapi.proto import ucr_integration_voice_pb2 as voice_pb2
  ```
