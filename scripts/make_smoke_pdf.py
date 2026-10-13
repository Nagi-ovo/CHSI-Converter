"""Generate a non-personal report fixture for staging acceptance."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from conftest import synthetic_report

Path(sys.argv[1]).write_bytes(synthetic_report())
