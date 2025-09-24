FROM python:3.9.12

WORKDIR /app

LABEL Author=Nagi-ovo

COPY . .

COPY ./sources.list /etc/apt/sources.list

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r pyproject.toml && \
    apt-get update && \
    apt-get install -y poppler-utils vim

ENV FLASK_DEBUG=false
ENV FLASK_PORT=5000

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app:app"]
