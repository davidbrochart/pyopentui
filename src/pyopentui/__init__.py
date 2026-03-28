from importlib.metadata import version

from .core import (
    CliRenderer,
    OptimizedBuffer,
    TextBuffer,
    EditBuffer,
    EditorView,
    NativeSpanFeed,
    RGBA,
    CursorStyle,
    create_renderer,
    get_library_path,
    get_allocator_stats,
    get_build_options,
)

__version__ = version("pyopentui")

__all__ = [
    "CliRenderer",
    "OptimizedBuffer",
    "TextBuffer",
    "EditBuffer",
    "EditorView",
    "NativeSpanFeed",
    "RGBA",
    "CursorStyle",
    "create_renderer",
    "get_library_path",
    "get_allocator_stats",
    "get_build_options",
]
