from flask import Flask, render_template, g
from .core.pypi import pypi_bp
from .logger import logger
from .core.ubuntu import ubuntu_bp
from datetime import datetime

app = Flask(__name__)
app.register_blueprint(pypi_bp)
app.register_blueprint(ubuntu_bp)

@app.before_request
def before_request():
    g.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

MIRRORS_CONFIG = [
    {
        "name": "PyPI", 
        "index_path": "/pypi/simple/", 
        "help_path": "/pypi/help", 
        "desc": "Python Package Index 智能流式代理", 
        "status": "Online"
    },
    {
        "name": "Ubuntu", 
        "index_path": "/ubuntu/", 
        "help_path": "/ubuntu/help", 
        "desc": "多源轮询高速镜像代理", 
        "status": "Online"
    }
]

@app.get('/')
def index():
    return render_template('index.html', mirrors=MIRRORS_CONFIG)

# 在 pypi.py 中增加一个帮助页面路由
@pypi_bp.route('/help')
def help():
    return render_template('pypi_help.html')

if __name__ == '__main__':
    logger.success("SYSTEM", "LiyaoUniversity Mirror Cluster Started")
    app.run(host='0.0.0.0', port=5000, debug=True)