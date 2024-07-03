import sys
import requests
import re
import os
from bs4 import BeautifulSoup
import zipfile
import shutil

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

def remove_key_files(zip_filename):
    temp_dir = "temp_zip_extract"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 创建一个新的zip文件
    temp_zip_filename = f"temp_{zip_filename}"
    with zipfile.ZipFile(temp_zip_filename, 'w') as new_zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if "key" not in file:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    new_zip_ref.write(file_path, arcname)

    # 删除临时目录中的文件和子目录
    def delete_files_in_folder(folder_path):
        shutil.rmtree(folder_path)
    folder_to_clean = (temp_dir)
    delete_files_in_folder(folder_to_clean)

    # 重命名新的zip文件
    os.replace(temp_zip_filename, zip_filename)
    print(f"已清理并保存到原文件: {zip_filename}")

def main(url):
    emoji_pattern = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{24})")
    sticker_pattern = re.compile(r"https://store\.line\.me/stickershop/product/(\d{8})")

    emoji_match = emoji_pattern.search(url)
    sticker_match = sticker_pattern.search(url)

    if emoji_match:
        ID = emoji_match.group(1)
        animation_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        package_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
        emoji_name = fetch_emoji_name(url)
        zip_filename = f"{emoji_name}.zip"

        if not download_file(animation_url, zip_filename):
            if not download_file(package_url, zip_filename):
                print("以上是报错信息")
        
        remove_key_files(zip_filename)
    elif sticker_match:
        ID = sticker_match.group(1)
        stickerpack_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
        sticker_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"
        emoji_name = fetch_emoji_name(url)
        zip_filename = f"{emoji_name}.zip"

        if not download_file(stickerpack_url, zip_filename):
            if not download_file(sticker_url, zip_filename):
                print("以上是报错信息")

        remove_key_files(zip_filename)
    else:
        print("URL格式错误")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python dl.py <url>")
    else:
        main(sys.argv[1])