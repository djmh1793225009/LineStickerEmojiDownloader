"""贴图包 / emoji 包的名称获取、下载与 zip 清理。"""

import glob
import json
import os
import re
import tempfile
import threading
import time
import zipfile

import requests
from bs4 import BeautifulSoup

from . import fetch
from .naming import sanitize, stripSiteTitle
from .progress import PlainReporter

EMOJI_PATTERN = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{23,25})")
STICKER_PATTERN = re.compile(r"https://store\.line\.me/stickershop/product/(\d{6,9})")
PRODUCT_PATTERN = re.compile(r"(https?://store\.line\.me/(?:sticker|emoji)shop/product/[^/?#]+)")

# 只匹配缩略图，而不是任何文件名里含 "key" 的文件。
# 贴图包是 key.png / key@2x.png，emoji 包是 001_key.png 这样每张图一个。
KEY_PATTERN = re.compile(r"^(key|\d+_key)(@\d+x)?$", re.IGNORECASE)

def toEnglishUrl(url):
    """把任意语言的商店链接改写成英文页链接，顺带去掉 query。

    旧实现只把 '/zh-Hant' 替换成 '/en'，/ja、/ko 或不带语言后缀的链接都取不到名字。
    """
    match = PRODUCT_PATTERN.match(url)
    return f"{match.group(1)}/en" if match else url

def getPackName(url, fallback, reporter=None):
    """抓取包名并净化；抓不到时回落到包 ID，而不是所有包共用一个名字。"""
    reporter = reporter or PlainReporter()
    try:
        response = fetch.get(toEnglishUrl(url))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        fetch.noteError(e)
        reporter.log(f"获取表情包名字失败({fetch.shortError(e)})，改用 ID: {fallback}")
        return fallback

    soup = BeautifulSoup(response.text, "html.parser")
    titleTag = soup.find("p", class_="mdCMN38Item01Ttl")
    if titleTag:
        return sanitize(titleTag.get_text(), fallback)

    # 页面改版时的兜底：og:title 比 class 名稳定得多
    # emoji 页没有上面那个 class，只能从标题取，需要先去掉站点后缀
    ogTitle = soup.find("meta", property="og:title")
    if ogTitle and ogTitle.get("content"):
        return sanitize(stripSiteTitle(ogTitle["content"]), fallback)

    if soup.title:
        return sanitize(stripSiteTitle(soup.title.get_text()), fallback)

    reporter.log(f"未能从页面解析包名，改用 ID: {fallback}")
    return fallback

def replaceWithRetry(src, dst, attempts=20):
    """os.replace 的重试版。

    Windows 上刚落地的新文件常被杀毒软件独占打开扫描，此时 replace 会报
    PermissionError(WinError 5/32)。这类锁的窗口时长不可控（大文件尤其久），
    单次短重试很可能错过，所以放宽到 20 次并封顶单次等待 1 秒。
    """
    for attempt in range(attempts):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.3 * (attempt + 1), 1.0))


def isKeyFile(filename):
    return KEY_PATTERN.match(os.path.splitext(filename)[0]) is not None

def safeExtract(zipRef, destDir):
    """解压前校验成员路径，拒绝 zip slip（../）与绝对路径逃逸。"""
    destRoot = os.path.realpath(destDir)
    for member in zipRef.infolist():
        filename = member.filename
        # extractall 对不同平台的绝对路径处理不同，统一显式拒绝
        if os.path.isabs(filename):
            raise ValueError(f"压缩包内存在绝对路径: {filename}")
        target = os.path.realpath(os.path.join(destRoot, filename))
        try:
            common = os.path.commonpath([destRoot, target])
        except ValueError:  # 不同盘符，必然在目标目录之外
            common = None
        if common != destRoot:
            raise ValueError(f"压缩包内存在非法路径: {filename}")
    zipRef.extractall(destDir)

