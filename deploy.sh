#!/bin/bash

REPO_URL="https://github.com/Nagi-ovo/CHSI-Converter.git"
REPO_NAME="CHSI-Converter"
IMAGE_NAME="chsi-converter"
CONTAINER_NAME="chsi-converter-app"

if [ -d "$REPO_NAME" ]; then
    echo "检测到已存在的仓库，正在更新..."
    cd $REPO_NAME
    git pull
    if [ $? -ne 0 ]; then
        echo "更新仓库失败，请检查您的网络连接或仓库权限。"
        exit 1
    fi
else
    echo "正在克隆仓库..."
    git clone $REPO_URL
    if [ $? -ne 0 ]; then
        echo "克隆仓库失败，请检查您的网络连接或仓库权限。"
        exit 1
    fi
    cd $REPO_NAME
fi

echo "正在构建 Docker 镜像..."
docker build -t $IMAGE_NAME .
if [ $? -ne 0 ]; then
    echo "构建 Docker 镜像失败，请检查 Dockerfile 或构建日志。"
    exit 1
fi

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "停止并删除已存在的容器..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

echo "启动新的容器..."
docker run -d -p 80:5000 --name $CONTAINER_NAME $IMAGE_NAME

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "部署成功！应用正在运行。"
    echo "您可以通过 http://localhost:5000 访问应用。"
else
    echo "部署失败，请检查日志。"
    exit 1
fi