"""命令行入口:扫描 inbox → 识别 → 写 out/reimburse.xlsx。

用法:
  python extract.py                 # 扫描 config.yaml 中的 input_dir
  python extract.py /path/to/dir    # 扫描指定目录
  python extract.py --out 别的.xlsx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from reimburse.excel_out import merge_and_write  # noqa: E402
from reimburse.pipeline import scan_dir  # noqa: E402


def load_config() -> dict:
    cfg_path = HERE / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def main() -> int:
    cfg = load_config()
    default_in = str((HERE / cfg.get("input_dir", "inbox")).resolve())
    default_out = str((HERE / cfg.get("output_xlsx", "out/reimburse.xlsx")).resolve())
    parser = argparse.ArgumentParser(description="发票识别汇总")
    parser.add_argument("input_dir", nargs="?", default=default_in)
    parser.add_argument("--out", default=default_out)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"输入目录不存在: {input_dir}")
        return 1
    files = [p for p in input_dir.iterdir() if p.is_file() and not p.name.startswith(".")]
    print(f"扫描 {input_dir} : {len(files)} 个文件")
    if not files:
        return 0

    records = scan_dir(str(input_dir))
    df = merge_and_write(records, args.out)

    done = len(df[df["method"].str.startswith("待人工") == False])
    todo = len(df) - done
    print(f"完成: {len(df)} 条 | 机器识别 {done} 条 | 待人工 {todo} 条")
    print(f"输出: {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
