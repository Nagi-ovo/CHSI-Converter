"""Short-lived conversion process. Only safe error codes cross the boundary."""

import json
import sys
from pathlib import Path

from converter import CHSIConverter, ConversionError


def write_error(folder, code, diagnostic, details=None):
    payload = {"code": code, "diagnostic": diagnostic}
    if details:
        payload["details"] = details
    (folder / "error.json").write_text(json.dumps(payload), encoding="utf-8")


def main():
    source, output = map(Path, sys.argv[1:3])
    try:
        overrides_path = source.parent / "translations.json"
        overrides = (
            json.loads(overrides_path.read_text(encoding="utf-8"))
            if overrides_path.exists()
            else {}
        )
        CHSIConverter.convert_to_pdf(source, output, overrides)
    except ConversionError as error:
        write_error(
            source.parent,
            error.code,
            error.diagnostic,
            error.details,
        )
        return 1
    except Exception as error:
        write_error(
            source.parent,
            "failed",
            f"unexpected worker error: {type(error).__name__}",
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
