"""识别主管线:文件分类 → 识别 → 汇总。

优先级:PDF 文本 > 二维码 > OCR 兜底 > 待人工。
Mac 拍照常为 HEIC,用系统自带 sips 自动转 JPEG 后再识别。
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from .fields import empty_record
from .ocr_extract import OcrUnavailable, ocr_image, parse_transport
from .pdf_extract import extract_pdf
from .qr_extract import decode_qr_texts, parse_vat_qr

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic"}


def convert_heic(path: Path) -> Path | None:
    """HEIC → JPEG(macOS sips)。返回转换后路径,失败返回 None。"""
    tmp = Path(tempfile.mkdtemp()) / (path.stem + ".jpg")
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(path), "--out", str(tmp)],
            check=True, capture_output=True, timeout=30,
        )
        return tmp if tmp.exists() else None
    except Exception:
        return None


def process_file(path: Path) -> dict:
    rec = empty_record()
    rec["source_file"] = str(path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        result = extract_pdf(str(path))
        if result:
            rec.update(result)
            rec["method"] = "PDF文本解析"
            return rec
        rec["method"] = "待人工(扫描版PDF)"
        return rec

    if ext in IMAGE_EXTS:
        actual = path
        converted = None
        if ext == ".heic":
            converted = convert_heic(path)
            if converted is None:
                rec["method"] = "待人工(HEIC转换失败)"
                return rec
            actual = converted
        # 1) 二维码优先
        for text in decode_qr_texts(str(actual)):
            parsed = parse_vat_qr(text)
            if parsed:
                rec.update(parsed)
                rec["method"] = "二维码"
                rec["remark"] = text[:120]
                return rec
            # 二维码存在但格式未知,记录原始内容继续走 OCR
            if not rec["remark"]:
                rec["remark"] = f"未识别二维码: {text[:80]}"
        # 2) OCR 兜底
        try:
            text = ocr_image(str(actual))
            rec.update(parse_transport(text))
            rec["method"] = "OCR"
            if text.strip():
                rec["remark"] = (rec.get("remark", "") + " | " + text[:150]).strip(" |")
        except OcrUnavailable:
            rec["method"] = "待人工(OCR未安装)"
        return rec

    rec["method"] = f"待人工(不支持的格式 {ext})"
    return rec


def scan_dir(input_dir: str) -> list[dict]:
    records = []
    for p in sorted(Path(input_dir).iterdir()):
        if p.is_file() and not p.name.startswith("."):
            records.append(process_file(p))
    return records