def removeKeyFiles(zipPath, reporter=None):
    """删除包里的 key 缩略图后原地覆盖。

    临时 zip 建在目标文件旁边而不是当前目录：一来 os.replace 不会跨盘符失败，
    二来 finally 能保证异常时不留下 temp_xxx.zip 残骸。
    """
    reporter = reporter or PlainReporter()
    targetPath = os.path.abspath(zipPath)
    handle, cleanedPath = tempfile.mkstemp(
        prefix=".cleaning-", suffix=".zip", dir=os.path.dirname(targetPath)
    )
    os.close(handle)
    try:
        with tempfile.TemporaryDirectory() as tempDir:
            with zipfile.ZipFile(targetPath, "r") as zipRef:
                safeExtract(zipRef, tempDir)

            with zipfile.ZipFile(cleanedPath, "w", zipfile.ZIP_DEFLATED) as newZipRef:
                for root, _, files in os.walk(tempDir):
                    for fileName in files:
                        if isKeyFile(fileName):
                            continue
                        filePath = os.path.join(root, fileName)
                        newZipRef.write(filePath, os.path.relpath(filePath, tempDir))
        replaceWithRetry(cleanedPath, targetPath)
        reporter.log(f"已清理并保存到原文件: {targetPath}")
        return True
    except (OSError, ValueError, zipfile.BadZipFile) as e:
        # 清理失败不影响已下载的原始 zip，提示一声即可
        reporter.log(f"清理 key 缩略图失败（原始文件已保留）: {e}")
        return False
    finally:
        if os.path.exists(cleanedPath):
            os.remove(cleanedPath)

