.. _changelog:

ChangeLog
==========

v0.3.0 (2026-08-27)
-------------------

**结构调整**
1. 删除了 ``realease/`` 下的全部历史版本目录，仓库主干只保留最新一份源码，历史版本请到 GitHub Releases 查看。
#. ``dl.py`` ``bd.py`` ``bdp.py`` 三个重复度约 90% 的脚本合并为 ``line_dl`` 包，入口统一为根目录的 ``main.py``，同一个 bug 不必再改三遍。
#. 三种用法改为同一个命令的不同参数：直接给链接、无参数交互输入、``-f`` 读取链接文件；新增 ``-o`` 指定输出目录（默认 ``output``）。

**问题修复**
1. 移除了 ``bd.py`` 里无用的 ``from django import urls``，本项目不再需要 Django。
#. 修正 README 的依赖安装命令：实际只需要 ``requests`` 和 ``beautifulsoup4``；``zipfile`` 是标准库不应该用 pip 安装，缺失的 ``requests`` 反而没有列出。
#. 新增文件名净化，贴图名里的 ``/ \\ : * ? " < > |`` 等字符不再导致 Windows 下报错或在 Linux 下被当成路径分隔符；超长名字按 UTF-8 字节截断。
#. 取不到包名时回落到贴图包 ID，不再让所有包共用 ``unknown_emoji_name`` 而互相覆盖；同名的不同包会自动加 ID 后缀。
#. 清理 key 缩略图时的临时文件改建在目标文件旁边，并由 ``finally`` 保证删除，既不会跨盘符失败也不会残留 ``temp_xxx.zip``。
#. key 缩略图的判定由"文件名含 key"改为精确匹配 ``key.png`` / ``key@2x.png``，含 key 的普通贴图不会再被误删。
#. 所有网络请求统一走带 User-Agent、30 秒超时和自动重试的会话，不会再无限期挂起。
#. 贴图 CDN 的链接由 ``http://`` 改为 ``https://``。
#. 下载先写入 ``.part`` 并校验确实是 zip 后才改名，失败时不留下损坏文件。
#. 解压前校验压缩包内的路径，拒绝 zip slip。
#. 取包名时的语言段改写更通用，``/ja`` ``/ko`` 及不带语言后缀的链接现在也能取到名字；页面结构变化时用 ``og:title`` 兜底。
#. 单个链接出网络错误不再中断整批任务。
#. 读取链接文件时使用 ``utf-8-sig``，带 BOM 的文件第一行不会再失效，并支持 ``#`` 注释行。
#. 贴图包改用新版 CDN 域名 ``stickershop.line-scdn.net``：旧域名 ``dl.stickershop.line.naver.jp`` 的 https 证书 hostname 不匹配，只能走明文 http，新域名的证书正常且内容一致。
#. emoji 包的名称改从页面标题解析并去掉 ``– LINE Emoji | LINE STORE`` 之类的站点后缀，不会再得到 ``xxx – LINE Emoji _ LINE STORE.zip`` 这种文件名。
#. key 缩略图的匹配增加 ``001_key.png`` 形式，emoji 包里每张图对应的缩略图现在也能正确清理。
#. 新增 ``--proxy`` 参数，并在连不上服务器时统一提示如何配置代理（代理软件的 PAC 模式与系统代理开关对 python 无效）。
#. 连接超时由 30 秒改为 10 秒，网络不通时不必长时间干等；错误输出压缩成一行，不再刷屏。
#. 修正退出码：贴图包下载失败或链接格式错误时会正确返回 1。
#. 非交互环境（管道、CI）下不带参数运行不会再因 ``EOFError`` 崩栈。
#. 解压前的路径校验增加对绝对路径成员的拒绝。

**下载体验**
1. 新增跳过已下载功能：输出目录下维护 ``.downloaded.json`` 记录“包 ID → 文件名”，重复运行时已下过的包直接跳过，连取名字的请求都不会发。下载作者页时中途中断，重跑即可接着下。
#. 新增 ``--overwrite`` 参数强制重新下载，会原地覆盖原文件而不是生成副本。
#. 新增 ``-j`` / ``--jobs`` 并发下载，默认 4 个并发、上限 16。下载整个作者页（可能上百个包）的耗时大幅降低。
#. 新增进度条：批量下载时显示 ``[====----] 3/6 (50%) 成功 2 跳过 1``，并发线程的日志不会把进度条冲散。输出重定向到文件时自动不画进度条。
#. 作者页现在会先展开成具体的贴图包链接再下载，因此进度条能显示总数，也会打印“作者页 xxx 找到 N 个表情包”。

