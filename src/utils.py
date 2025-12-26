import re
import requests
from flask import Response, stream_with_context
from .logger import logger

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
        
        return response

    except Exception as e:
        logger.error("UTILS", f"Streaming replacement failed: {str(e)}")
        return "Internal Server Error", 500