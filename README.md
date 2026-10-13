# CHSI-Converter

把原始学信档案 PDF 中的中文替换为英文，输出英文 PDF。保留原页尺寸、背景、边框、照片、二维码与各行的位置，不重新设计报告版式。英文较长时仅在原文字区域内缩小字号，无法放下时提示修改译名。

当前支持单页 A4《教育部学籍在线验证报告》的原始文字型 PDF。扫描件、不同报告类型或无法可靠识别的版式明确返回错误。生成的是辅助翻译，正式验证以原报告及学信网为准。

## 运行

Python 3.12：

```bash
uv sync --locked
uv run app.py
```

打开 http://127.0.0.1:5001 。无需安装 LibreOffice、Poppler 或其他桌面软件，转换直接在 PDF 中完成。

校名使用 `data/` 中的 582 所高校精确对照，来源为 2021 年社区数据，含 MIT 许可证。未知或更名校名、专业与院系不自动猜译，可在上传时补充正式英文名，也可指定姓名拼写。数据不发送外部翻译服务。

每次只转换一份文件，最大 5 MB，超时 45 秒。每次使用独立临时目录并自动清理，日志只记录结果和耗时。

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
