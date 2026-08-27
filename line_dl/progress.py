"""下载进度显示。

并发下载时多个线程会同时输出，直接 print 会把进度条冲散，
所以统一通过这里加锁输出：日志行打在进度条上方，进度条始终留在最后一行。
"""

import sys
import threading

BAR_WIDTH = 28


class Progress:
    """线程安全的进度显示。

    非终端环境（重定向到文件、CI）下不画进度条，只保留日志行，
    避免输出里塞满 \\r 控制字符。
    """

    def __init__(self, total, stream=None, showBar=None):
        self.total = total
        self.completed = 0
        self.succeeded = 0
        self.skipped = 0
        self.failed = 0
        self.stream = stream or sys.stderr
        self.lock = threading.Lock()
        self.barVisible = False
        if showBar is None:
            showBar = bool(getattr(self.stream, "isatty", lambda: False)())
        # 只有一个任务时画进度条没什么意义
        self.showBar = showBar and total > 1

    def formatBar(self):
        ratio = self.completed / self.total if self.total else 1.0
        filled = int(BAR_WIDTH * ratio)
        bar = "=" * filled + "-" * (BAR_WIDTH - filled)
        parts = [f"[{bar}] {self.completed}/{self.total} ({ratio:.0%})",
                 f"成功 {self.succeeded}"]
        if self.skipped:
            parts.append(f"跳过 {self.skipped}")
        if self.failed:
            parts.append(f"失败 {self.failed}")
        return "  ".join(parts)

    def clearBar(self):
        """擦掉当前进度条，供日志行占用这一行。"""
        if self.barVisible:
            self.stream.write("\r\033[K")
            self.barVisible = False

    def drawBar(self):
        if self.showBar:
            self.stream.write("\r\033[K" + self.formatBar())
            self.stream.flush()
            self.barVisible = True

    def log(self, message):
        """输出一行日志，不破坏进度条。"""
        with self.lock:
            self.clearBar()
            print(message, flush=True)
            self.drawBar()

    def advance(self, status):
        """完成一个任务。status 取 ok / skip / fail。"""
        with self.lock:
            self.completed += 1
            if status == "ok":
                self.succeeded += 1
            elif status == "skip":
                self.skipped += 1
            else:
                self.failed += 1
            self.drawBar()

    def close(self):
        """收尾：把进度条固定成最后一行输出。"""
        with self.lock:
            if self.barVisible:
                self.stream.write("\r\033[K" + self.formatBar() + "\n")
                self.stream.flush()
                self.barVisible = False


class PlainReporter:
    """不带进度条的输出，用于单个链接的场景。"""

    def log(self, message):
        print(message, flush=True)

    def advance(self, status):
        pass

    def close(self):
        pass
