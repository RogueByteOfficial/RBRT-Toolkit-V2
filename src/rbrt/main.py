"""Main executable entrypoint for RogueByte RBRT Toolkit V2."""

import sys
from rbrt.cli import handle_cli

def main() -> int:
    """Invoked when running 'rbrt' from shell or python -m rbrt."""
    return handle_cli(sys.argv[1:])

if __name__ == "__main__":
    sys.exit(main())
