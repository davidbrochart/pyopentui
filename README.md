# pyopentui

[![Test](https://github.com/davidbrochart/pyopentui/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/davidbrochart/pyopentui/actions/workflows/test.yml)

Python bindings for OpenTUI - a native terminal UI core written in Zig.

## Installation

```bash
pip install pyopentui
```

## Development

Install [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html), then:

```bash
# Create a conda environment and install pip and zig:
git clean -fdx
micromamba create -n pyopentui -y
micromamba activate pyopentui
micromamba install pip zig -y

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

# Install the package in editable mode:
pip install -e . --group dev
```

Run tests:

```bash
pytest -v tests
```

Build the package:

```bash
python -m build --wheel
python -m build --sdist
python rename_wheel.py
```
