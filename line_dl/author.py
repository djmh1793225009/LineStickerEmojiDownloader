"""作者页的翻页与链接嗅探。翻页逻辑与 v0.2.4 保持一致，本次迭代不做改动，只把网络请求换成统一的会话。"""

from bs4 import BeautifulSoup

from . import fetch


def getStickerUrls(url):
    response = fetch.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return [f"https://store.line.me{link['href']}"
            for link in soup.find_all('a', href=True)
            if '/stickershop/product/' in link['href']]


def processAuthorUrl(url):
    i = 1
    allStickerUrls = []
    while True:
        pageUrl = f"{url}?page={i}"
        print(f"正在检查页面: {pageUrl}")
        stickerUrls = getStickerUrls(pageUrl)
        if stickerUrls:
            allStickerUrls.extend(stickerUrls)
            i += 1
        else:
            break
    return allStickerUrls