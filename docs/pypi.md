# PyPI 镜像使用帮助

**LiyaoUniversity Mirrors** 提供 PyPI 的代理服务。你可以通过以下方式使用该镜像。

## 临时使用

在执行 `pip install` 时，使用 `-i` 参数指定镜像源地址：

```bash
pip install requests -i https://mirrors.liyao.edu.kg/pypi/simple/ --trusted-host mirrors.liyao.edu.kg
```

## 永久配置

修改全局配置，将镜像源设置为本站：

```bash
pip config set global.index-url https://mirrors.liyao.edu.kg/pypi/simple/
```

## 代理机制说明

本站采用流式代理技术。当你请求一个包时，服务器会实时从上游源（pypi.org）抓取并重写 HTML 索引。所有的 `.whl` 和 `.tar.gz` 文件均通过本站中转，实现加速效果。