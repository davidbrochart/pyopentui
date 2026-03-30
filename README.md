# pyopentui

[![Test](https://github.com/davidbrochart/pyopentui/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/davidbrochart/pyopentui/actions/workflows/test.yml)

Python bindings for OpenTUI - a native terminal UI core written in Zig.

## Installation

```bash
pip install pyopentui
```

## Development

```bash
# Get the latest opentui code:
curl -L -o opentui.zip https://github.com/anomalyco/opentui/archive/refs/tags/v0.1.92.zip
unzip opentui.zip

# Compile the core Zig code:
cd opentui-0.1.92/packages/core/src/zig
zig build -Doptimize=ReleaseSafe

# Copy the shared library in the lib directory:
cd -
mkdir src/pyopentui/lib
cp opentui-0.1.92/packages/core/src/zig/lib/*/* src/pyopentui/lib

# Install with dev dependencies:
pip install -e . --group dev
```

Run tests:

```bash
pytest -v tests
```

Build the package:

```bash
pip install build
python -m build --wheel
python -m build --sdist
mv dist/pyopentui-0.1.0-py3-none-any.whl dist/pyopentui-0.1.0-py3-none-linux_x86_64.whl
```

## License

MIT
