.. _changelog:

ChangeLog
==========

v0.2.4 (2024-07-07)
-------------------

**功能更新**
1. 添加了多页识别下载功能，即使创作者有上传超过36个表情包也能一网打尽，无需挨个页面复制网址。
#. 优化`bdp.py`调用`bdp.txt`的方法，修复了即使不在同一目录下运行无法调用`bdp.txt`的错误。

**Function Updates**
1. Download all emoji packs from a creator, even if they have uploaded more than 36, eliminating the need to manually copy URLs from each page.
#. Optimized how `bdp.py` accesses the `bdp.txt` file, fixing an issue where the script couldn't locate `bdp.txt` if they weren't in the same directory.