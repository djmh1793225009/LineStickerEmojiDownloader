import sys
import requests
import re

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

def main(url):
    emoji_pattern = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{24})")
    sticker_pattern = re.compile(r"https://store\.line\.me/stickershop/product/(\d{8})")

    emoji_match = emoji_pattern.search(url)
    sticker_match = sticker_pattern.search(url)

    if emoji_match:
        # Step 2
        ID = emoji_match.group(1)
        animation_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        if not download_file(animation_url, "package_animation.zip"):
            package_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
            if not download_file(package_url, "package.zip"):
                print("以上是报错信息")
    elif sticker_match:
        # Step 3
        ID = sticker_match.group(1)
        stickerpack_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
        if not download_file(stickerpack_url, "stickerpack@2x.zip"):
            sticker_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"
            if not download_file(sticker_url, "sticker@2x.zip"):
                print("以上是报错信息")
    else:
        print("URL格式错误")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python dl.py <url>")
    else:
        main(sys.argv[1])