"""二维码解码与增值税发票二维码解析。

主路径:cv2.QRCodeDetector(纯 pip 依赖,无需系统库)。
兜底:pyzbar(需 brew install zbar,可选)。

增值税发票二维码内容为逗号分隔字段,常见格式:
  01,<类型码>,<发票代码>,<发票号码>,<不含税金额>,<开票日期YYYYMMDD>,<校验码后位>,...
类型码与校验码位数因票种/地区略有差异,故保留原始串进备注,便于人工校准。
"""

from __future__ import annotations

import datetime as _dt

VAT_QR_TYPES = {
    "01": "增值税专用发票",
    "02": "增值税普通发票",
    "03": "增值税普通发票(卷票)",
    "04": "增值税电子普通发票",
    "10": "增值税电子专用发票",
    "11": "数电发票(增值税)",
}


def decode_qr_texts(image_path: str) -> list[str]:
    """解码图片中所有二维码,返回文本列表。"""
    texts: list[str] = []
    try:
        import cv2

        img = cv2.imread(image_path)
        if img is None:
            return texts
        detector = cv2.QRCodeDetector()
        # 返回顺序: retval, 解码文本tuple, 坐标点, 原图
        ok, decoded, _points, _ = detector.detectAndDecodeMulti(img)
        if ok:
            texts = [t for t in decoded if isinstance(t, str) and t]
    except Exception:
        pass
    if not texts:
        try:
            from pyzbar.pyzbar import decode as zbar_decode
            from PIL import Image

            for obj in zbar_decode(Image.open(image_path)):
                texts.append(obj.data.decode("utf-8", "ignore"))
        except Exception:
            pass
    return texts


def parse_vat_qr(text: str) -> dict | None:
    """解析增值税发票二维码字符串。返回字段 dict,无法解析返回 None。"""
    s = text.strip()
    if not s:
        return None
    # 数电发票:20 位纯数字号码
    if s.isdigit() and len(s) == 20:
        return {
            "invoice_type": "数电发票(增值税)",
            "invoice_no": s,
        }
    parts = [p.strip() for p in s.split(",")]
    if len(parts) < 7 or parts[0] not in VAT_QR_TYPES:
        return None
    code, no, amount, date, check = parts[2], parts[3], parts[4], parts[5], parts[6]
    try:
        date_fmt = _dt.datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        date_fmt = date
    return {
        "invoice_type": VAT_QR_TYPES[parts[0]],
        "invoice_code": code,
        "invoice_no": no,
        "date": date_fmt,
        "check_code": check,
        "amount_excl_tax": _normalize_amount(amount),
    }


def _normalize_amount(raw: str) -> str:
    s = raw.replace("¥", "").replace("￥", "").strip()
    if not s:
        return ""
    try:
        return f"{float(s):.2f}"
    except ValueError:
        return s
