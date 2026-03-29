import pytest
import pyopentui


def test_optimized_buffer_create():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    assert buffer.width == 80
    assert buffer.height == 24


def test_optimized_buffer_clear():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.clear(1, 0, 0, 1)


def test_optimized_buffer_draw_text():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.draw_text("Hello World", 0, 0)


def test_optimized_buffer_fill_rect():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.fill_rect(0, 0, 10, 10, pyopentui.RGBA(1, 1, 1, 1))


def test_text_buffer_append():
    tb = pyopentui.TextBuffer()
    tb.append("Hello World")
    assert tb.get_text() == "Hello World"


def test_edit_buffer_create():
    eb = pyopentui.EditBuffer()
    assert eb is not None


def test_edit_buffer_cursor_movement():
    eb = pyopentui.EditBuffer()
    eb.insert_text("Hello World")
    for _ in range(11):
        eb.move_cursor_right()
    row, col = eb.get_cursor()
    assert col == 11
    for _ in range(11):
        eb.move_cursor_left()
    row, col = eb.get_cursor()
    assert col == 0


def test_edit_buffer_insert_text():
    eb = pyopentui.EditBuffer()
    eb.insert_text("Hello")
    assert eb.get_text() == "Hello"


def test_editor_view_create():
    eb = pyopentui.EditBuffer()
    view = pyopentui.EditorView(eb, 80, 24)
    assert view is not None


def test_native_span_feed():
    feed = pyopentui.NativeSpanFeed()
    feed.write("Hello")
    feed.commit()
    stats = feed.get_stats()
    assert "bytes_written" in stats
    assert stats["bytes_written"] > 0


def test_get_allocator_stats():
    stats = pyopentui.get_allocator_stats()
    assert "total_requested_bytes" in stats
    assert "active_allocations" in stats


def test_get_build_options():
    opts = pyopentui.get_build_options()
    assert "gpa_safe_stats" in opts
    assert "gpa_memory_limit_tracking" in opts
