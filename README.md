[English README](./docs/README_EN.md) /[Telegram](https://t.me/yume_yuki)/[QQ](https://qm.qq.com/q/dCn4enLQly)

# LINE贴图包和emoji下载器

这个项目可以用来下载LINE上的贴纸和emoji，同时支持动图和静态图，以及批量下载的操作。所有python脚本内容的生成均来自于AI  
本项目禁止用于非法用途，禁止贩卖。**如果喜欢这些stickers，请支持正版line贴纸**

## 目录

- [LINE贴图包和emoji下载器](#line贴图包和emoji下载器)
  - [目录](#目录)
  - [脚本依赖](#脚本依赖)
  - [项目结构](#项目结构)
  - [使用方法](#使用方法)
    - [跳过已下载](#跳过已下载)
    - [并发下载与进度](#并发下载与进度)
  - [报错与解决](#报错与解决)
    - [1. 无法获取表情包名](#1-无法获取表情包名)
    - [2. 无法下载](#2-无法下载)
    - [3. 下载后未删除temp文件](#3-下载后未删除temp文件)
    - [4. 下载不完全](#4-下载不完全)
    - [5. 清理缩略图失败（`[winerror-5]`-`[winerror-32]`）](#5-清理缩略图失败winerror-5--winerror-32)
    - [6. 其他](#6-其他)
  - [鸣谢](#鸣谢)
  - [许可证](#许可证)

## 脚本依赖

> 首先请确保你的电脑里安装了**python3.6**以上的版本且将python列入计算机中的**PATH**！确保你的pip是最新版本，你可以通过运行`python -m pip install --upgrade pip`来更新你的pip。

你可以运行下面的命令以安装依赖库。
```bash
pip install requests beautifulsoup4
```

> `zipfile`、`tempfile` 等都是 python 自带的标准库，无需也不应该用 pip 安装。

## 项目结构

`v0.3.0`起，三个功能重复的脚本合并成了一个包，入口统一为根目录的`main.py`。

```
main.py            # 入口，所有用法都从这里走
line_dl/
  cli.py           # 命令行参数解析
  fetch.py         # 统一的 HTTP 会话（超时、重试、User-Agent）
  naming.py        # 文件名净化
  pack.py          # 单个贴图包 / emoji 包的下载与清理
  author.py        # 作者页翻页与链接嗅探
  progress.py      # 并发下载时的进度条
docs/bdp.txt       # 批量下载的链接清单范例
```

## 使用方法

在项目根目录下运行`main.py`即可，三种用法对应旧版的`dl.py`、`bd.py`、`bdp.py`。

| 用法 | 命令 | 说明 |
|------|------|------|
| 下载指定链接 | `python main.py <url> [<url> ...]` | 可以一次给多个链接，贴图包、emoji 包、作者页都支持。 |
| 交互式输入 | `python main.py` | 直接运行，把链接粘贴在提示后面。 |
| 从文件批量下载 | `python main.py -f bdp.txt` | 每行一个链接，`#`开头的行会被当作注释忽略，范例见[此处](./docs/bdp.txt)。 |

可选参数：

| 参数 | 说明 |
|------|------|
| `-o DIR` / `--output DIR` | 指定输出目录，默认为`output`。想下载到当前目录就用`-o .`。 |
| `-f FILE` / `--file FILE` | 从文本文件读取链接清单，可与直接给出的链接混用。 |
| `-j N` / `--jobs N` | 并发下载数，默认`4`，最大`16`。用`-j 1`改回逐个下载。 |
| `--overwrite` | 重新下载已经下过的包（默认会跳过）。 |
| `--proxy URL` | 指定代理，例如`--proxy http://127.0.0.1:7897`。 |
| `-h` / `--help` | 查看完整帮助。 |

### 跳过已下载

脚本会在输出目录下维护一个`.downloaded.json`，记录“贴图包 ID → 文件名”。再次运行时已经下过的包会直接跳过，**不会重复下载，也不会重复发请求**，所以下载作者页时中途按`Ctrl+C`中断，重跑就能接着下没下完的部分。

- 如果你手动删掉了某个 zip，重跑时只会补下这一个。
- 想强制重新下载，加`--overwrite`，它会原地覆盖原文件而不是生成副本。
- 删掉`.downloaded.json`会让所有包都被当成没下过。

### 并发下载与进度

下载多个包时默认 4 个并发，命令行里会显示一个进度条：

```
[==============--------------] 3/6 (50%)  成功 2  跳过 1
```

下载 158 个包这种规模建议保持默认或适当调高（如`-j 8`），但不建议开太大，既容易被 LINE 限流也不礼貌。输出重定向到文件时不会画进度条，只保留日志行。

范例：

```bash
python main.py https://store.line.me/stickershop/product/1419581/zh-Hant
python main.py https://store.line.me/stickershop/author/831836/zh-Hant -o ./stickers
python main.py -f docs/bdp.txt
```

## 报错与解决

### 1. 无法获取表情包名
`v0.3.0`起，抓不到名字时会自动改用贴图包 ID 作为文件名（例如`1419581.zip`），不会再出现所有包都叫`unknown_emoji_name`而互相覆盖的情况。如果你希望拿到正确的名字，请检查您的网络环境，您的网络ip是否在line提供服务的区域外。

### 2. 无法下载
`v0.3.0`起，下载先写入`.part`临时文件并校验确实是 zip 之后才改名，因此失败时不会再留下损坏的 zip 或空文件夹。如果仍然报错，请提起issues并附上完整的报错输出。

### 3. 下载后未删除temp文件
`v0.3.0`起，清理用的临时文件建在目标文件旁边并由`finally`保证删除，正常情况下不会残留。
- 如果你用的手机termux并在storage目录尝试下载，那你真是buff叠满了，部分手机的termux在storage目录及其子目录下删除文件会被系统拦截。
- 如果你用的是别的设备或未在storage目录下出现此错误，请检查你是否有该文件夹目录下的权限。

### 4. 下载不完全
- 当创作者的表情包上传数量超过了36个时，脚本会自动翻页嗅探，无需手动复制每一页的网址。

### 5. 清理缩略图失败（`[WinError 5]` / `[WinError 32]`）

如果看到一行类似
```
清理 key 缩略图失败（原始文件已保留）: [WinError 5] 拒绝访问。...
```

这**不是下载失败**。贴图包的 zip 已经完整下载并保存好了，只是脚本在尝试把它里面的 `key` 缩略图（`key.png` 或 `001_key.png` 这类）删掉重新打包时，`os.replace` 被系统拒绝。该压缩包仍然完好可用，只是里面多保留了些缩略图而已。

- 该现象在 Windows 上偶发，推测与刚落盘的文件被占用（杀毒软件扫描、OneDrive 同步、索引服务等）有关，尚未定位到确切原因。
- 如果你能稳定复现，请提起 issues 并附上：
  - 完整的报错输出
  - 出错的是哪一类包（贴图包 / emoji 包）
  - 你使用的 Windows 版本与杀毒 / 同步软件
  若能找到复现规律，将有助于根因修复。

### 6. 其他
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