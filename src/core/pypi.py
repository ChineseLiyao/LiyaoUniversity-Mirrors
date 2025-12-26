from flask import Blueprint, request, render_template, current_app
from ..utils import stream_proxy
import requests
import re

pypi_bp = Blueprint('pypi', __name__, url_prefix='/pypi')

# 官方源
PYPI_INDEX_URL = "https://pypi.org/simple/"
PYPI_FILE_URL = "https://files.pythonhosted.org/packages/"

@pypi_bp.route('/simple/')
@pypi_bp.route('/simple/<path:path>')
def index(path=""):
    target_url = f"{PYPI_INDEX_URL}{path}"
    # 抓取官方 Index 页面
    resp = requests.get(target_url)
    
    if resp.status_code != 200:
        return resp.text, resp.status_code

    # 核心逻辑：使用正则重写链接
    # 将 https://files.pythonhosted.org/packages/ 替换为我们的本地文件代理路径
    content = resp.text
    local_files_prefix = f"{request.host_url}pypi/files/"
    content = content.replace("https://files.pythonhosted.org/packages/", local_files_prefix)
    
    # 将页面内的相对路径链接也修正为绝对路径（可选）
    return content

@pypi_bp.route('/files/<path:path>')
def files(path):
    # 代理真实的 .whl 或 .tar.gz 文件
    target_url = f"{PYPI_FILE_URL}{path}"
    return stream_proxy(target_url)