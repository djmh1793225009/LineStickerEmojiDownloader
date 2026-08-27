"""文件名净化。

LINE 的贴图名里常见 / \\ : * ? " < > | 和各种 emoji 字符，
直接拼成文件名会在 Windows 上抛异常、在 Linux 上把 / 变成路径分隔符。
"""

import re

# Windows 与 POSIX 下都不能出现在文件名里的字符，外加控制字符
INVALID_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')

# Windows 保留设备名，即使带扩展名也不能用
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

MAX_BYTES = 120

# og:title / <title> 的格式是 "包名 – LINE stickers | LINE STORE"，
# 贴图页能从 mdCMN38Item01Ttl 拿到干净的名字，但 emoji 页只有这个标题，
# 后缀不去掉就会得到 "xxx – LINE Emoji _ LINE STORE.zip" 这种文件名。
SITE_SUFFIX = re.compile(
    r"\s*[|｜]\s*LINE\s*STORE\s*$", re.IGNORECASE)
CATEGORY_SUFFIX = re.compile(
    r"\s*[–—-]\s*LINE\s*(?:emoji|emojis|sticker|stickers|絵文字|貼圖|表情貼|스티커|이모지)\s*$",
    re.IGNORECASE)


def stripSiteTitle(title):
    """去掉商店标题里的站点与分类后缀，只留包名本身。"""
    text = SITE_SUFFIX.sub("", title or "")
    return CATEGORY_SUFFIX.sub("", text).strip()


def truncateBytes(text, limit=MAX_BYTES):
    """按 UTF-8 字节数截断，避免中文/emoji 名字超出文件系统限制。"""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    return encoded[:limit].decode("utf-8", "ignore")


def sanitize(name, fallback):
    """把网页上抓来的包名转成安全的文件名，无法使用时回落到 fallback。"""
    cleaned = INVALID_CHARS.sub("_", name or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Windows 会静默丢掉结尾的点和空格
    cleaned = truncateBytes(cleaned).strip().rstrip(". ")
    if not cleaned or cleaned.upper() in RESERVED_NAMES:
        return fallback
    return cleaned
