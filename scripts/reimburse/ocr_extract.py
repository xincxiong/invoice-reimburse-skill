"""OCR 兜底(PaddleOCR,可选依赖)。

处理无二维码票种:火车票、机票行程单、出租车票、定额票。
paddleocr 未安装时抛出 OcrUnavailable,由管线降级为"待人工"。

安装(可选,体积较大):
  pip install paddlepaddle paddleocr
"""

from __future__ import annotations

import re

RE_DATE_CN = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
RE_AMOUNT = re.compile(r"[¥￥]\s*([\d,]+\.\d{2})")
RE_TRAIN_NO = re.compile(r"\b[A-Z]\d{1,5}\b")
RE_FLIGHT = re.compile(r"\b[A-Z]{2}\d{3,4}\b")


class OcrUnavailable(RuntimeError):
    pass


def ocr_image(image_path: str) -> str:
    """返回整图 OCR 拼接文本。"""
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        raise OcrUnavailable("paddleocr 未安装") from e
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    result = ocr.ocr(image_path, cls=True)
    lines = []
    for page in result or []:
        for item in page or []:
            if item and len(item) >= 2 and isinstance(item[1], tuple):
                lines.append(item[1][0])
    return "\n".join(lines)


def parse_transport(text: str) -> dict:
    """从 OCR 文本抽取交通票据字段。抽不出的字段留空,交人工复核。"""
    rec: dict = {"invoice_type": "交通/其他票据(OCR)"}
    m = RE_DATE_CN.search(text)
    if m:
        rec["date"] = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    amounts = [a.replace(",", "") for a in RE_AMOUNT.findall(text)]
    if amounts:
        rec["amount_total"] = max(amounts, key=float)
    m = RE_TRAIN_NO.search(text)
    if m:
        rec["remark"] = f"车次/班次候选: {m.group(0)}"
    return rec
