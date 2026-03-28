# pyopentui

Python bindings for OpenTUI - a native terminal UI core written in Zig.

## Installation

```bash
pip install pyopentui
```

## Usage

```python
import pyopentui

# Create a buffer for rendering
buffer = pyopentui.OptimizedBuffer(80, 24)
buffer.clear(r=0.1, g=0.1, b=0.2)
buffer.draw_text("Hello, OpenTUI!", x=5, y=5)

# Work with text
tb = pyopentui.TextBuffer()
tb.append("Hello World")

# Work with editable text
eb = pyopentui.EditBuffer()
eb.set_text("Editable text")
eb.move_cursor_right()
eb.insert_text(" - inserted")

# Create a viewport-managed editor
eb = pyopentui.EditBuffer()
eb.set_text("Line 1\nLine 2\nLine 3")
view = pyopentui.EditorView(eb, 80, 24)

# Handle input streams
feed = pyopentui.NativeSpanFeed()
feed.write("user input")
feed.commit()
```

## Development

Get the latest `opentui` code:
```bash
curl -L -o opentui.zip https://github.com/anomalyco/opentui/archive/refs/tags/v0.1.92.zip
unzip opentui.zip
```

Compile the core Zig code:
```bash
cd opentui-0.1.92/packages/core/src/zig
zig build
```

Copy the shared library in the `lib` directory:
```bash
cd -
mkdir src/pyopentui/lib
cp opentui-0.1.92/packages/core/src/zig/lib/*/libopentui.so src/pyopentui/lib
```

Install with dev dependencies:
```bash
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
