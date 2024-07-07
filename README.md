[English README](./docs/README_EN.md) /[Telegram](https://t.me/yume_yuki)/[QQ](https://qm.qq.com/q/dCn4enLQly)

# LINE贴图包和emoji下载器

这个项目可以用来下载LINE上的贴纸和emoji，同时支持动图和静态图，以及批量下载的操作。所有python脚本内容的生成均来自于AI（chatGPT-4o, Gemini1.5PRO）  
本项目禁止用于非法用途，禁止贩卖。**如果喜欢这些stickers，请支持正版line贴纸**

## 目录

- [LINE贴图包和emoji下载器](#line贴图包和emoji下载器)
  - [目录](#目录)
  - [脚本依赖](#脚本依赖)
  - [使用方法](#使用方法)
  - [报错与解决](#报错与解决)
    - [1. 无法获取表情包名](#1-无法获取表情包名)
    - [2. 无法下载](#2-无法下载)
    - [3. 下载后未删除temp文件](#3-下载后未删除temp文件)
    - [4. 下载不完全](#4-下载不完全)
    - [5. 其他](#5-其他)
  - [鸣谢](#鸣谢)
  - [许可证](#许可证)

## 脚本依赖

> 首先请确保你的电脑里安装了**python3.6**以上的版本且将python列入计算机中的**PATH**！确保你的pip是最新版本，你可以通过运行`python -m pip install --upgrade pip`来更新你的pip。

你可以运行下面的命令以安装依赖库。
```bash
pip install BeautifulSoup4 zipfile
```

## 使用方法

| 文件名   | 功能                                    | 使用方法                                                                                    |
|----------|----------------------------------------|--------------------------------------------------------------------------------------------|
| `dl.py`  | 该文件仅有下载单个贴图包的功能            | 请复制你想下载的贴图包网址`url`，你可以在相同目录下运行`python dl.py <url>`来下载。             |
| `bd.py`  | 下载单个贴图或批量下载某个创作者的所有贴图 | 请复制你想下载的贴图包网址或作者网址，并在相同目录下输入`python bd.py`并运行，将url粘贴在提示后。 |
| `bdp.py` | 与`bd.py`类似                         | 请将你想下载的贴图包网址及作者网址粘贴在与脚本相同目录下的`bdp.txt`内，通过回车隔开不同网址，范例请见[此处](./docs/bdp.txt)。然后运行`python bdp.py`，脚本将自动批量下载。 |

## 报错与解决

### 1. 无法获取表情包名
如果下载后的文件名为`unknown_emoji_name`，请检查您的网络环境，您的网络ip是否在line提供服务的区域外。

### 2. 无法下载
如果程序运行后报错并在目录下留下了一个空文件夹，请提起issues并尝试复现内容。问题曾经出现过，但是问题解决后忘记了如何复现问题。

### 3. 下载后未删除temp文件
- 如果你用的手机termux并在storage目录尝试下载，那你真是buff叠满了，部分手机的termux在storage目录及其子目录下删除文件会被系统拦截。
- 如果你用的是别的设备或未在storage目录下出现此错误，请检查你是否有该文件夹目录下的权限。

### 4. 下载不完全
- 当创作者的表情包上传数量超过了36个时，表情包仅能嗅探单页的表情包，请使用`bdp.py`下载，将作者的所有表情包页面url粘贴进`bdp.txt`。
- `v0.2.4`版本后已修复此问题。

### 5. 其他
如果你遇到了除以上问题外的其他问题，请提起issues并列出详细复现问题过程记录并提交。感谢你对本项目的支持。

## 鸣谢

感谢以下朋友及contributor：(排名不分先后)  
[@CPuddingOwO](https://github.com/CPuddingOwO) | [@kaixinol](https://github.com/kaixinol) | [@ZGQ Inc.](https://github.com/ZGQ-inc) 

## 许可证

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