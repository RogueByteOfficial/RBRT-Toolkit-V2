# Developer Guide & Release Procedures — RogueByte RBRT Toolkit V2

## Packaging and Release

To build source distribution and wheel packages for PyPI or GitHub Releases:

```bash
# 1. Install build tools
pip install --upgrade build twine

# 2. Build distribution archives
python -m build

# 3. Check artifacts in dist/
ls -lh dist/
# Output:
# rbrt-2.0.0-py3-none-any.whl
# rbrt-2.0.0.tar.gz

# 4. Verify package metadata
twine check dist/*
```

---

## Coding Standards

- Line length: 100 characters.
- Python version compatibility: Python 3.10, 3.11, 3.12+.
- Strict typing with dataclasses where applicable.
- No mutable default arguments.
- Safe path handling using `pathlib.Path.resolve()`.
- Explicit subprocess error handling.

---

## Developer Contact
- **Organization**: RogueByte
- **GitHub**: [github.com/RogueByteOfficial/RBRT-Toolkit-V2](https://github.com/RogueByteOfficial/RBRT-Toolkit-V2)
- **Ko-fi**: [https://ko-fi.com/roguebyte](https://ko-fi.com/roguebyte)
- **Website**: [https://roguebyte.online](https://roguebyte.online)
- **Contact**: `contact@roguebyte.online`
