"""命令行入口：把原来 dl.py / bd.py / bdp.py 三种用法合并成一个 CLI。"""

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from . import fetch
from .author import processAuthorUrl
from .pack import cleanStaleTempFiles, processUrl
from .progress import PlainReporter, Progress

DEFAULT_JOBS = 4
MAX_JOBS = 16


def readUrlFile(path):
    """从文本文件读取链接，每行一个，忽略空行与 # 开头的注释。"""
    # utf-8-sig 兼容带 BOM 的文件，避免第一行链接匹配不上
    with open(path, "r", encoding="utf-8-sig") as f:
        return [line.strip() for line in f
                if line.strip() and not line.strip().startswith("#")]


def expandUrls(urls, reporter):
    """把作者页展开成一个个贴图包链接，其他链接原样保留。

    展开要先于下载完成，这样才知道总数，进度条才有分母。
    """
    expanded = []
    for url in urls:
        if '/author/' not in url:
            expanded.append(url)
            continue
        authorUrl = url.split('?page=')[0]
        try:
            stickerUrls = processAuthorUrl(authorUrl)
        except requests.exceptions.RequestException as e:
            fetch.noteError(e)
            reporter.log(f"读取作者页 {authorUrl} 失败: {fetch.shortError(e)}")
            continue
        if not stickerUrls:
            reporter.log(f"在 {authorUrl} 中没有找到表情包链接。")
            continue
        reporter.log(f"作者页 {authorUrl} 找到 {len(stickerUrls)} 个表情包")
        expanded.extend(stickerUrls)
    return expanded


def runOne(url, outputDir, reporter, overwrite):
    """下载一个包，返回状态字符串；异常也收敛成 fail，避免拖垮整批。"""
    try:
        return processUrl(url, outputDir, reporter, overwrite)
    except requests.exceptions.RequestException as e:
        fetch.noteError(e)
        reporter.log(f"处理 {url} 失败: {fetch.shortError(e)}")
        return "fail"
    except OSError as e:
        reporter.log(f"处理 {url} 失败: {e}")
        return "fail"


def runAll(urls, outputDir, jobs, overwrite):
    """按并发数下载全部链接，返回 (成功, 跳过, 失败)。"""
    reporter = Progress(len(urls)) if len(urls) > 1 else PlainReporter()
    counts = {"ok": 0, "skip": 0, "fail": 0}

    try:
        if jobs > 1 and len(urls) > 1:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                futures = [pool.submit(runOne, url, outputDir, reporter, overwrite)
                           for url in urls]
                for future in as_completed(futures):
                    status = future.result()
                    counts[status] += 1
                    reporter.advance(status)
        else:
            for url in urls:
                status = runOne(url, outputDir, reporter, overwrite)
                counts[status] += 1
                reporter.advance(status)
    finally:
        reporter.close()

    return counts["ok"], counts["skip"], counts["fail"]


def buildParser():
    parser = argparse.ArgumentParser(
        prog="line-dl",
        description="LINE 贴图包和 emoji 下载器",
        epilog="示例: python main.py https://store.line.me/stickershop/product/1419581/zh-Hant",
    )
    parser.add_argument("urls", nargs="*", help="贴图包 / emoji / 作者页链接，可以给多个")
    parser.add_argument("-f", "--file", help="从文本文件批量读取链接，每行一个")
    parser.add_argument("-o", "--output", default="output",
                        help="输出目录，默认 output；用 -o . 下载到当前目录")
    parser.add_argument("-j", "--jobs", type=int, default=DEFAULT_JOBS,
                        help=f"并发下载数，默认 {DEFAULT_JOBS}；用 -j 1 改回逐个下载")
    parser.add_argument("--overwrite", action="store_true",
                        help="重新下载已存在的包，默认跳过")
    parser.add_argument("--proxy",
                        help="代理地址，例如 http://127.0.0.1:7897。"
                             "不指定时会读取 HTTP_PROXY / HTTPS_PROXY 环境变量")
    return parser


def main(argv=None):
    parser = buildParser()
    args = parser.parse_args(argv)

    if args.jobs < 1:
        parser.error("--jobs 至少为 1")
    # 并发太高对 LINE 不友好，也容易被限流
    jobs = min(args.jobs, MAX_JOBS)

    urls = list(args.urls)
    if args.proxy:
        fetch.setProxy(args.proxy)
        print(f"使用代理: {args.proxy}")
    if args.file:
        try:
            urls.extend(readUrlFile(args.file))
        except OSError as e:
            parser.error(f"无法读取链接文件 {args.file}: {e}")

    if not urls:
        # 非交互环境（管道、CI）下 input() 会抛 EOFError，别让程序崩栈
        try:
            entered = input("请输入贴图包 / emoji / 作者页网址: ").strip()
        except EOFError:
            entered = ""
        if entered:
            urls.append(entered)
    if not urls:
        parser.error("没有可下载的链接")

    outputDir = os.path.abspath(args.output)
    try:
        os.makedirs(outputDir, exist_ok=True)
    except OSError as e:
        parser.error(f"无法创建输出目录 {outputDir}: {e}")
    print(f"输出目录: {outputDir}")

    stale = cleanStaleTempFiles(outputDir)
    if stale:
        print(f"已清理上次中断残留的临时文件 {stale} 个")

    urls = expandUrls(urls, PlainReporter())
    if not urls:
        print("没有可下载的表情包")
        return 1

    if jobs > 1 and len(urls) > 1:
        print(f"共 {len(urls)} 个表情包，并发 {jobs} 个下载")

    succeeded, skipped, failed = runAll(urls, outputDir, jobs, args.overwrite)

    summary = f"完成: 成功 {succeeded}"
    if skipped:
        summary += f"，跳过 {skipped}"
    if failed:
        summary += f"，失败 {failed}"
    print(summary)

    # 连不上服务器多半是网络环境问题，结束时统一提示一次怎么配代理
    if fetch.hasConnectionFailures():
        print(fetch.NETWORK_HINT)

    return 1 if failed else 0
