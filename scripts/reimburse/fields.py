"""统一发票字段 schema:所有识别路径(QR/PDF/OCR)输出到同一张表。"""

FIELD_DEFS = [
    ("invoice_type", "发票类型"),
    ("invoice_code", "发票代码"),
    ("invoice_no", "发票号码"),
    ("date", "开票日期"),
    ("check_code", "校验码"),
    ("seller", "销方名称"),
    ("buyer", "购方名称"),
    ("amount_excl_tax", "金额(不含税)"),
    ("tax", "税额"),
    ("amount_total", "价税合计"),
    ("source_file", "来源文件"),
    ("method", "识别方式"),
    ("review", "复核状态"),
    ("remark", "备注/原始内容"),
]

FIELDS_KEY = [k for k, _ in FIELD_DEFS]
FIELDS_HEADER = [h for _, h in FIELD_DEFS]


def empty_record() -> dict:
    return {k: "" for k in FIELDS_KEY}
