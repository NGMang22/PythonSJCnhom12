"""clean_xauusd.py - Đọc và làm sạch dữ liệu giá vàng thế giới XAU/USD (theo ngày).
"""
import sys
import warnings
import pandas as pd

MIN_RECORDS = 300  # yêu cầu tối thiểu số bản ghi hợp lệ

# Tên cột trong file gốc (Date, Open, High, Low, Close, Change) -> tên chuẩn
RENAME = {
    "date": "ngay", "ngày": "ngay", "ngay": "ngay", "datetime": "ngay",
    "open": "xau_open", "high": "xau_high", "low": "xau_low",
    "close": "xau_close", "adj close": "xau_close", "price": "xau_close",
    "change": "xau_change_pct", "change %": "xau_change_pct",
    "change, %": "xau_change_pct", "change%": "xau_change_pct",
}
PRICE_COLS = ["xau_open", "xau_high", "xau_low", "xau_close"]
OUT_COLS = ["ngay"] + PRICE_COLS + ["xau_change_pct"]


def _to_number(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
    return pd.to_numeric(s.str.strip(), errors="coerce")


def _to_date(s: pd.Series) -> pd.Series:
    """Hiểu ngày dạng tháng/ngày/năm (1/31/2020), YYYY-MM-DD hoặc kiểu ngày của Excel."""
    s = s.astype(str).str.strip()
    d = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    miss = d.isna()
    if miss.any():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d[miss] = pd.to_datetime(s[miss], errors="coerce")
    return d.dt.normalize()


def clean_xauusd(filepath: str) -> pd.DataFrame:
    """Đọc (.csv hoặc .xlsx) và làm sạch dữ liệu XAU/USD.

    - Đổi tên cột, chuẩn hóa cột ngày về datetime, ép kiểu số cho các cột giá
    - Loại dòng thiếu ngày/giá đóng cửa, giá <= 0, high < low, trùng ngày
    - Sắp xếp tăng dần theo ngày
    Báo cáo số dòng nằm trong df.attrs["report"].
    """
    if filepath.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    report = {"raw_rows": len(df)}

    df.columns = [RENAME.get(str(c).strip().lower(), str(c).strip().lower())
                  for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    if "ngay" not in df.columns or "xau_close" not in df.columns:
        raise ValueError(f"Thiếu cột ngày/giá đóng cửa. Cột hiện có: {list(df.columns)}")

    df["ngay"] = _to_date(df["ngay"])
    for c in PRICE_COLS + ["xau_change_pct"]:
        if c in df.columns:
            df[c] = _to_number(df[c])

    n = len(df)
    df = df.dropna(subset=["ngay", "xau_close"])
    df = df[df["xau_close"] > 0]
    report["dropped_missing_or_bad"] = n - len(df)

    n = len(df)
    if {"xau_high", "xau_low"}.issubset(df.columns):
        df = df[~(df["xau_high"] < df["xau_low"])]
    report["dropped_high_lt_low"] = n - len(df)

    n = len(df)
    df = df.drop_duplicates(subset=["ngay"], keep="last")
    report["dropped_duplicates"] = n - len(df)

    df = df.sort_values("ngay").reset_index(drop=True)
    df = df[[c for c in OUT_COLS if c in df.columns]]
    report["clean_rows"] = len(df)
    if len(df):
        report["date_min"] = df["ngay"].min().strftime("%Y-%m-%d")
        report["date_max"] = df["ngay"].max().strftime("%Y-%m-%d")
    df.attrs["report"] = report
    return df


def summarize(df: pd.DataFrame, min_records: int = MIN_RECORDS) -> str:
    rep = df.attrs.get("report", {"clean_rows": len(df)})
    ok = rep["clean_rows"] >= min_records
    lines = [f"{k}: {v}" for k, v in rep.items()]
    lines.append(f"Đạt yêu cầu >= {min_records} bản ghi hợp lệ: {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    return "\n".join(lines)


# --- KIỂM THỬ ---
if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/raw/xauusd_raw.csv"
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    df_xau = clean_xauusd(src)
    print(summarize(df_xau))
    print("Các cột hiện có:", list(df_xau.columns))
    print("\n5 dòng đầu tiên:")
    print(df_xau.head())
    if dst:
        df_xau.to_csv(dst, index=False)
        print(f"\nĐã lưu: {dst}")
