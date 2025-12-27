import re
import requests
from flask import Response, stream_with_context, abort
from .logger import logger
import markdown
import os

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

def render_markdown(filename):
    """
    读取并解析 Markdown 文件为 HTML
    """
    # 获取项目根目录下的 docs 文件夹路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'docs', f"{filename}.md")
    
    if not os.path.exists(file_path):
        abort(404)
        
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        # 启用 codehilite (代码高亮) 和 tables 扩展
        return markdown.markdown(text, extensions=['fenced_code', 'tables'])

def stream_proxy(url, headers=None):
    # 合并传入的 headers (如 Range) 与默认的浏览器伪装头
    req_headers = DEFAULT_HEADERS.copy()
    if headers:
        req_headers.update(headers)

    # 发起请求
    req = requests.get(url, stream=True, allow_redirects=True, headers=req_headers, timeout=10)
    
    # 如果上游返回 403/404/5xx，直接抛出异常，让 Ubuntu 的轮询逻辑能够捕获并切换上游
    if req.status_code >= 400:
        logger.error("UTILS", f"Upstream returned {req.status_code} for {url}")
        req.raise_for_status()

    @stream_with_context
    def generate():
        for chunk in req.iter_content(chunk_size=256 * 1024):
            yield chunk

    response = Response(generate(), status=req.status_code)
    
    # 转发关键响应头
    for key in ['Content-Type', 'Content-Length', 'Accept-Ranges', 'Content-Range']:
        if key in req.headers:
            response.headers[key] = req.headers[key]
    
    response.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=60'
    return response

def stream_and_replace(url, pattern, replacement, headers=None):
    """
    流式获取内容并实时进行正则替换
    """
    try:
        # 开启 stream=True
        req = requests.get(url, stream=True, headers=headers, timeout=20)
        
        # 预编译正则以提高效率
        regex = re.compile(pattern)

        @stream_with_context
        def generate():
            # 使用 iter_lines 处理文本流，这对于 HTML 索引页非常有效
            # 因为链接通常不会跨行存在
            for line in req.iter_lines(decode_unicode=True):
                if line:
                    # 执行正则替换
                    modified_line = regex.sub(replacement, line)
                    # 必须手动加上换行符，因为 iter_lines 会去掉它
                    yield (modified_line + "\n").encode('utf-8')

        response = Response(generate(), status=req.status_code)
        
        # 复制必要的响应头
        for key in ['Content-Type', 'Cache-Control']:
            if key in req.headers:
                response.headers[key] = req.headers[key]
        
        response.headers.pop('Content-Length', None)

        response.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=60'
        return response

    except Exception as e:
        logger.error("UTILS", f"Streaming replacement failed: {str(e)}")
        return "Internal Server Error", 500