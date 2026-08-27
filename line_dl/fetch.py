"""统一的 HTTP 会话：带 User-Agent、超时、自动重试与代理支持。
之前三个脚本里的 requests.get 都没有 timeout，网络卡住时会永久挂起；
也没有 User-Agent，容易被 LINE 挡下。所有网络请求现在都走这里。
"""

import requests
from requests.adapters import HTTPAdapter

try:
    from urllib3.util.retry import Retry
except ImportError:  # 极旧的 requests 会把 urllib3 打包在自己的命名空间下
    from requests.packages.urllib3.util.retry import Retry

TIMEOUT = (10, 60)  # (连接超时, 读取超时)：连不上时 10 秒放弃，不用干等 30 秒

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

NETWORK_HINT = """
============================================================
连接 LINE 服务器失败。LINE 商店在部分地区无法直接访问，请任选一种方式：

  1. 命令行指定代理：
       python main.py <url> --proxy http://127.0.0.1:7897

  2. 设置环境变量后再运行：
       PowerShell:   $env:HTTPS_PROXY='http://127.0.0.1:7897'
       bash/termux:  export HTTPS_PROXY=http://127.0.0.1:7897

端口请换成你自己代理软件的实际监听端口。

注意：代理软件的 PAC 模式和系统代理开关对 python 都无效，
必须用上面两种方式之一显式告诉脚本走代理。
============================================================"""

def buildSession():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = buildSession()

# 出现过的连接类错误次数，用于结束时给出一次统一的代理提示
connectionFailures = 0


def setProxy(proxyUrl):
    """显式指定代理。不调用时 requests 仍会读取 HTTP(S)_PROXY 环境变量。"""
    SESSION.proxies.update({"http": proxyUrl, "https": proxyUrl})


def noteError(error):
    """记录连接类错误，供 hasConnectionFailures() 判断是否要提示代理。"""
    global connectionFailures
    if isinstance(error, (requests.exceptions.ConnectionError,
                          requests.exceptions.Timeout)):
        connectionFailures += 1


def hasConnectionFailures():
    return connectionFailures > 0

def shortError(error):
    """把 requests 冗长的异常压成一行，避免刷屏。"""
    if isinstance(error, requests.exceptions.Timeout):
        return "连接超时"
    if isinstance(error, requests.exceptions.SSLError):
        return "SSL 证书校验失败"
    if isinstance(error, requests.exceptions.ConnectionError):
        return "无法连接到服务器"
    if isinstance(error, requests.exceptions.HTTPError):
        response = getattr(error, "response", None)
        return f"HTTP {response.status_code}" if response is not None else "HTTP 错误"
    return str(error)


def get(url, **kwargs):
    """带默认超时的 GET。"""
    kwargs.setdefault("timeout", TIMEOUT)
    return SESSION.get(url, **kwargs)
