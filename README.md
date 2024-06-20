[English README](./README_EN.md) /[Telegram](https://t.me/Eschericia0)/[QQ](https://qm.qq.com/q/dCn4enLQly)

# LINE贴图包和emoji下载器  

这个项目可以用来下载LINE上的贴纸和emoji，同时支持动图和静态图，以及批量下载的操作。所有内容的生成均来自于AI（chatGPT-4o, Gemini1.5PRO）  

## 脚本依赖
>首先请确保你的电脑里安装了**python3.6**以上的版本且将python列入计算机中的**PATH**！确保你的pip是最新版本，你可以通过运行``python -m pip install --upgrade pip``来更新你的pip。  

你可以运行``pip install BeautifulSoup4 zipfile shutil``以安装依赖库。

## 使用方法

``dl.py``仅有下载单个贴图包的功能，~~所以更建议你使用``bd.py``~~。如果你想要使用``dl.py``，请复制你想下载的贴图包网址url，你可以在相同目录下运行``python dl.py <url>``来下载。  

如果你想下载单个贴图包或同一个作者的所有贴图包，请复制你想下载的贴图包网址或作者网址，并在相同目录下运行``python bd.py``，并将url粘贴在提示后，脚本便可实现批量下载。

>
>注：若输出文件名为未知表情包名，请检测您的ip是否在line提供服务的区域外。  
>如果出现了其他问题，请提起issue。  
>

## 如果喜欢这些stickers，请支持正版line贴纸