import subprocess
from unittest.mock import Mock

import pytest

import app


def test_timeout_reaps_the_conversion_process_group(monkeypatch, tmp_path):
    process = Mock(pid=999999)
    process.wait.side_effect = [subprocess.TimeoutExpired("worker", 45), -9]
    popen = Mock(return_value=process)
    kill_group = Mock()
    monkeypatch.setattr(app.subprocess, "Popen", popen)
    monkeypatch.setattr(app.os, "killpg", kill_group)
    with pytest.raises(app.JobError) as error:
        app.run_conversion(tmp_path / "input.pdf", tmp_path / "output.pdf", 45)
    assert error.value.code == "timeout"
    assert popen.call_args.kwargs["start_new_session"] is True
    kill_group.assert_called_once_with(process.pid, app.signal.SIGKILL)
    assert process.wait.call_count == 2
