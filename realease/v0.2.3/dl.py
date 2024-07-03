import sys
import requests
from bs4 import BeautifulSoup
import re
import os
import zipfile
import tempfile

def downloadFile(url, filename):
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
    emojiPattern = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{23,25})")
    stickerPattern = re.compile(r"https://store\.line\.me/stickershop/product/(\d{6,9})")
    emojiMatch = emojiPattern.search(url)
    stickerMatch = stickerPattern.search(url)

    if emojiMatch:
        ID = emojiMatch.group(1)
        packageUrl = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
        animationUrl = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        emojiName = getEmojiName(url)
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
        emojiName = getEmojiName(url)
        zipFilename = f"{emojiName}.zip"

        if downloadFile(stickerUrl, zipFilename):
            removeKeyFiles(zipFilename)
        elif downloadFile(stickerpackUrl, zipFilename):
            removeKeyFiles(zipFilename)
        else:
            print(f"下载 {emojiName} 失败")

    else:
        print("URL格式错误")

def main():
    if len(sys.argv) != 2:
        print("用法: python dl.py <url>")
    else:
        processUrl(sys.argv[1])

if __name__ == "__main__":
    main()