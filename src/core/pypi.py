from flask import Blueprint, request, render_template
from ..utils import stream_proxy, stream_and_replace, render_markdown, stream_proxy, stream_and_replace
from ..logger import logger

pypi_bp = Blueprint('pypi', __name__, url_prefix='/pypi')

# 上游配置
PYPI_INDEX_URL = "https://pypi.org/simple/"
PYPI_FILE_URL = "https://files.pythonhosted.org/packages/"

@pypi_bp.route('/help')
def help():
    # 调用解析工具读取 docs/pypi.md
    md_content = render_markdown('pypi')
    return render_template('help_page.html', title="PyPI", content=md_content)

@pypi_bp.route('/simple/')
@pypi_bp.route('/simple/<path:path>')
def index(path=""):
    target_url = f"{PYPI_INDEX_URL}{path}"
    logger.info("PYPI", f"Streaming index: {path}")

    # 定义匹配规则：匹配官方文件域名
    pattern = r"https://files\.pythonhosted\.org/packages/"
    # 定义替换规则：指向本地的 files 路由
    replacement = f"{request.host_url}pypi/files/"

    # 使用流式替换处理器
    return stream_and_replace(target_url, pattern, replacement)

@pypi_bp.route('/files/<path:path>')
def files(path):
    # 对于二进制文件（.whl, .tar.gz），直接使用原始流式代理
    target_url = f"{PYPI_FILE_URL}{path}"
    logger.info("PYPI", f"Proxying file: {path}")
    return stream_proxy(target_url)