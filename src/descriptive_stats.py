
import pandas as pd
from pathlib import Path

# Các biến cần thống kê
NUMERIC_COLUMNS = [
    "sjc_mua",
    "sjc_ban",
    "usd_vnd",
    "xauusd",
    "gia_quy_doi",
    "chenh_lech",
    "chenh_lech_ptc",
    "bien_do_mua_ban",
    "bien_do_ptc",
    "thay_doi_sjc"
]


def descriptive_statistics(df):
    """
    Thống kê mô tả tổng quan dữ liệu.
    """
    cols = [col for col in NUMERIC_COLUMNS if col in df.columns]

    if not cols:
        raise ValueError("Không tìm thấy cột số liệu cần thống kê.")

    return df[cols].describe().T


def monthly_statistics(df):
    """
    Thống kê dữ liệu theo tháng.
    """
    data = df.copy()
    data["ngay"] = pd.to_datetime(data["ngay"])

    data["nam_thang"] = data["ngay"].dt.to_period("M")

    cols = [
        col for col in NUMERIC_COLUMNS
        if col in data.columns
    ]

    return data.groupby("nam_thang")[cols].agg(
        ["mean", "min", "max", "std", "count"]
    )


def yearly_statistics(df):
    """
    Thống kê dữ liệu theo năm.
    """
    data = df.copy()
    data["ngay"] = pd.to_datetime(data["ngay"])
    data["nam"] = data["ngay"].dt.year

    cols = [
        col for col in NUMERIC_COLUMNS
        if col in data.columns
    ]

    return data.groupby("nam")[cols].agg(
        ["mean", "min", "max", "std", "count"]
    )


def export_statistics(df, output_dir="output"):
    """
    Xuất các bảng thống kê ra CSV.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    descriptive_statistics(df).to_csv(
        output / "descriptive_stats.csv",
        encoding="utf-8-sig"
    )

    monthly_statistics(df).to_csv(
        output / "monthly_stats.csv",
        encoding="utf-8-sig"
    )

    yearly_statistics(df).to_csv(
        output / "yearly_stats.csv",
        encoding="utf-8-sig"
    )

    print("Đã xuất thành công 3 bảng thống kê!")
