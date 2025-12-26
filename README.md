# LiyaoUniversity Mirrors

一个基于 Flask 构建的高性能、流式开源镜像代理服务。与传统的通过 `rsync` 全量同步数百 GB 数据的镜像站不同，本项目采用 **代理分发 (Pull-through Cache/Proxy)** 模式，实现按需拉取、零存储占用。

## 特性

- **零存储成本**：无需购买昂贵的大容量硬盘，通过上游源实时转发数据。
- **流式传输 (Streaming)**：采用 `chunked` 传输编码，支持超大 ISO 文件分发，内存占用极低。
- **链接重写**：针对 PyPI 等 Index 协议，自动重写 HTML 内的绝对路径，确保客户端下载链路完整闭环。
- **模块化架构**：基于 Flask Blueprint 设计，可轻松扩展 Ubuntu, NPM, PyPI, Docker 等多种镜像环境。
- **工业级日志**：标准格式化日志输出，方便部署于容器环境或进行系统级监控。

## 技术栈

- **Language:** Python 3.10+
- **Framework:** Flask 3.0.x
- **HTTP Client:** Requests (with Stream support)
- **UI:** Tailwind CSS & Jinja2
- **Server:** Gunicorn (Recommended for Production)

## 目录结构

```text
liyao-mirrors/
├── src/
│   ├── app.py             # 核心入口
│   ├── logger.py          # 标准化日志模块
│   ├── utils.py           # 通用流式处理工具
│   └── core/
│       ├── pypi.py        # PyPI 镜像蓝图
│       └── ubuntu.py      # Ubuntu 镜像蓝图 (Development)
├── templates/
│   ├── base.html          # 响应式基础模板
│   └── index.html         # 镜像站首页
├── .gitignore             # 排除环境与缓存
├── requirements.txt       # 项目依赖
└── README.md              # 项目文档
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.10 或更高版本。建议使用虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行服务

**开发模式：**

```bash
python -m src.app
```

**生产模式 (Gunicorn)：**

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 src.app:app
```

## 镜像使用示例

### Python (PyPI)

在安装包时临时指定源：

```bash
pip install requests -i http://localhost:5000/pypi/simple/ --trusted-host localhost
```

全局配置：

```bash
pip config set global.index-url http://localhost:5000/pypi/simple/
```

## 开发规范

### 添加新镜像

1. 在 `src/core/` 目录下创建新的镜像模块（如 `npm.py`）。
2. 使用 `Blueprint` 定义路由，并实现特定的重写逻辑（若需要）。
3. 在 `src/app.py` 中注册新蓝图：
   ```python
   from .core.npm import npm_bp
   app.register_blueprint(npm_bp)
   ```

### 链接重写原则

对于提供 HTML 索引的镜像（如 PyPI），必须捕获响应内容并将其中的上游文件链接（如 `files.pythonhosted.org`）重写为本地代理路径，否则客户端将直接绕过代理服务器。

## 许可证

基于 MIT License 开源。

---

**LiyaoUniversity Mirrors** &copy; 2025
Designed for efficiency and logic.