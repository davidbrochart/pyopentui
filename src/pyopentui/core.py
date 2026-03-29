from __future__ import annotations

import ctypes
import os
import sys
from ctypes import (
    POINTER,
    c_void_p,
    c_uint32,
    c_uint64,
    c_uint8,
    c_int8,
    c_int32,
    c_int64,
    c_float,
    c_bool,
    c_char,
    c_char_p,
    c_size_t,
    Structure,
    Array,
    CDLL,
    CFUNCTYPE,
    cast,
    pointer,
    create_string_buffer,
    byref,
)
from enum import IntEnum
from pathlib import Path
from typing import Optional, Any


class LibraryLoader:
    _lib: Optional[CDLL] = None

    @classmethod
    def get_library(cls) -> CDLL:
        if cls._lib is None:
            cls._lib = cls._load_library()
        return cls._lib

    @classmethod
    def _load_library(cls) -> CDLL:
        lib_path = get_library_path()
        return CDLL(lib_path)


def get_library_path() -> str:
    script_dir = Path(__file__).parent
    lib_dir = script_dir / "lib"

    if sys.platform == "darwin":
        lib_name = "libopentui.dylib"
    elif sys.platform == "win32":
        lib_name = "opentui.dll"
    else:
        lib_name = "libopentui.so"

    lib_path = lib_dir / lib_name
    if lib_path.exists():
        return str(lib_path)

    opentui_dir = (
        Path(__file__).parent.parent
        / "opentui"
        / "packages"
        / "core"
        / "src"
        / "zig"
        / "lib"
        / "x86_64-linux"
        / "libopentui.so"
    )
    if opentui_dir.exists():
        return str(opentui_dir)

    raise FileNotFoundError(f"Could not find opentui library at {lib_path}")