def downloadFile(url, filePath, reporter=None):
    """下载到 .part 临时文件，校验是 zip 后才落到最终文件名。"""
    reporter = reporter or PlainReporter()
    partPath = f"{filePath}.part"
    try:
        response = fetch.get(url, stream=True)
        response.raise_for_status()
        with open(partPath, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                f.write(chunk)
        if not zipfile.is_zipfile(partPath):
            raise ValueError("服务器返回的不是有效的 zip 文件")
        replaceWithRetry(partPath, filePath)
        reporter.log(f"下载成功: {filePath}")
        return True
    except (requests.exceptions.RequestException, ValueError, OSError) as e:
        fetch.noteError(e)
        reporter.log(f"下载失败: {fetch.shortError(e)}")
        return False
    finally:
        if os.path.exists(partPath):
            os.remove(partPath)

_reservedPaths = set()
_reserveLock = threading.Lock()


def resolveZipPath(outputDir, packName, packId):
    """同名的包不互相覆盖：被别的包占用时在名字后面接上包 ID。

    并发下载时两个不同的包可能重名，光看文件存不存在会让它们抢同一个路径，
    所以选中的路径要先登记下来，后来者看到已被占用就自动加后缀。
    """
    plainPath = os.path.join(outputDir, f"{packName}.zip")
    suffixPath = os.path.join(outputDir, f"{packName}_{packId}.zip")
    fileName = f"{packName}.zip"
    with _reserveLock:
        # 同名文件如果就是这个包上次下的（中断导致账本没记全），直接沿用，
        # 否则会平白多出一个 <名字>_<id>.zip 副本。
        owner = None
        for recordedId, recordedName in loadIndex(outputDir).items():
            if recordedName == fileName:
                owner = recordedId
                break
        # 只有当同名文件明确属于「别的包」时才让路。
        # 账本里查不到归属的孤儿文件（中断残留、手工放进来的）直接认领覆盖，
        # 否则每次中断重跑都会多出一个副本。
        occupied = (os.path.exists(plainPath)
                    and owner is not None
                    and owner != str(packId))
        if occupied or plainPath in _reservedPaths:
            _reservedPaths.add(suffixPath)
            return suffixPath
        _reservedPaths.add(plainPath)
        return plainPath


INDEX_NAME = ".downloaded.json"
_indexLock = threading.Lock()


def cleanStaleTempFiles(outputDir):
    """清掉上次被强制中断（Ctrl+C、杀进程）时留下的临时文件。

    正常退出走 finally 就删干净了，这里只处理来不及执行 finally 的情况。
    """
    patterns = (".cleaning-*.zip", "*.zip.part", INDEX_NAME + ".tmp")
    removed = 0
    for pattern in patterns:
        for path in glob.glob(os.path.join(glob.escape(outputDir), pattern)):
            try:
                os.remove(path)
                removed += 1
            except OSError:
                pass
    return removed


def loadIndex(outputDir):
    """读取下载记录：包 ID -> 文件名。

    文件名来自网页上的包名，没法从文件名反推出 ID，所以单独记一份账。
    记录损坏或不存在时按空处理，大不了重新下一次。
    """
    path = os.path.join(outputDir, INDEX_NAME)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def updateIndex(outputDir, mutate):
    """按 mutate 修改账本并落盘。并发下载时多个线程会同时写，需要加锁。"""
    with _indexLock:
        index = loadIndex(outputDir)
        mutate(index)
        tmpPath = os.path.join(outputDir, INDEX_NAME + ".tmp")
        try:
            with open(tmpPath, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=1)
            replaceWithRetry(tmpPath, os.path.join(outputDir, INDEX_NAME))
        except OSError:
            # 记不上账不影响这次下载，最多下次重复下载一遍
            if os.path.exists(tmpPath):
                try:
                    os.remove(tmpPath)
                except OSError:
                    pass


def recordDownload(outputDir, packId, zipPath):
    """把包记进账本。"""
    updateIndex(outputDir,
                lambda index: index.update({str(packId): os.path.basename(zipPath)}))


def forgetDownload(outputDir, packId):
    """从账本里划掉一个包（下载失败时用）。"""
    updateIndex(outputDir, lambda index: index.pop(str(packId), None))


def findExistingPack(outputDir, packId):
    """按包 ID 查出已下载且文件仍在的 zip，找不到返回 None。"""
    fileName = loadIndex(outputDir).get(str(packId))
    if not fileName:
        return None
    path = os.path.join(outputDir, fileName)
    # 账本里有但文件被删了，就当没下过
    return path if os.path.exists(path) else None


def processUrl(url, outputDir=".", reporter=None, overwrite=False):
    """下载单个贴图包或 emoji 包。

    返回 "ok" / "skip" / "fail"，供调用方统计与显示进度。
    """
    reporter = reporter or PlainReporter()
    emojiMatch = EMOJI_PATTERN.search(url)
    stickerMatch = STICKER_PATTERN.search(url)
    if emojiMatch:
        packId = emojiMatch.group(1)
        base = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{packId}/iphone"
        candidates = [f"{base}/package.zip", f"{base}/package_animation.zip"]
    elif stickerMatch:
        packId = stickerMatch.group(1)
        # 旧域名 dl.stickershop.line.naver.jp 的 https 证书 hostname 不匹配，
        # 只能走明文 http；新版 CDN 域名的证书正常，内容一致。
        base = f"https://stickershop.line-scdn.net/stickershop/v1/product/{packId}/iphone"
        candidates = [f"{base}/stickers@2x.zip", f"{base}/stickerpack@2x.zip"]
    else:
        reporter.log(f"URL格式错误: {url}")
        return "fail"

    # 先按 ID 查一次，能跳过的话连取名字的请求都省了
    existing = findExistingPack(outputDir, packId)
    if existing and not overwrite:
        reporter.log(f"已存在，跳过: {os.path.basename(existing)}")
        return "skip"

    if existing:
        # overwrite：沿用上次的文件名原地覆盖，不然会多出一个带后缀的副本
        zipPath = existing
        packName = os.path.splitext(os.path.basename(existing))[0]
    else:
        packName = getPackName(url, packId, reporter)
        zipPath = resolveZipPath(outputDir, packName, packId)
        # 选定路径后立刻记账，而不是等下载完。
        # 否则下载完到记账之间被 Ctrl+C 打断，重跑时账本里查不到这个包，
        # 就会重新下一遍并因为同名而生成 <名字>_<id>.zip 副本。
        recordDownload(outputDir, packId, zipPath)

    for candidate in candidates:
        if downloadFile(candidate, zipPath, reporter):
            removeKeyFiles(zipPath, reporter)
            return "ok"
    # 没下成功就把账划掉，免得下次误以为下过了
    if not existing:
        forgetDownload(outputDir, packId)
    reporter.log(f"下载 {packName} 失败")
    return "fail"