from flask import Blueprint, request, current_app, render_template
from ..utils import stream_proxy, render_markdown
from ..logger import logger
import itertools

ubuntu_bp = Blueprint('ubuntu', __name__, url_prefix='/ubuntu')

# 1. 定义上游集群 (Upstream Cluster)
UBUNTU_UPSTREAMS = [
    "https://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "https://mirrors.ustc.edu.cn/ubuntu/",
    "https://mirrors.aliyun.com/ubuntu/",
    "http://archive.ubuntu.com/ubuntu/"
]

# 2. 创建无限循环迭代器实现轮询
upstream_cycle = itertools.cycle(UBUNTU_UPSTREAMS)

@ubuntu_bp.route('/help')
def help():
    md_content = render_markdown('ubuntu')
    return render_template('help_page.html', title="Ubuntu", content=md_content)

@ubuntu_bp.route('/')
@ubuntu_bp.route('/<path:path>')
def proxy(path=""):
    attempts = 0
    max_attempts = len(UBUNTU_UPSTREAMS)
    
    while attempts < max_attempts:
        base_url = next(upstream_cycle)
        target_url = f"{base_url}{path}"
        
        try:
            # 这里的 headers 应该来自原始请求，比如客户端执行 apt 时带的 Range
            client_headers = {k: v for k, v in request.headers if k.lower() in ['range']}
            return stream_proxy(target_url, headers=client_headers)
        except Exception as e:
            # 当返回 403 时，会触发这里的切换逻辑
            logger.warning("UBUNTU", f"Attempt {attempts + 1} failed: {target_url} (Error: {str(e)})")
            attempts += 1
            continue

    return "All upstreams denied access or are offline", 502

def perform_ubuntu_proxy(url):
    """
    具体的执行逻辑，如果上游返回错误则抛出异常触发轮询
    """
    # 转发请求头（支持断点续传）
    headers = {k: v for k, v in request.headers if k.lower() in ['range', 'user-agent']}
    
    return stream_proxy(url, headers=headers)