**已知问题**
Windows 上清理 key 缩略图时偶发 ``[WinError 5] 拒绝访问``。这不影响下载结果，
贴图包 zip 已完整保存，只是里面多保留了缩略图。详见 `README文档`_ 的报错与解决第 5 条。

**说明**
作者页的翻页逻辑本次未做改动，与 ``v0.2.4`` 保持一致。

v0.2.4 (2024-07-07)
-------------------

**功能更新**
1. 添加了多页识别下载功能，即使创作者有上传超过36个表情包也能一网打尽，无需挨个页面复制网址。
#. 优化`bdp.py`调用`bdp.txt`的方法，修复了即使不在同一目录下运行无法调用`bdp.txt`的错误。

**Function Updates**
1. Download all emoji packs from a creator, even if they have uploaded more than 36, eliminating the need to manually copy URLs from each page.
#. Optimized how `bdp.py` accesses the `bdp.txt` file, fixing an issue where the script couldn't locate `bdp.txt` if they weren't in the same directory.

v0.2.3 (2024-07-03)
-------------------

**功能更新**
1. 在`bd.py`脚本中添加**是否新建文件夹**功能。

**代码优化**
1. 优化代码块和函数名，减少了代码冗余。
#. 改变了库调用，减少依赖项。不再需要`shutil`库依赖。

**Function Updates**
1. Add **whether to create a new folder** functionality in the `bd.py` script.

**Code Optimization**
1. Optimized code blocks and function names, reducing code redundancy.
#. Changed library calls, reducing dependencies. No longer requires the `shutil` library.

v0.2.2 (2024-06-27)
-------------------

**功能更新**
1. 新增`bdp.py`脚本，目前已包含`dl.py` `bd.py`在内的所有功能，在此基础上修改了输入方式。如果你想要直接通过链接下载，推荐使用`bd.py`。`bdp.py`仅用于需要下载多个链接中的所有表情包。
#. 在使用`bdp.py`时，将在当前目录下生成`output`文件夹，所有的表情包都将下载在该文件夹中。
#. 使用方法见`README文档`。在使用`bdp.py`时，请一定在与脚本相同的目录下创建`bdp.txt`文件。

**Feature Updates**
1. Added `bdp.py` script, which now includes all the functionalities of `dl.py` and `bd.py`. The input method has been modified based on this. If you want to download directly from a link, it's recommended to use `bd.py`. `bdp.py` is only used for downloading all the sticker packs from multiple links.
#. When using `bdp.py`, an `output` folder will be created in the current directory, and all the sticker packs will be downloaded into this folder.
#. For usage, please refer to the `README document`. When using `bdp.py`, make sure to create a `bdp.txt` file in the same directory as the script.

.. _README文档: https://github.com/djmh1793225009/LINE_sticker_emoji_downloader/blob/main/README.md

.. _README document: https://github.com/djmh1793225009/LINE_sticker_emoji_downloader/blob/main/README.md

v0.2.1 (2024-06-09)
-------------------

**功能更新**
1. 修改了动态表情包和静态表情包的下载顺序，减少下载请求。
#. 整合了批量下载的功能，详情请见 `README.md`。
#. 使用大小驼峰法减少了代码冗余。
#. 修改了正则表达式使其更加兼容LINE的表情包规则。
#. 学习了非常好markdown使我的README旋转。
**Feature Updates**
1. Modified the download order of animated and static stickers to reduce download requests.
#. Integrated batch download functionality. For details, please refer to `README.md`.
#. Reduced code redundancy using upper camel case notation.
#. Modified the regular expression to make it more compatible with LINE's sticker rules.

.. _README.md: https://github.com/djmh1793225009/LINE_sticker_emoji_downloader/blob/main/README.md

v0.1.2(2024-05-16)
-------------------

This version adds a feature to delete key thumbnails from zip files, saving me the trouble of repeatedly deleting key files and greatly improving my work efficiency!
In addition, since the script written by ChatGPT-4o still has bugs, I have manually modified some of the code, so the current code is no longer completely AI-generated, but is now **partially AI-generated!**
However, this version refers to `shutil` `zipfile` `requests` and `BeautifulSoup4` dependencies, and you can install the dependencies by the following command.
```sh
python -m pip install requests beautifulsoup4 zipfile shutil
```

v0.1.1(2024-05-16)
-------------------

This version adds the function of crawling the name of the expression pack from the web page and renaming it, so now you won't encounter the problem of batch downloading because the names are all the same!
However, this version refers to `requests` and `BeautifulSoup` dependencies, and you can install the dependencies by the following command.
```sh
python -m pip install BeautifulSoup requests
```
**Generated by AI**

v0.1.0(2024-05-16)
-------------------

This version distinguishes emoji from sticker, and then uses regular expressions to match the ID in the url and download it. The script is very elementary, but I hope you can enjoy it.
Generated through AI
