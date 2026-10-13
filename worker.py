"""Short-lived conversion process. Only safe error codes cross the boundary."""

import json
import sys
from pathlib import Path

from converter import CHSIConverter, ConversionError


def main():
    source, output = map(Path, sys.argv[1:3])
    try:
        overrides_path = source.parent / "translations.json"
        overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
        CHSIConverter.convert_to_pdf(source, output, overrides)
    except ConversionError as error:
        (source.parent / "error.json").write_text(json.dumps({"code": error.code}))
        return 1
    except Exception:
        (source.parent / "error.json").write_text(json.dumps({"code": "failed"}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
