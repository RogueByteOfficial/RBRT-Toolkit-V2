# Contributing to RogueByte RBRT Toolkit V2

We welcome contributions from firmware developers, repair technicians, and forensics engineers.

## Development Workflow

1. Fork the repository on GitHub: `https://github.com/RogueByteOfficial/RBRT-Toolkit-V2`
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RBRT-Toolkit-V2.git
   cd RBRT-Toolkit-V2
   ```
3. Set up a clean Python 3.10+ virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```
4. Run tests before writing changes:
   ```bash
   python tests/run_tests.py
   ```
5. Follow code quality standards:
   - Zero unnecessary external dependencies for core functionality.
   - All file processing must use chunked streams to avoid unbounded RAM usage.
   - Never claim to decrypt or extract proprietary content without independent verifiable implementation.
   - Non-destructive operation: source input files must never be modified or overwritten.
6. Submit a clean Pull Request with relevant test coverage.

## Contact
- Organization: RogueByte
- Website: https://roguebyte.online
- Email: contact@roguebyte.online
