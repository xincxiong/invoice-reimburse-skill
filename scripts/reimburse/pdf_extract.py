"""电子发票 PDF 文本解析(pdfplumber)。

电子普票/数电票 PDF 均为文本型(非扫描),直接抽文本做正则,零误差。
"""

from __future__ import annotations

import re

RE_INVOICE_NO = re.compile(r"发票号码[:：]?\s*(\d{8,20})")
RE_INVOICE_CODE = re.compile(r"发票代码[:：]?\s*(\d{10,12})")
RE_DATE = re.compile(r"开票日期[:：]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
RE_TOTAL = re.compile(r"价税合计[（(]小写[）)]\s*[¥￥]?\s*([\d,]+\.\d{2})")
RE_TOTAL_UPPER = re.compile(r"价税合计[（(]大写[）)]")
RE_SUM_ROW = re.compile(r"合\s*计\s*[¥￥]\s*([\d,]+\.\d{2})\s*[¥￥]?\s*([\d,]+\.\d{2})")
RE_CHECK_CODE = re.compile(r"校验码[:：]?\s*([\d ]{6,20})")
RE_SELLER = re.compile(r"名\s*称\s*[:：]?\s*([^\s¥￥合计销退税率%]+?)(?:\s{2,}|$)")
RE_BUYER = RE_SELLER


def extract_pdf(pdf_path: str) -> dict | None:
    """解析电子发票 PDF。返回字段 dict;非文本型/非发票返回 None。"""
    try:
        import pdfplumber
    except ImportError:
        return None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception:
        return None
    if not text or ("发票" not in text and "开票日期" not in text):
        return None

    rec: dict = {"invoice_type": "电子发票(PDF)"}
    m = RE_INVOICE_NO.search(text)
    if m:
        rec["invoice_no"] = m.group(1)
    m = RE_INVOICE_CODE.search(text)
    if m:
        rec["invoice_code"] = m.group(1)
    m = RE_DATE.search(text)
    if m:
        rec["date"] = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = RE_CHECK_CODE.search(text)
    if m:
        rec["check_code"] = m.group(1).replace(" ", "")
    m = RE_TOTAL.search(text)
    if m:
        rec["amount_total"] = m.group(1).replace(",", "")
    m = RE_SUM_ROW.search(text)
    if m:
        rec["amount_excl_tax"] = m.group(1).replace(",", "")
        rec["tax"] = m.group(2).replace(",", "")
    if not rec.get("amount_total") and rec.get("amount_excl_tax") and rec.get("tax"):
        total = float(rec["amount_excl_tax"]) + float(rec["tax"])
        rec["amount_total"] = f"{total:.2f}"
    # 购销方:不同排版差异大,仅当文本中标签明确时提取
    m = _labeled_name(text, "销")
    if m:
        rec["seller"] = m
    m = _labeled_name(text, "购")
    if m:
        rec["buyer"] = m
    if not rec.get("invoice_no"):
        return None
    return rec


def _labeled_name(text: str, side: str) -> str | None:
    # 兼容"销售方名称/销方名称/购买方名称/购方名称/名称"等排版
    block = re.search(side + r"(?:售|买)?\s*方?\s*名\s*称\s*[:：]?\s*(\S{2,40})", text)
    if block:
        name = block.group(1)
        return None if any(k in name for k in ("¥", "￥", "合计", "税率")) else name
    return None
