#!/usr/bin/env python3
"""
Compile protobuf definitions in ucapi/proto to Python modules.

This script is intended for maintainers. It generates Python files from the
`.proto` sources and writes them next to the source files so they can be
committed to version control. The library will then import the generated
modules directly without re-generating them on each build.

Usage:
  - Run from project root:
      python3 scripts/compile_protos.py
  - Optional flags:
      --src DIR     Directory containing .proto files (default: ucapi/proto)
      --out DIR     Output directory for generated files (default: ucapi/proto)

The script prefers `grpc_tools.protoc` if available, and falls back to a
system `protoc` executable. It also attempts to generate PEP 561 type stubs
(`--pyi_out`) when supported.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


def find_proto_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.glob("*.proto") if p.is_file())


def run_with_grpc_tools(protos: Iterable[Path], src_dir: Path, out_dir: Path) -> int:
    try:
        from grpc_tools import protoc  # type: ignore
    except Exception:
        return 127

    args_base: list[str] = [
        "protoc",
        f"-I{src_dir}",
        f"--python_out={out_dir}",
    ]

    # Try to generate .pyi stubs if supported by installed protobuf
    try:
        # Modern protobuf supports --pyi_out
        args_with_pyi = args_base + [f"--pyi_out={out_dir}"] + [str(p.name) for p in protos]
        return int(protoc.main(args_with_pyi) != 0)
    except Exception:
        args = args_base + [str(p.name) for p in protos]
        return int(protoc.main(args) != 0)


def run_with_system_protoc(
    protos: Iterable[Path], src_dir: Path, out_dir: Path
) -> int:
    exe = shutil.which("protoc")
    if not exe:
        return 127

    cmd_base: list[str] = [
        exe,
        f"-I{src_dir}",
        f"--python_out={out_dir}",
    ]

    # Try --pyi_out if supported (ignore error if not)
    rc = subprocess.call(cmd_base + [f"--pyi_out={out_dir}"] + [str(p) for p in protos])
    if rc == 0:
        return 0

    return subprocess.call(cmd_base + [str(p) for p in protos])


def compile_dir(src_dir: Path, out_dir: Path) -> int:
    protos = find_proto_files(src_dir)
    if not protos:
        print(f"No .proto files found in {src_dir}", file=sys.stderr)
        return 0

    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    # Prefer grpc_tools.protoc (works cross-platform in Python envs)
    rc = run_with_grpc_tools(protos, src_dir, out_dir)
    if rc == 0:
        return 0

    # Fallback: system protoc
    rc = run_with_system_protoc(protos, src_dir, out_dir)
    if rc == 0:
        return 0

    print(
        "Failed to compile protos. Please install either grpcio-tools (pip install grpcio-tools) "
        "or ensure 'protoc' is available on PATH.",
        file=sys.stderr,
    )
    return 1


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_src = Path("ucapi/proto")
    parser.add_argument(
        "--src",
        type=Path,
        default=default_src,
        help="Directory containing .proto files (default: ucapi/proto)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=default_src,
        help="Output directory for generated files (default: ucapi/proto)",
    )

    args = parser.parse_args(argv)

    src_dir = args.src.resolve()
    out_dir = args.out.resolve()

    if not src_dir.exists():
        print(f"Source directory does not exist: {src_dir}", file=sys.stderr)
        return 2

    # Change working dir to src_dir so protoc includes work as expected
    cwd = os.getcwd()
    try:
        os.chdir(src_dir)
        return compile_dir(Path("."), out_dir)
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    try:
        import shutil  # imported late to keep top clean and avoid pylint complaints
    except Exception:  # pragma: no cover - shutil is always available in stdlib
        shutil = None  # type: ignore
    sys.exit(main())
