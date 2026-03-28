import pytest
import pyopentui


def test_optimized_buffer_create():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    assert buffer.width == 80
    assert buffer.height == 24


def test_optimized_buffer_clear():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.clear(r=0.1, g=0.1, b=0.2)


def test_optimized_buffer_draw_text():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.draw_text("Hello, OpenTUI!", x=5, y=5)


def test_optimized_buffer_fill_rect():
    buffer = pyopentui.OptimizedBuffer(80, 24)
    buffer.fill_rect(x=10, y=10, width=20, height=5)


def test_text_buffer_append():
    tb = pyopentui.TextBuffer()
    tb.append("Line 1\n")
    tb.append("Line 2\n")
    tb.append("Line 3")
    assert tb.length == 18
    assert tb.line_count == 3


def test_edit_buffer_create():
    eb = pyopentui.EditBuffer()
    eb.set_text("Hello EditBuffer")
    assert eb.get_cursor() == (0, 0)


def test_edit_buffer_cursor_movement():
    eb = pyopentui.EditBuffer()
    eb.set_text("Hello")
    eb.move_cursor_right()
    assert eb.get_cursor() == (0, 1)


def test_edit_buffer_insert_text():
    eb = pyopentui.EditBuffer()
    eb.set_text("Hello")
    eb.move_cursor_right()
    eb.insert_text(" - inserted")
    assert eb.get_cursor() == (0, 12)


def test_editor_view_create():
    eb = pyopentui.EditBuffer()
    eb.set_text("Line 1\nLine 2\nLine 3")
    view = pyopentui.EditorView(eb, 80, 24)
    assert view.virtual_line_count > 0


def test_native_span_feed():
    feed = pyopentui.NativeSpanFeed()
    feed.write("test input")
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
