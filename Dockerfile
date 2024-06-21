FROM python:3.9.12

WORKDIR /app

LABEL Author=Nagi-ovo

COPY . .

COPY ./sources.list /etc/apt/sources.list

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt && \
    apt-get update && \
    apt-get install -y poppler-utils vim
    
ENTRYPOINT ["python","app.py"]