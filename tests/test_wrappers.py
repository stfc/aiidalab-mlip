"""Test error handling decorators."""

from unittest.mock import MagicMock
from aiidalab_mlip.wrappers import handle_errors, err_handler


class DummyWidgetWithStatus:
    """Mock widget having a status attribute."""

    def __init__(self):
        self.status = MagicMock()

    @handle_errors
    def successful_action(self, x: int) -> int:
        return x * 2

    @handle_errors
    def failing_action(self):
        raise ValueError("Something went wrong")


def test_handle_errors_success():
    """Test handle_errors returns result when no error occurs."""
    widget = DummyWidgetWithStatus()
    result = widget.successful_action(5)
    assert result == 10
    widget.status.failure.assert_not_called()


def test_handle_errors_failure():
    """Test handle_errors catches exceptions and logs to status."""
    widget = DummyWidgetWithStatus()
    result = widget.failing_action()
    assert result is None
    widget.status.failure.assert_called_once()
    msg = widget.status.failure.call_args[0][0]
    assert "✗ Error in failing_action:" in msg
    assert "ValueError: Something went wrong" in msg


def test_err_handler_context_manager():
    """Test err_handler context manager directly."""
    widget = DummyWidgetWithStatus()
    with err_handler(widget, "test_operation"):
        raise RuntimeError("boom")
    widget.status.failure.assert_called_once()
    assert "✗ Error in test_operation:" in widget.status.failure.call_args[0][0]
