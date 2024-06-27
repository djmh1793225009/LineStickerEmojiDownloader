[Chinese README](../README.md) /[Telegram](https://t.me/Eschericia0)/[QQ](https://qm.qq.com/q/dCn4enLQly)

# LINE Stickers and Emoji Downloader

This project can be used to download LINE stickers and emoji, including animated and static images, and batch download operations. All the python script content is generated by AI (chatGPT-4o, Gemini1.5PRO).  
This project is prohibited for illegal use and sale. **If you like these stickers, please support the official LINE stickers**

## Directory

- [LINE Stickers and Emoji Downloader](#line-stickers-and-emoji-downloader)
  - [Directory](#directory)
  - [Script Dependencies](#script-dependencies)
  - [How to use](#how-to-use)
  - [Errors and solutions](#errors-and-solutions)
    - [1. Unable to get the sticker pack name](#1-unable-to-get-the-sticker-pack-name)
    - [2. Unable to download](#2-unable-to-download)
    - [3. Temp files are not deleted after download](#3-temp-files-are-not-deleted-after-download)
    - [4. Others](#4-others)
  - [Acknowledgement](#acknowledgement)
  - [License](#license)

## Script Dependencies

> First, make sure that your computer has **python3.6** or above installed and python is included in your computer's **PATH**! Ensure your pip is the latest version, you can update your pip by running `python -m pip install --upgrade pip`.

You can run the following command to install the dependent libraries.
```bash
pip install BeautifulSoup4 zipfile shutil
```

## How to use

| File name | Function                                                                | How to use                                                       |
|-----------|-------------------------------------------------------------------------|------------------------------------------------------------------|
| `dl.py`   | This file only has the function of downloading a single sticker pack    | Please copy the sticker pack URL `url` you want to download, and you can run `python dl.py <url>` in the same directory to download.                                  |
| `bd.py`   | Download a single sticker or batch download all stickers from a creator | Please copy the sticker pack URL or creator URL you want to download, and enter `python bd.py` in the same directory and run it, paste the URL after the prompt. |
| `bdp.py`  | Similar to `bd.py`                                                      | Paste the URLs of the texture packs you want to download and the author's URLs into `bdp.txt` in the same directory as the script, separated by carriage returns. See [here](./docs/bdp.txt) for an example. Then run `python bd.py` and the script will automatically download the textures in bulk.                                     |

## Errors and solutions

### 1. Unable to get the sticker pack name
If the downloaded file is named `unknown_emoji_name`, please check your network environment and whether your network IP is outside the region where LINE provides services.

### 2. Unable to download
If the program runs an error and leaves an empty folder in the directory, please raise an issue and try to reproduce the content. The problem has occurred before, but the problem was solved and forgotten how to reproduce the problem.

### 3. Temp files are not deleted after download
- If you use termux on your mobile phone and try to download in the storage directory, then you have stacked the buffs. The termux on some mobile phones intercepts the deletion of files in the storage directory and its subdirectories.
- If you are using another device or the error does not occur in the storage directory, please check if you have permissions in the directory of this folder.

### 4. Others
If you encounter other problems besides the above, please raise an issue and reproduce the problem record submitted. Thank you for your support of this project.

## Acknowledgement

Thanks to the following friends and contributors: (in no particular order)  
[@kaixinol](https://github.com/kaixinol) | [@ZGQ Inc.](https://github.com/ZGQ-inc) | [@CPuddingOwO](https://github.com/CPuddingOwO) 

## License

```
MIT License

Copyright (c) 2024 元亓

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```