"""Pytest configuration and fixtures."""

import sys
from unittest.mock import MagicMock

# Mock tkinter to avoid GUI dependency in tests
# This allows main.py to be imported without requiring tkinter installation
sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.filedialog"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()

from tests.fixtures import *

# Import the test data from the fixtures.py file