class RGBA(ctypes.Structure):
    _fields_ = [
        ("r", c_float),
        ("g", c_float),
        ("b", c_float),
        ("a", c_float),
    ]

    def __init__(self, r: float = 0, g: float = 0, b: float = 0, a: float = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def create_ptr(
        r: float = 0, g: float = 0, b: float = 0, a: float = 1.0
    ) -> ctypes.Array:
        color = RGBA(r, g, b, a)
        return (c_float * 4)(color.r, color.g, color.b, color.a)


class CursorStyle(IntEnum):
    BLOCK = 0
    LINE = 1
    UNDERLINE = 2
    DEFAULT = 3


class TerminalCapabilities(Structure):
    _fields_ = [
        ("kitty_keyboard", c_uint8),
        ("kitty_graphics", c_uint8),
        ("rgb", c_uint8),
        ("unicode", c_uint8),
        ("sgr_pixels", c_uint8),
        ("color_scheme_updates", c_uint8),
        ("explicit_width", c_uint8),
        ("scaled_text", c_uint8),
        ("sixel", c_uint8),
        ("focus_tracking", c_uint8),
        ("sync", c_uint8),
        ("bracketed_paste", c_uint8),
        ("hyperlinks", c_uint8),
        ("osc52", c_uint8),
        ("explicit_cursor_positioning", c_uint8),
        ("term_name", c_char_p),
        ("term_name_len", c_size_t),
        ("term_version", c_char_p),
        ("term_version_len", c_size_t),
        ("term_from_xtversion", c_uint8),
    ]


class CursorState(Structure):
    _fields_ = [
        ("x", c_uint32),
        ("y", c_uint32),
        ("visible", c_uint8),
        ("style", c_uint8),
        ("blinking", c_uint8),
        ("r", c_float),
        ("g", c_float),
        ("b", c_float),
        ("a", c_float),
    ]


class BuildOptions(Structure):
    _fields_ = [
        ("gpa_safe_stats", c_uint8),
        ("gpa_memory_limit_tracking", c_uint8),
    ]


class AllocatorStats(Structure):
    _fields_ = [
        ("total_requested_bytes", c_uint64),
        ("active_allocations", c_uint64),
        ("small_allocations", c_uint64),
        ("large_allocations", c_uint64),
        ("requested_bytes_valid", c_uint8),
    ]


class OutputSlice(Structure):
    _fields_ = [
        ("ptr", c_void_p),
        ("len", c_size_t),
    ]


class ExternalMeasureResult(Structure):
    _fields_ = [
        ("line_count", c_uint32),
        ("width_cols_max", c_uint32),
    ]


class ExternalLineInfo(Structure):
    _fields_ = [
        ("start_cols", c_void_p),
        ("start_cols_len", c_uint32),
        ("width_cols", c_void_p),
        ("width_cols_len", c_uint32),
        ("sources", c_void_p),
        ("sources_len", c_uint32),
        ("wraps", c_void_p),
        ("wraps_len", c_uint32),
        ("width_cols_max", c_uint32),
    ]


class NativeSpanFeedOptions(Structure):
    _fields_ = [
        ("chunk_size", c_uint32),
        ("initial_chunks", c_uint32),
        ("max_bytes", c_uint64),
        ("growth_policy", c_uint8),
        ("auto_commit_on_full", c_uint8),
        ("span_queue_capacity", c_uint32),
    ]


class NativeSpanFeedStats(Structure):
    _fields_ = [
        ("bytes_written", c_uint64),
        ("spans_committed", c_uint64),
        ("chunks", c_uint32),
        ("pending_spans", c_uint32),
    ]


class SpanInfo(Structure):
    _fields_ = [
        ("chunk_ptr", c_void_p),
        ("offset", c_uint32),
        ("len", c_uint32),
        ("chunk_index", c_uint32),
        ("reserved", c_uint32),
    ]


def _setup_functions(lib: CDLL) -> None:
    lib.createRenderer.argtypes = [c_uint32, c_uint32, c_bool, c_bool]
    lib.createRenderer.restype = c_void_p

    lib.destroyRenderer.argtypes = [c_void_p]
    lib.destroyRenderer.restype = None

    lib.render.argtypes = [c_void_p, c_bool]
    lib.render.restype = None

    lib.resizeRenderer.argtypes = [c_void_p, c_uint32, c_uint32]
    lib.resizeRenderer.restype = None

    lib.getNextBuffer.argtypes = [c_void_p]
    lib.getNextBuffer.restype = c_void_p

    lib.getCurrentBuffer.argtypes = [c_void_p]
    lib.getCurrentBuffer.restype = c_void_p

    lib.createOptimizedBuffer.argtypes = [
        c_uint32,
        c_uint32,
        c_bool,
        c_uint8,
        c_char_p,
        c_size_t,
    ]
    lib.createOptimizedBuffer.restype = c_void_p

    lib.destroyOptimizedBuffer.argtypes = [c_void_p]
    lib.destroyOptimizedBuffer.restype = None

    lib.bufferClear.argtypes = [c_void_p, POINTER(c_float)]
    lib.bufferClear.restype = None

    lib.bufferDrawText.argtypes = [
        c_void_p,
        c_char_p,
        c_uint32,
        c_uint32,
        c_uint32,
        POINTER(c_float),
        POINTER(c_float),
        c_uint32,
    ]
    lib.bufferDrawText.restype = None

    lib.bufferSetCell.argtypes = [
        c_void_p,
        c_uint32,
        c_uint32,
        c_uint32,
        POINTER(c_float),
        POINTER(c_float),
        c_uint32,
    ]
    lib.bufferSetCell.restype = None

    lib.bufferFillRect.argtypes = [
        c_void_p,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        POINTER(c_float),
    ]
    lib.bufferFillRect.restype = None

    lib.bufferResize.argtypes = [c_void_p, c_uint32, c_uint32]
    lib.bufferResize.restype = None

    lib.getBufferWidth.argtypes = [c_void_p]
    lib.getBufferWidth.restype = c_uint32

    lib.getBufferHeight.argtypes = [c_void_p]
    lib.getBufferHeight.restype = c_uint32

    lib.createTextBuffer.argtypes = [c_uint8]
    lib.createTextBuffer.restype = c_void_p

    lib.destroyTextBuffer.argtypes = [c_void_p]
    lib.destroyTextBuffer.restype = None

    lib.textBufferAppend.argtypes = [c_void_p, c_char_p, c_uint32]
    lib.textBufferAppend.restype = None

    lib.textBufferGetLength.argtypes = [c_void_p]
    lib.textBufferGetLength.restype = c_uint32

    lib.textBufferGetLineCount.argtypes = [c_void_p]
    lib.textBufferGetLineCount.restype = c_uint32

    lib.textBufferGetPlainText.argtypes = [
        c_void_p,
        c_void_p,
        c_size_t,
    ]
    lib.textBufferGetPlainText.restype = c_size_t

    lib.createEditBuffer.argtypes = [c_uint8]
    lib.createEditBuffer.restype = c_void_p

    lib.destroyEditBuffer.argtypes = [c_void_p]
    lib.destroyEditBuffer.restype = None

    lib.editBufferSetText.argtypes = [c_void_p, c_char_p, c_uint32]
    lib.editBufferSetText.restype = None

    lib.editBufferInsertText.argtypes = [c_void_p, c_char_p, c_uint32]
    lib.editBufferInsertText.restype = None

    lib.editBufferMoveCursorLeft.argtypes = [c_void_p]
    lib.editBufferMoveCursorLeft.restype = None

    lib.editBufferMoveCursorRight.argtypes = [c_void_p]
    lib.editBufferMoveCursorRight.restype = None

    lib.editBufferMoveCursorUp.argtypes = [c_void_p]
    lib.editBufferMoveCursorUp.restype = None

    lib.editBufferMoveCursorDown.argtypes = [c_void_p]
    lib.editBufferMoveCursorDown.restype = None

    lib.editBufferGetCursor.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32)]
    lib.editBufferGetCursor.restype = None

    lib.editBufferGetText.argtypes = [c_void_p, c_void_p, c_size_t]
    lib.editBufferGetText.restype = c_size_t

    lib.editBufferUndo.argtypes = [c_void_p]
    lib.editBufferUndo.restype = c_bool

    lib.editBufferRedo.argtypes = [c_void_p]
    lib.editBufferRedo.restype = c_bool

    lib.editBufferCanUndo.argtypes = [c_void_p]
    lib.editBufferCanUndo.restype = c_bool

    lib.editBufferCanRedo.argtypes = [c_void_p]
    lib.editBufferCanRedo.restype = c_bool

    lib.createEditorView.argtypes = [c_void_p, c_uint32, c_uint32]
    lib.createEditorView.restype = c_void_p

    lib.destroyEditorView.argtypes = [c_void_p]
    lib.destroyEditorView.restype = None

    lib.editorViewSetViewport.argtypes = [
        c_void_p,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        c_bool,
    ]
    lib.editorViewSetViewport.restype = None

    lib.editorViewGetVirtualLineCount.argtypes = [c_void_p]
    lib.editorViewGetVirtualLineCount.restype = c_uint32

    lib.setupTerminal.argtypes = [c_void_p, c_bool]
    lib.setupTerminal.restype = None

    lib.enableMouse.argtypes = [c_void_p, c_bool]
    lib.enableMouse.restype = None

    lib.disableMouse.argtypes = [c_void_p]
    lib.disableMouse.restype = None

    lib.setCursorPosition.argtypes = [c_void_p, c_int32, c_int32, c_bool]
    lib.setCursorPosition.restype = None

    lib.setTerminalTitle.argtypes = [c_void_p, c_char_p, c_uint32]
    lib.setTerminalTitle.restype = None

    lib.copyToClipboardOSC52.argtypes = [c_void_p, c_uint8, c_char_p, c_uint32]
    lib.copyToClipboardOSC52.restype = c_bool

    lib.setBackgroundColor.argtypes = [c_void_p, POINTER(c_float)]
    lib.setBackgroundColor.restype = None

    lib.getLastOutputForTest.argtypes = [c_void_p, POINTER(OutputSlice)]
    lib.getLastOutputForTest.restype = None

    lib.createNativeSpanFeed.argtypes = [POINTER(NativeSpanFeedOptions)]
    lib.createNativeSpanFeed.restype = c_void_p

    lib.destroyNativeSpanFeed.argtypes = [c_void_p]
    lib.destroyNativeSpanFeed.restype = None

    lib.streamWrite.argtypes = [c_void_p, c_char_p, c_uint64]
    lib.streamWrite.restype = c_int32

    lib.streamCommit.argtypes = [c_void_p]
    lib.streamCommit.restype = c_int32

    lib.streamDrainSpans.argtypes = [c_void_p, POINTER(SpanInfo), c_uint32]
    lib.streamDrainSpans.restype = c_uint32

    lib.streamGetStats.argtypes = [c_void_p, POINTER(NativeSpanFeedStats)]
    lib.streamGetStats.restype = None

    lib.getAllocatorStats.argtypes = [POINTER(AllocatorStats)]
    lib.getAllocatorStats.restype = None

    lib.getBuildOptions.argtypes = [POINTER(BuildOptions)]
    lib.getBuildOptions.restype = None


