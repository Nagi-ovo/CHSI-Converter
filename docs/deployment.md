# 部署与检查

## 部署

`compose.yaml` 使用普通用户、只读文件系统、768 MB 内存与 128 个进程上限，本机端口 8002。建议在专用用户的 rootless Docker 中运行，通过 Nginx 提供 HTTPS。`deploy.sh` 仅暂存新版本，不直接切换生产入口；验证后再切换 Nginx。

容器直接安装 `requirements.txt` 中锁定版本并校验哈希，不包含 uv、LibreOffice 或 Poppler。修改依赖后执行 `uv export --frozen --no-dev --no-emit-project --no-header --no-annotate --format requirements.txt -o requirements.txt`。国内构建可通过 `--build-arg PYPI_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple` 选择镜像，仍校验同一套哈希。

```bash
CHSI_RELEASE=20261013 CHSI_PORT=8002 ./deploy.sh
```

CPU 通过专用用户的 systemd slice 限制为 `CPUQuota=100%`（一个逻辑 CPU），建议同时设置 `MemoryMax=900M`、`TasksMax=256`。容器单独限制 768 MB 内存和 128 个进程。实际部署后检查这些限制是否生效。公网代理建议上传上限 `6m`、读取超时 `60s`；按 IP 限制转换请求速率。

## 检查

```bash
uv run ruff check .
uv run pytest -q
```

保留少量转换、临时文件清理、未知译名及超时检查。测试文件均为生成的样本，不提交真实报告。
