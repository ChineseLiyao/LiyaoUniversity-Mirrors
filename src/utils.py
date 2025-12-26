import requests
from flask import Response, stream_with_context

def stream_proxy(url, headers=None):
    req = requests.get(url, stream=True, headers=headers, allow_redirects=True)
    
    def generate():
        for chunk in req.iter_content(chunk_size=128 * 1024): # 128KB 缓冲区
            yield chunk

    response = Response(stream_with_context(generate()), status=req.status_code)
    
    # 转发必要的响应头
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    for k, v in req.headers.items():
        if k.lower() not in excluded_headers:
            response.headers[k] = v
            
    response.headers['X-Mirrored-From'] = url
    return response