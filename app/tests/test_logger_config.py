"""Unit tests for core/logger_config.py.

Covers:
- Default level calls (INFO).
- Alternative level calls (DEBUG, WARNING, ERROR).
- Idempotency (multiple calls should not raise exceptions).
- Log directory and file creation.
"""

from pathlib import Path
from core.logger_config import setup_logger


class TestSetupLogger:
    """Tests the behavior of the setup_logger function."""

    def test_default_level_does_not_raise(self):
        """Calling without arguments (INFO) should not raise any exceptions."""
        setup_logger()

    def test_debug_level_does_not_raise(self):
        """The DEBUG level should be accepted without error."""
        setup_logger("DEBUG")

    def test_warning_level_does_not_raise(self):
        """The WARNING level should be accepted without error."""
        setup_logger("WARNING")

    def test_error_level_does_not_raise(self):
        """The ERROR level should be accepted without error."""
        setup_logger("ERROR")

    def test_idempotent_multiple_calls(self):
        """Calling setup_logger multiple times should not cause errors."""
        setup_logger()
        setup_logger("DEBUG")
        setup_logger()

    def test_log_directory_exists_after_setup(self):
        """The logs/ directory should exist after logger configuration."""
        setup_logger()
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        assert log_dir.exists(), f"Log directory not found: {log_dir}"

    def test_log_file_is_created(self):
        """The monitor_log.txt file should exist after configuration."""
        setup_logger()
        log_file = Path(__file__).resolve().parent.parent.parent / "logs" / "monitor_log.txt"
        assert log_file.exists(), f"Log file not found: {log_file}"