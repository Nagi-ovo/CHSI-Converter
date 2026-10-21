FROM python:3.12.13-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade ca-certificates liblzma5 \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419~deb12u2' \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' liblzma5)" ge '5.4.1-1+deb12u2' \
    && rm -rf /var/lib/apt/lists/*
ARG PYPI_INDEX_URL=https://pypi.org/simple
COPY requirements.txt ./
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: \
    --index-url "$PYPI_INDEX_URL" -r requirements.txt
COPY app.py worker.py converter.py translations.py pdf_layout.py ./
COPY templates ./templates
COPY static ./static
COPY data ./data
USER 10001:10001
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=3).read()"]
ENTRYPOINT ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "--worker-tmp-dir", "/tmp", "app:app"]
