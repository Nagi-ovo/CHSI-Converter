"""HTTP boundary; reports never share a path or enter application logs."""

import json
import logging
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

BASE_DIR = Path(__file__).resolve().parent
ERRORS = {
    "invalid_file": "请选择原始 PDF 学信档案，文件大小不超过 5 MB。",
    "invalid_pdf": "无法读取这份 PDF。请重新下载原始学信档案后上传。",
    "encrypted_pdf": "请上传未加密的 PDF 学信档案。",
    "unsupported_report": "这份报告缺少必要信息或版式不受支持。请上传原始学信档案。",
    "too_complex": "这份 PDF 超出处理范围。请上传单页原始学籍在线验证报告。",
    "timeout": "转换超时。请检查报告是否为原始文件，稍后重试。",
    "busy": "当前正在处理另一份报告，请稍后重试。",
    "failed": "暂时无法完成转换，请稍后重试。",
    "missing_translation": "部分字段暂无可靠英文译名。请补充学校、专业或院系英文名后重试。",
    "invalid_translation": (
        "补充译名请使用常用拉丁字母、数字和标点，不超过 200 个字符。姓名拼音请不加声调。"
    ),
    "translation_too_long": "译文超出原报告的文字区域。请使用较短的正式英文名称后重试。",
}


class JobError(Exception):
    def __init__(self, code: str, status: int):
        self.code, self.status = code, status


def run_conversion(source: Path, output: Path, timeout: float) -> None:
    process = subprocess.Popen(
        [sys.executable, str(BASE_DIR / "worker.py"), str(source), str(output)],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise JobError("timeout", 504) from None
    if process.returncode:
        code = "failed"
        error_file = source.parent / "error.json"
        if error_file.is_file() and error_file.stat().st_size < 1024:
            try:
                code = json.loads(error_file.read_text()).get("code", "failed")
            except (ValueError, OSError):
                pass
        if code not in ERRORS:
            code = "failed"
        raise JobError(code, 422 if code != "failed" else 500)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        MAX_FORM_MEMORY_SIZE=256 * 1024,
        MAX_FORM_PARTS=5,
        CONVERSION_TIMEOUT=45,
        TEMP_ROOT=os.environ.get("CHSI_TEMP_ROOT"),
        CONVERTER=run_conversion,
    )
    if test_config:
        app.config.update(test_config)
    slot = threading.BoundedSemaphore(1)
    app.logger.setLevel(logging.INFO)

    def failure(code, status):
        response = app.make_response((render_template("index.html", error=ERRORS[code]), status))
        if status == 503:
            response.headers["Retry-After"] = "10"
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_error):
        return failure("invalid_file", 413)

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; form-action 'self'; "
            "frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/healthz")
    def health():
        return {"status": "ok"}

    @app.post("/convert")
    def convert():
        request_id = uuid.uuid4().hex
        started = time.monotonic()
        if not slot.acquire(blocking=False):
            return failure("busy", 503)
        outcome = "failed"
        try:
            files = request.files.getlist("file")
            if len(files) != 1 or len(request.files) != 1:
                raise JobError("invalid_file", 400)
            upload = files[0]
            if not upload.filename or Path(upload.filename).suffix.lower() != ".pdf":
                raise JobError("invalid_file", 400)
            with tempfile.TemporaryDirectory(prefix="chsi-", dir=app.config["TEMP_ROOT"]) as folder:
                source, output = Path(folder) / "input.pdf", Path(folder) / "output.pdf"
                upload.save(source)
                with source.open("rb") as stream:
                    if stream.read(5) != b"%PDF-":
                        raise JobError("invalid_pdf", 422)
                overrides = {
                    key: request.form[field].strip()
                    for field, key in {
                        "institution": "Institution",
                        "major": "Major",
                        "department": "Faculties",
                        "english_name": "Name",
                    }.items()
                    if request.form.get(field, "").strip()
                }
                (Path(folder) / "translations.json").write_text(json.dumps(overrides))
                app.config["CONVERTER"](source, output, app.config["CONVERSION_TIMEOUT"])
                if not output.is_file() or not 0 < output.stat().st_size <= 8 * 1024 * 1024:
                    raise JobError("failed", 500)
                document = output.read_bytes()
            outcome = "success"
            response = send_file(
                BytesIO(document),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"report-{request_id}.pdf",
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except JobError as error:
            outcome = error.code
            return failure(error.code, error.status)
        except RequestEntityTooLarge:
            outcome = "too_large"
            raise
        except Exception:
            return failure("failed", 500)
        finally:
            slot.release()
            app.logger.info(
                "conversion id=%s outcome=%s duration_ms=%d",
                request_id,
                outcome,
                round((time.monotonic() - started) * 1000),
            )

    return app


app = create_app()
application = app
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("FLASK_PORT", "5001")), debug=False)
