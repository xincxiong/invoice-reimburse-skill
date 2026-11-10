"""文件夹监控:发票落入 inbox 后自动重新扫描(幂等,重跑不丢复核状态)。

用法: python watch.py
停止: Ctrl+C
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print("缺少 watchdog,请先: pip install watchdog")
    sys.exit(1)


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        self.last_run = 0.0

    def on_any_event(self, event):
        if event.is_directory:
            return
        now = time.time()
        # 去抖:5 秒内的事件合并为一次重扫
        if now - self.last_run < 5:
            return
        self.last_run = now
        time.sleep(2)  # 等文件写完
        print(f"[watch] 检测到新文件,重新扫描 {self.input_dir}")
        subprocess.run([sys.executable, str(HERE / "extract.py")], cwd=HERE)


def main() -> int:
    import yaml

    with open(HERE / "config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    input_dir = str((HERE / cfg.get("input_dir", "inbox")).resolve())
    Path(input_dir).mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(NewFileHandler(input_dir), input_dir, recursive=False)
    observer.start()
    print(f"[watch] 监控 {input_dir} ,把发票丢进来即可,Ctrl+C 退出")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
