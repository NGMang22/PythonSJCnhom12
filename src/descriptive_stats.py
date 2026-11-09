"""descriptive_stats.py - Thống kê mô tả bộ dữ liệu giá vàng SJC vs vàng thế giới quy đổi.

Đầu vào : data/processed/gold_final_merged.csv (do feature_engineering.py xuất ra)
Đầu ra  : các bảng thống kê in ra màn hình và lưu vào data/processed/stats/*.csv
"""
import os
import pandas as pd

INPUT_PATH = "data/processed/gold_final_merged.csv"
OUTPUT_DIR = "data/processed/stats"

# Các cột số chính cần thống kê
KEY_COLS = [
    "sjc_mua", "sjc_ban", "xauusd", "usd_vnd", "gia_quy_doi",
    "chenh_lech", "chenh_lech_pct", "bien_do_mua_ban", "bien_do_pct",
    "thay_doi_sjc", "thay_doi_sjc_pct",
]
# Các cột dùng khi thống kê theo năm / quý
GROUP_COLS = ["chenh_lech", "chenh_lech_pct", "bien_do_mua_ban", "bien_do_pct"]

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def load_data(path: str = INPUT_PATH) -> pd.DataFrame:
    """Đọc file đã ghép và bổ sung cột % thay đổi giá bán SJC theo đề cương."""
    df = pd.read_csv(path, parse_dates=["ngay"]).sort_values("ngay").reset_index(drop=True)

    # Dòng đầu chưa có ngày trước đó -> phải là NaN, không phải 0
    df["thay_doi_sjc"] = df["sjc_ban"].diff()
    df["thay_doi_sjc_pct"] = df["sjc_ban"].pct_change() * 100

    # Phòng trường hợp file thiếu cột nam/quy
    if "nam" not in df.columns:
        df["nam"] = df["ngay"].dt.year
    if "quy" not in df.columns:
        df["quy"] = df["ngay"].dt.to_period("Q").astype(str)
    return df


def describe_overall(df: pd.DataFrame) -> pd.DataFrame:
    """describe() toàn kỳ + độ lệch (skew), độ nhọn (kurtosis), hệ số biến thiên (CV %)."""
    cols = [c for c in KEY_COLS if c in df.columns]
    stats = df[cols].describe().T
    stats["skew"] = df[cols].skew()
    stats["kurtosis"] = df[cols].kurt()
    stats["cv_pct"] = stats["std"] / stats["mean"].abs() * 100
    return stats


def describe_by_group(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Thống kê theo nhóm (nam hoặc quy) bằng groupby + agg, làm phẳng tên cột."""
    cols = [c for c in GROUP_COLS if c in df.columns]
    agg = df.groupby(by)[cols].agg(["count", "mean", "std", "min", "median", "max"])
    agg.columns = [f"{c}_{s}" for c, s in agg.columns]
    return agg


def extreme_days(df: pd.DataFrame, col: str = "chenh_lech_pct", n: int = 5):
    """Top n ngày chênh lệch cao nhất và thấp nhất (phục vụ Câu hỏi 4)."""
    show = ["ngay", "sjc_ban", "gia_quy_doi", "chenh_lech", "chenh_lech_pct"]
    show = [c for c in show if c in df.columns]
    return df.nlargest(n, col)[show], df.nsmallest(n, col)[show]


def quality_check(df: pd.DataFrame) -> pd.DataFrame:
    """Kiểm tra nhanh: số bản ghi, thiếu dữ liệu, trùng ngày, khoảng thời gian."""
    info = {
        "so_ban_ghi": len(df),
"tu_ngay": df["ngay"].min().strftime("%Y-%m-%d"),
        "den_ngay": df["ngay"].max().strftime("%Y-%m-%d"),
        "so_o_thieu": int(df[[c for c in KEY_COLS if c in df.columns]].isna().sum().sum()),
        "so_ngay_trung": int(df["ngay"].duplicated().sum()),
    }
    return pd.Series(info, name="gia_tri").to_frame()


def save(df: pd.DataFrame, name: str, index: bool = True) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, name), index=index, encoding="utf-8-sig")


def run(path: str = INPUT_PATH) -> None:
    df = load_data(path)

    print("\n=== 1. KIỂM TRA CHẤT LƯỢNG ===")
    qc = quality_check(df)
    print(qc)

    print("\n=== 2. THỐNG KÊ MÔ TẢ TOÀN KỲ (describe) ===")
    overall = describe_overall(df)
    print(overall)

    print("\n=== 3. THỐNG KÊ THEO NĂM ===")
    by_year = describe_by_group(df, "nam")
    print(by_year[[c for c in by_year.columns if c.endswith(("_mean", "_min", "_max"))]])

    print("\n=== 4. THỐNG KÊ THEO QUÝ ===")
    by_quarter = describe_by_group(df, "quy")
    print(by_quarter[["chenh_lech_pct_mean", "chenh_lech_pct_std", "bien_do_mua_ban_mean"]])

    print("\n=== 5. NGÀY CHÊNH LỆCH TƯƠNG ĐỐI CAO NHẤT / THẤP NHẤT ===")
    top, bottom = extreme_days(df)
    print("Cao nhất:\n", top.to_string(index=False))
    print("\nThấp nhất:\n", bottom.to_string(index=False))

    # Lưu kết quả
    save(qc, "00_kiem_tra_chat_luong.csv")
    save(overall, "01_describe_toan_ky.csv")
    save(by_year, "02_thong_ke_theo_nam.csv")
    save(by_quarter, "03_thong_ke_theo_quy.csv")
    save(top, "04_top_chenh_lech_cao.csv", index=False)
    save(bottom, "05_top_chenh_lech_thap.csv", index=False)
    print(f"\n✅ Đã lưu các bảng thống kê vào: {OUTPUT_DIR}/")


if __name__ == "__main__":
    run()
