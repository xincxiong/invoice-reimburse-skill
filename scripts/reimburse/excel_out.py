"""Excel 输出与复核列合并。

重跑不丢人工成果:已有表中的"复核状态/备注"按 发票号码 回填到新结果。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .fields import FIELDS_HEADER, FIELDS_KEY


def merge_and_write(records: list[dict], out_path: str) -> pd.DataFrame:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records, columns=FIELDS_KEY)

    if out.exists():
        try:
            old = pd.read_excel(out)
            keep_cols = [c for c in ("invoice_no", "review", "remark") if c in old.columns]
            old = old[keep_cols].rename(
                columns={"review": "_review_old", "remark": "_remark_old"}
            )
            old = old[old["invoice_no"].astype(str).str.strip() != ""]
            old = old.drop_duplicates(subset="invoice_no", keep="last")
            df = df.merge(old, on="invoice_no", how="left")
            df["review"] = df["review"].fillna("").astype(str).str.strip()
            df.loc[df["review"] == "", "review"] = df["_review_old"].fillna("")
            df["remark"] = df["remark"].fillna("")
            df.loc[df["remark"] == "", "remark"] = df["_remark_old"].fillna("")
            df = df.drop(columns=[c for c in ("_review_old", "_remark_old") if c in df.columns])
        except Exception:
            pass

    df = df[FIELDS_KEY]
    df.to_excel(out, index=False, header=FIELDS_HEADER)

    # 列宽与"复核状态"下拉
    try:
        from openpyxl import load_workbook
        from openpyxl.worksheet.datavalidation import DataValidation

        wb = load_workbook(out)
        ws = wb.active
        widths = {"A": 16, "B": 13, "C": 13, "D": 12, "E": 12, "F": 24, "G": 24,
                  "H": 13, "I": 10, "J": 13, "K": 30, "L": 14, "M": 10, "N": 40}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        review_col = FIELDS_KEY.index("review") + 1
        header = ws.cell(row=1, column=review_col).coordinate.replace("1", "")
        dv = DataValidation(type="list", formula1='"通过,待核,作废"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{header}2:{header}{len(df) + 1}")
        wb.save(out)
    except Exception:
        pass
    return df
