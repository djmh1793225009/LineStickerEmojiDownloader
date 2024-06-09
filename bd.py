import requests
from bs4 import BeautifulSoup
import subprocess
import re
import os
import zipfile
import shutil

def get_sticker_urls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    stickerUrls = [f"https://store.line.me{link['href']}" 
                    for link in soup.find_all('a', href=True)
                    if '/stickershop/product/' in link['href']]
    return stickerUrls

def download_file(url, filename):
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

def fetch_emoji_name(url):
    english_url = url.replace('/zh-Hant', '/en')
    try:
        response = requests.get(english_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
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

    temp_zip_filename = f"temp_{zip_filename}"
    with zipfile.ZipFile(temp_zip_filename, 'w') as new_zip_ref:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if "key" not in file:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    new_zip_ref.write(file_path, arcname)

    def delete_files_in_folder(folder_path):
        shutil.rmtree(folder_path)

    delete_files_in_folder(temp_dir)
    os.replace(temp_zip_filename, zip_filename)
    print(f"已清理并保存到原文件: {zip_filename}")

def process_url(url):
    emoji_pattern = re.compile(r"https://store\.line\.me/emojishop/product/([a-zA-Z0-9]{23,25})")
    sticker_pattern = re.compile(r"https://store\.line\.me/stickershop/product/(\d{6,9})")

    emoji_match = emoji_pattern.search(url)
    sticker_match = sticker_pattern.search(url)

    if emoji_match:
        ID = emoji_match.group(1)
        package_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package.zip"
        animation_url = f"https://stickershop.line-scdn.net/sticonshop/v1/sticon/{ID}/iphone/package_animation.zip"
        emoji_name = fetch_emoji_name(url)
        zip_filename = f"{emoji_name}.zip"

        if download_file(package_url, zip_filename):
            remove_key_files(zip_filename)
        else:
            if download_file(animation_url, zip_filename):
                remove_key_files(zip_filename)
            else:
                print("以上是报错信息")

    elif sticker_match:
        ID = sticker_match.group(1)
        sticker_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickers@2x.zip"  # 调整下载顺序
        stickerpack_url = f"http://dl.stickershop.line.naver.jp/products/0/0/1/{ID}/iphone/stickerpack@2x.zip"
        emoji_name = fetch_emoji_name(url)
        zip_filename = f"{emoji_name}.zip"

        if download_file(sticker_url, zip_filename):
            remove_key_files(zip_filename)
        else:
            if download_file(stickerpack_url, zip_filename):
                remove_key_files(zip_filename)
            else:
                print("以上是报错信息")

    else:
        print("URL格式错误")

if __name__ == "__main__":
    input_url = input("请输入类似的网址: ")
    if '/author/' in input_url:
        sticker_urls = get_sticker_urls(input_url)

        if not sticker_urls:
            print(f"在 {input_url} 中没有找到表情包链接。")
        else:
            for url in sticker_urls:
                print(f"正在处理: {url}")
                process_url(url)
    else:
        process_url(input_url)