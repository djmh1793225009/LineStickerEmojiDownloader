import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import tempfile


# ---------------------- 公共函数 ----------------------
def sanitize_filename(filename):
    """移除或替换 Windows 文件名中的非法字符"""
    # Windows 非法字符: \ / : * ? " < > |
    # 以及控制字符，这里简单替换为下划线
    return re.sub(r'[\\/*?:"<>|]', '_', filename)


def getStickerUrls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [
        f"https://store.line.me{link['href']}"
        for link in soup.find_all('a', href=True)
        if '/stickershop/product/' in link['href']
    ]


def downloadFile(url, filename):
    filename = sanitize_filename(filename)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"下载成功: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return False


def getEmojiName(url):
    englishUrl = url.replace('/zh-Hant', '/en')
    try:
        response = requests.get(englishUrl)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        titleTag = soup.find('p', class_='mdCMN38Item01Ttl')
        if titleTag:
            return titleTag.get_text().strip()
        else:
            return "unknown_emoji_name"
    except requests.exceptions.RequestException as e:
        print(f"获取表情包名字失败: {e}")
        return "unknown_emoji_name"


def removeKeyFiles(zipFilename):
    with tempfile.TemporaryDirectory() as tempDir:
        with zipfile.ZipFile(zipFilename, 'r') as zipRef:
            zipRef.extractall(tempDir)

        tempZipFilename = f"temp_{zipFilename}"
        with zipfile.ZipFile(tempZipFilename, 'w') as newZipRef:
            for root, _, files in os.walk(tempDir):
                for file in files:
                    if "key" not in file:
                        filePath = os.path.join(root, file)
                        arcname = os.path.relpath(filePath, tempDir)
                        newZipRef.write(filePath, arcname)

        os.replace(tempZipFilename, zipFilename)
        print(f"已清理并保存到原文件: {zipFilename}")


def processUrl(url):
    emojiPattern = re.compile(
        r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{23,25})"
    )
    stickerPattern = re.compile(
        r"https://store\.line\.me/stickershop/product/(\d{6,9})"
    )
    emojiMatch = emojiPattern.search(url)
    stickerMatch = stickerPattern.search(url)

    if emojiMatch:
        ID = emojiMatch.group(1)
        packageUrl = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
        animationUrl = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        emojiName = sanitize_filename(getEmojiName(url))
        zipFilename = f"{emojiName}.zip"

        if downloadFile(packageUrl, zipFilename):
            removeKeyFiles(zipFilename)
        elif downloadFile(animationUrl, zipFilename):
            removeKeyFiles(zipFilename)
        else:
            print(f"下载 {emojiName} 失败")

    elif stickerMatch:
        ID = stickerMatch.group(1)
        stickerUrl = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"
        stickerpackUrl = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
        emojiName = sanitize_filename(getEmojiName(url))
        zipFilename = f"{emojiName}.zip"

        if downloadFile(stickerUrl, zipFilename):
            removeKeyFiles(zipFilename)
        elif downloadFile(stickerpackUrl, zipFilename):
            removeKeyFiles(zipFilename)
        else:
            print(f"下载 {emojiName} 失败")

    else:
        print("URL格式错误")


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


# ---------------------- 询问下载目录 ----------------------
def ask_output_directory() -> str:
    """询问用户是否下载到指定文件夹，返回目标目录路径（已确保存在）"""
    choice = input("是否下载到指定文件夹？(Y/n): ").strip().lower()
    if choice.lower() != 'n':
        folder = input("请输入文件夹路径（相对或绝对路径，默认output）: ").strip()
        if not folder:
            folder = "output"
        os.makedirs(folder, exist_ok=True)
        return folder
    else:
        # 下载到当前目录
        return "."


# ---------------------- 模式实现 ----------------------
def mode1():
    """下载单个表情包（交互输入URL）"""
    target_dir = ask_output_directory()
    original_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        url = input("请输入表情包URL: ").strip()
        processUrl(url)
    finally:
        os.chdir(original_dir)


def mode2():
    """下载作者的所有表情包（交互输入作者URL）"""
    target_dir = ask_output_directory()
    original_dir = os.getcwd()
    os.chdir(target_dir)
    try:
        authorUrl = input("请输入作者主页URL: ").strip()
        authorUrl = authorUrl.split('?page=')[0]
        stickerUrls = processAuthorUrl(authorUrl)
        if not stickerUrls:
            print(f"在 {authorUrl} 中没有找到表情包链接。")
        else:
            for url in stickerUrls:
                print(f"正在处理: {url}")
                processUrl(url)
    finally:
        os.chdir(original_dir)


def mode3():
    """读取指定txt文件进行批量下载"""
    target_dir = ask_output_directory()
    original_dir = os.getcwd()
    try:
        txtPath = input(
            "请输入txt文件路径（直接回车使用当前目录下的 bdp.txt）: "
        ).strip()
        print("使用文件路径：", os.path.join(os.getcwd(), txtPath))
        if not txtPath:
            txtPath = "bdp.txt"
        if not os.path.exists(txtPath):
            print(f"文件 {txtPath} 不存在")
            return

        with open(txtPath, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        # 切换到目标目录
        os.chdir(target_dir)

        for url in urls:
            if '/author/' in url:
                authorUrl = url.split('?page=')[0]
                stickerUrls = processAuthorUrl(authorUrl)
                if not stickerUrls:
                    print(f"在 {authorUrl} 中没有找到表情包链接。")
                else:
                    for stickerUrl in stickerUrls:
                        print(f"正在处理: {stickerUrl}")
                        processUrl(stickerUrl)
            else:
                processUrl(url)
    finally:
        os.chdir(original_dir)


# ---------------------- 主程序 ----------------------
if __name__ == "__main__":
    print(f"当前路径：{os.getcwd()}")
    print("请选择模式：")
    print("1 - 下载单个表情包（交互输入URL）")
    print("2 - 下载作者的所有表情包（交互输入作者URL）")
    print("3 - 读取指定txt文件批量下载")
    choice = input("请输入数字(1/2/3): ").strip()

    if choice == '1':
        mode1()
    elif choice == '2':
        mode2()
    elif choice == '3':
        mode3()
    else:
        print("无效选择，程序退出。")
