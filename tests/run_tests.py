"""Automated test runner for RogueByte RBRT Toolkit V2."""

import sys
import unittest
from pathlib import Path

# Add root_dir and src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def run_tests() -> bool:
    """Discovers and runs all tests in the tests/ directory."""
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(root_dir / "tests"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