_lib = LibraryLoader.get_library()
_setup_functions(_lib)


class CliRenderer:
    def __init__(
        self, width: int, height: int, testing: bool = False, remote: bool = False
    ):
        self._ptr = _lib.createRenderer(width, height, testing, remote)
        if not self._ptr:
            raise RuntimeError("Failed to create renderer")

    def __del__(self):
        if self._ptr:
            _lib.destroyRenderer(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    def render(self, force: bool = False) -> None:
        _lib.render(self._ptr, force)

    def resize(self, width: int, height: int) -> None:
        _lib.resizeRenderer(self._ptr, width, height)

    def get_next_buffer(self) -> Optional["OptimizedBuffer"]:
        buf_ptr = _lib.getNextBuffer(self._ptr)
        if buf_ptr:
            return OptimizedBuffer._from_ptr(buf_ptr)
        return None

    def get_current_buffer(self) -> Optional["OptimizedBuffer"]:
        buf_ptr = _lib.getCurrentBuffer(self._ptr)
        if buf_ptr:
            return OptimizedBuffer._from_ptr(buf_ptr)
        return None

    def set_background_color(
        self, r: float = 0, g: float = 0, b: float = 0, a: float = 1.0
    ) -> None:
        color_ptr = RGBA.create_ptr(r, g, b, a)
        _lib.setBackgroundColor(self._ptr, color_ptr)

    def setup_terminal(self, use_alternate_screen: bool = True) -> None:
        _lib.setupTerminal(self._ptr, use_alternate_screen)

    def enable_mouse(self, enable_movement: bool = True) -> None:
        _lib.enableMouse(self._ptr, enable_movement)

    def disable_mouse(self) -> None:
        _lib.disableMouse(self._ptr)

    def set_cursor_position(self, x: int, y: int, visible: bool = True) -> None:
        _lib.setCursorPosition(self._ptr, x, y, visible)

    def set_terminal_title(self, title: str) -> None:
        title_bytes = title.encode("utf-8")
        _lib.setTerminalTitle(self._ptr, title_bytes, len(title_bytes))

    def get_last_output(self) -> str:
        output = OutputSlice()
        _lib.getLastOutputForTest(self._ptr, byref(output))
        if output.len > 0:
            return ctypes.string_at(output.ptr, output.len).decode("utf-8")
        return ""


class OptimizedBuffer:
    def __init__(
        self,
        width: int,
        height: int,
        respect_alpha: bool = False,
        width_method: int = 0,
        id: str = "unnamed buffer",
    ):
        self._id_bytes = bytearray(id.encode("utf-8"))
        self._ptr = _lib.createOptimizedBuffer(
            width,
            height,
            respect_alpha,
            width_method,
            bytes(self._id_bytes),
            len(self._id_bytes),
        )
        if not self._ptr:
            raise RuntimeError("Failed to create buffer")
        self._owns_memory = True

    @staticmethod
    def _from_ptr(ptr: c_void_p) -> "OptimizedBuffer":
        buf = object.__new__(OptimizedBuffer)
        buf._ptr = ptr
        buf._owns_memory = False
        return buf

    def __del__(self):
        if self._ptr and self._owns_memory:
            _lib.destroyOptimizedBuffer(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    @property
    def width(self) -> int:
        return _lib.getBufferWidth(self._ptr)

    @property
    def height(self) -> int:
        return _lib.getBufferHeight(self._ptr)

    def clear(self, r: float = 0, g: float = 0, b: float = 0, a: float = 1.0) -> None:
        color_ptr = RGBA.create_ptr(r, g, b, a)
        _lib.bufferClear(self._ptr, color_ptr)

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = 0,
    ) -> None:
        text_bytes = text.encode("utf-8")
        fg_ptr = (
            RGBA.create_ptr(1, 1, 1, 1)
            if fg is None
            else RGBA.create_ptr(fg.r, fg.g, fg.b, fg.a)
        )
        bg_ptr = (
            RGBA.create_ptr(0, 0, 0, 1)
            if bg is None
            else RGBA.create_ptr(bg.r, bg.g, bg.b, bg.a)
        )
        _lib.bufferDrawText(
            self._ptr, text_bytes, len(text_bytes), x, y, fg_ptr, bg_ptr, attributes
        )

    def set_cell(
        self,
        x: int,
        y: int,
        char: int,
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = 0,
    ) -> None:
        fg_ptr = (
            RGBA.create_ptr(1, 1, 1, 1)
            if fg is None
            else RGBA.create_ptr(fg.r, fg.g, fg.b, fg.a)
        )
        bg_ptr = (
            RGBA.create_ptr(0, 0, 0, 1)
            if bg is None
            else RGBA.create_ptr(bg.r, bg.g, bg.b, bg.a)
        )
        _lib.bufferSetCell(self._ptr, x, y, char, fg_ptr, bg_ptr, attributes)

    def fill_rect(
        self, x: int, y: int, width: int, height: int, bg: Optional[RGBA] = None
    ) -> None:
        bg_ptr = (
            RGBA.create_ptr(0, 0, 0, 1)
            if bg is None
            else RGBA.create_ptr(bg.r, bg.g, bg.b, bg.a)
        )
        _lib.bufferFillRect(self._ptr, x, y, width, height, bg_ptr)

    def resize(self, width: int, height: int) -> None:
        _lib.bufferResize(self._ptr, width, height)


class TextBuffer:
    def __init__(self, width_method: int = 0):
        self._ptr = _lib.createTextBuffer(width_method)
        if not self._ptr:
            raise RuntimeError("Failed to create text buffer")

    def __del__(self):
        if self._ptr:
            _lib.destroyTextBuffer(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    def append(self, text: str) -> None:
        text_bytes = text.encode("utf-8")
        _lib.textBufferAppend(self._ptr, text_bytes, len(text_bytes))

    @property
    def length(self) -> int:
        return _lib.textBufferGetLength(self._ptr)

    @property
    def line_count(self) -> int:
        return _lib.textBufferGetLineCount(self._ptr)

    def get_text(self) -> str:
        max_len = 4096
        buffer = bytearray(max_len)
        addr = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
        length = _lib.textBufferGetPlainText(self._ptr, addr, max_len)
        if length == 0:
            return ""
        return bytes(buffer[:length]).decode("utf-8")


class EditBuffer:
    def __init__(self, width_method: int = 0):
        self._ptr = _lib.createEditBuffer(width_method)
        if not self._ptr:
            raise RuntimeError("Failed to create edit buffer")

    def __del__(self):
        if self._ptr:
            _lib.destroyEditBuffer(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    def set_text(self, text: str) -> None:
        text_bytes = text.encode("utf-8")
        _lib.editBufferSetText(self._ptr, text_bytes, len(text_bytes))

    def insert_text(self, text: str) -> None:
        text_bytes = text.encode("utf-8")
        _lib.editBufferInsertText(self._ptr, text_bytes, len(text_bytes))

    def move_cursor_left(self) -> None:
        _lib.editBufferMoveCursorLeft(self._ptr)

    def move_cursor_right(self) -> None:
        _lib.editBufferMoveCursorRight(self._ptr)

    def move_cursor_up(self) -> None:
        _lib.editBufferMoveCursorUp(self._ptr)

    def move_cursor_down(self) -> None:
        _lib.editBufferMoveCursorDown(self._ptr)

    def get_cursor(self) -> tuple[int, int]:
        row = c_uint32()
        col = c_uint32()
        _lib.editBufferGetCursor(self._ptr, byref(row), byref(col))
        return (row.value, col.value)

    def get_text(self) -> str:
        max_len = 4096
        buffer = bytearray(max_len)
        addr = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
        length = _lib.editBufferGetText(self._ptr, addr, max_len)
        if length == 0:
            return ""
        return bytes(buffer[:length]).decode("utf-8")

    def undo(self) -> bool:
        return bool(_lib.editBufferUndo(self._ptr))

    def redo(self) -> bool:
        return bool(_lib.editBufferRedo(self._ptr))

    @property
    def can_undo(self) -> bool:
        return bool(_lib.editBufferCanUndo(self._ptr))

    @property
    def can_redo(self) -> bool:
        return bool(_lib.editBufferCanRedo(self._ptr))


class EditorView:
    def __init__(
        self, edit_buffer: EditBuffer, viewport_width: int, viewport_height: int
    ):
        self._ptr = _lib.createEditorView(
            edit_buffer.ptr, viewport_width, viewport_height
        )
        if not self._ptr:
            raise RuntimeError("Failed to create editor view")
        self._edit_buffer = edit_buffer

    def __del__(self):
        if self._ptr:
            _lib.destroyEditorView(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    def set_viewport(
        self, x: int, y: int, width: int, height: int, move_cursor: bool = True
    ) -> None:
        _lib.editorViewSetViewport(self._ptr, x, y, width, height, move_cursor)

    @property
    def virtual_line_count(self) -> int:
        return _lib.editorViewGetVirtualLineCount(self._ptr)


class NativeSpanFeed:
    def __init__(
        self,
        chunk_size: int = 64 * 1024,
        initial_chunks: int = 2,
        max_bytes: int = 0,
        growth_policy: int = 0,
        auto_commit_on_full: bool = True,
        span_queue_capacity: int = 0,
    ):

        options = NativeSpanFeedOptions(
            chunk_size=chunk_size,
            initial_chunks=initial_chunks,
            max_bytes=max_bytes,
            growth_policy=growth_policy,
            auto_commit_on_full=1 if auto_commit_on_full else 0,
            span_queue_capacity=span_queue_capacity,
        )
        self._ptr = _lib.createNativeSpanFeed(byref(options))
        if not self._ptr:
            raise RuntimeError("Failed to create native span feed")

    def __del__(self):
        if self._ptr:
            _lib.destroyNativeSpanFeed(self._ptr)
            self._ptr = None

    @property
    def ptr(self) -> c_void_p:
        return self._ptr

    def write(self, data: str) -> int:
        data_bytes = data.encode("utf-8")
        return _lib.streamWrite(self._ptr, data_bytes, len(data_bytes))

    def commit(self) -> int:
        return _lib.streamCommit(self._ptr)

    def drain_spans(self, max_spans: int = 1024) -> list[SpanInfo]:
        spans = (SpanInfo * max_spans)()
        count = _lib.streamDrainSpans(self._ptr, spans, max_spans)
        return [spans[i] for i in range(count)]

    def get_stats(self) -> dict:
        stats = NativeSpanFeedStats()
        _lib.streamGetStats(self._ptr, byref(stats))
        return {
            "bytes_written": stats.bytes_written,
            "spans_committed": stats.spans_committed,
            "chunks": stats.chunks,
            "pending_spans": stats.pending_spans,
        }


def create_renderer(
    width: int, height: int, testing: bool = False, remote: bool = False
) -> CliRenderer:
    return CliRenderer(width, height, testing, remote)


def get_allocator_stats() -> dict:
    stats = AllocatorStats()
    _lib.getAllocatorStats(byref(stats))
    return {
        "total_requested_bytes": stats.total_requested_bytes,
        "active_allocations": stats.active_allocations,
        "small_allocations": stats.small_allocations,
        "large_allocations": stats.large_allocations,
        "requested_bytes_valid": bool(stats.requested_bytes_valid),
    }


def get_build_options() -> dict:
    options = BuildOptions()
    _lib.getBuildOptions(byref(options))
    return {
        "gpa_safe_stats": bool(options.gpa_safe_stats),
        "gpa_memory_limit_tracking": bool(options.gpa_memory_limit_tracking),
    }
