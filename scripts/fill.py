"""Phase 2:Playwright 自动填报。

运行方式:
  python fill.py

首次运行:
  1. 弹出 Chrome(使用系统已装 Chrome,登录态保存在 ./chrome-profile)
  2. 打开报销网站,人工登录(统一认证/短信都行)
  3. 回到终端按回车,机器开始逐张填报
之后运行:登录态仍在,直接进入填报。

安全边界:机器只"填入 + 暂存",不点提交;提交按钮必须人工点。
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import yaml
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent

FIELDS_HEADER_TO_KEY = {
    "发票类型": "invoice_type", "发票代码": "invoice_code", "发票号码": "invoice_no",
    "开票日期": "date", "校验码": "check_code", "销方名称": "seller",
    "购方名称": "buyer", "金额(不含税)": "amount_excl_tax", "税额": "tax",
    "价税合计": "amount_total", "复核状态": "review",
}


def load_rows(xlsx: str, only_pass: bool) -> list[dict]:
    df = pd.read_excel(xlsx)
    df = df.rename(columns=FIELDS_HEADER_TO_KEY)
    if only_pass and "review" in df.columns:
        df = df[df["review"].astype(str).str.strip() == "通过"]
    return df.to_dict("records")


def fill_page(page, cfg: dict, row: dict) -> None:
    page.goto(cfg["invoice_page_url"], wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    for key, selector in cfg["selectors"].items():
        value = str(row.get(key, "")).strip()
        if not value or value == "nan":
            continue
        loc = page.locator(selector).first
        if loc.count() == 0:
            print(f"  [warn] selector 未命中: {key} -> {selector}")
            continue
        loc.fill("")  # 清空再填,避免追加
        loc.fill(value)

    # 日期控件常见 readonly,用键盘输入绕过
    # 如仍失败,把 date 的 selector 改成 click + 选项序列(见 selectors.yaml 注释)

    page.locator(cfg["save_button"]).first.click()
    page.wait_for_timeout(int(cfg.get("wait_seconds_after_save", 2)) * 1000)
    print(f"  已暂存: {row.get('invoice_no', '')} {row.get('seller', '')} {row.get('amount_total', '')} 元")


def main() -> int:
    with open(HERE / "selectors.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    with open(HERE / "config.yaml", encoding="utf-8") as f:
        app_cfg = yaml.safe_load(f)

    xlsx = HERE / app_cfg.get("output_xlsx", "out/reimburse.xlsx")
    if not xlsx.exists():
        print(f"找不到 {xlsx},先运行 extract.py")
        return 1

    rows = load_rows(str(xlsx), bool(cfg.get("only_fill_reviewed_pass", True)))
    if not rows:
        print("没有复核状态为'通过'的发票行。先在 Excel 里复核并把状态改为'通过'。")
        return 0
    print(f"待填报 {len(rows)} 张。注意:机器只填+暂存,提交请人工确认。")

    profile = str(HERE / "chrome-profile")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            profile,
            channel="chrome",   # 用系统已装的 Chrome,无需下载浏览器
            headless=False,
        )
        page = context.pages[0] if context.pages else context.new_page()

        input("在弹出的 Chrome 中登录报销网站,登录完成后回到这里按回车开始填报...")
        for i, row in enumerate(rows, 1):
            print(f"[{i}/{len(rows)}]")
            try:
                fill_page(page, cfg, row)
            except Exception as e:
                print(f"  [error] 该张填报失败,跳过: {e}")
                page.screenshot(path=str(HERE / "out" / f"error_{i}.png"))
        print("全部完成。请在网站上人工检查并逐张提交。")
        context.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
