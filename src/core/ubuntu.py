from flask import Blueprint, request, current_app
from ..utils import stream_proxy
from ..logger import logger
import itertools

ubuntu_bp = Blueprint('ubuntu', __name__, url_prefix='/ubuntu')

# 1. 定义上游集群 (Upstream Cluster)
UBUNTU_UPSTREAMS = [
    "https://mirrors.tuna.tsinghua.edu.cn/ubuntu/",
    "https://mirrors.ustc.edu.cn/ubuntu/",
    "https://mirrors.aliyun.com/ubuntu/",
    "http://archive.ubuntu.com/ubuntu/" # 官方兜底源
]

# 2. 创建无限循环迭代器实现轮询
upstream_cycle = itertools.cycle(UBUNTU_UPSTREAMS)

@ubuntu_bp.route('/')
@ubuntu_bp.route('/<path:path>')
def proxy(path=""):
    # 获取当前轮询的上游
    
    attempts = 0
    max_attempts = len(UBUNTU_UPSTREAMS)
    
    while attempts < max_attempts:
        base_url = next(upstream_cycle)
        target_url = f"{base_url}{path}"
        
        logger.info("UBUNTU", f"Polling attempt {attempts + 1}: {target_url}")
        
        try:
            # 执行流式代理
            # 我们需要检查上游的状态码，如果 404 或 5xx 则尝试下一个源
            # 这里对 stream_proxy 进行微调，传入检测逻辑
            return perform_ubuntu_proxy(target_url)
        except Exception as e:
            logger.error("UBUNTU", f"Source {base_url} failed: {str(e)}")
            attempts += 1
            continue

    return "All upstreams failed", 502

def perform_ubuntu_proxy(url):
    """
    具体的执行逻辑，如果上游返回错误则抛出异常触发轮询
    """
    # 转发请求头（支持断点续传）
    headers = {k: v for k, v in request.headers if k.lower() in ['range', 'user-agent']}
    
    return stream_proxy(url, headers=headers)