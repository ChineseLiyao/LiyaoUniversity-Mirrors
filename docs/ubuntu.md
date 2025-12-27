# Ubuntu 镜像使用帮助

**LiyaoUniversity Mirrors** 提供 Ubuntu 官方仓库的代理。

## 自动调度机制
本站采用 **多源自动轮询 (Polling)** 技术。系统会实时在上游（TUNA, USTC, Aliyun）之间进行负载均衡。如果某个节点失效，系统将自动透明切换至健康节点。

## 修改 sources.list

备份现有的配置文件：
```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
```

编辑 `/etc/apt/sources.list`，将 `archive.ubuntu.com` 和 `security.ubuntu.com` 替换为本站地址：

```text
deb https://mirrors.liyao.edu.kg/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.liyao.edu.kg/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.liyao.edu.kg/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.liyao.edu.kg/ubuntu/ jammy-security main restricted universe multiverse
```

## 适用版本
支持所有 Ubuntu 发行版（包括 20.04, 22.04, 24.04 等）。