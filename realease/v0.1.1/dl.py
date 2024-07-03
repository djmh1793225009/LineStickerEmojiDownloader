import sys
import requests
import re
from bs4 import BeautifulSoup

def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"下载成功: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return False
    return True

def fetch_emoji_name(url):
    # 替换URL中的zh-Hant为en以尽量获取英文的表情包名字
    english_url = url.replace('/zh-Hant', '/en')
    try:
        response = requests.get(english_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含表情包名字的标签
        title_tag = soup.find('p', class_='mdCMN38Item01Ttl')
        if title_tag:
            return title_tag.get_text().strip()
        else:
            return "unknown_emoji_name"
    except requests.exceptions.RequestException as e:
        print(f"获取表情包名字失败: {e}")
        return "unknown_emoji_name"

def main(url):
    emoji_pattern = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{24})")
    sticker_pattern = re.compile(r"https://store\.line\.me/stickershop/product/(\d{8})")

    emoji_match = emoji_pattern.search(url)
    sticker_match = sticker_pattern.search(url)

    if emoji_match:
        # Step 2
        ID = emoji_match.group(1)
        animation_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        package_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
        emoji_name = fetch_emoji_name(url)

        if not download_file(animation_url, f"{emoji_name}.zip"):
            if not download_file(package_url, f"{emoji_name}.zip"):
                print("以上是报错信息")
    elif sticker_match:
        # Step 3
        ID = sticker_match.group(1)
        stickerpack_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
        sticker_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"
        emoji_name = fetch_emoji_name(url)

        if not download_file(stickerpack_url, f"{emoji_name}.zip"):
            if not download_file(sticker_url, f"{emoji_name}.zip"):
                print("以上是报错信息")
    else:
        print("URL格式错误")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python dl.py <url>")
    else:
        main(sys.argv[1])