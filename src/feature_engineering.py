import os
import numpy as np
import pandas as pd

# Hệ số quy đổi: 1 lượng vàng = 1.205653 troy ounce
TROY_OUNCE_TO_TAEL = 1.205653

# Tiêu chí số lượng bản ghi tối thiểu theo đề cương đề tài
MIN_RECORDS = 300

def merge_gold_data(df_sjc: pd.DataFrame, df_xau: pd.DataFrame, df_usd: pd.DataFrame) -> pd.DataFrame:
    """Ghép 3 bảng dữ liệu sạch theo cột chung 'ngay' (Inner Join)."""
    # Đảm bảo cột 'ngay' ở định dạng datetime chuẩn
    for df in [df_sjc, df_xau, df_usd]:
        df["ngay"] = pd.to_datetime(df["ngay"])
        
    # Ghép bảng SJC với XAU/USD và USD/VND
    merged = pd.merge(df_sjc, df_xau, on="ngay", how="inner")
    merged = pd.merge(merged, df_usd, on="ngay", how="inner")
    
    # Sắp xếp tăng dần theo thời gian
    merged = merged.sort_values("ngay").reset_index(drop=True)
    return merged

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tính toán toàn bộ các chỉ số tài chính phái sinh theo chuẩn đề cương.
    Bao gồm:
    - gia_quy_doi: Giá thế giới quy đổi (đồng/lượng) = xauusd * usd_vnd * 1.205653
    - chenh_lech: Chênh lệch giá bán SJC vs Giá quy đổi (đồng/lượng)
    - chenh_lech_pct: % Chênh lệch trên giá quy đổi
    - bien_do_mua_ban: Giá bán SJC - Giá mua SJC (đồng/lượng)
    - bien_do_pct: % Mức lỗ tức thì trên giá bán SJC
    - thay_doi_sjc: Biến động giá bán SJC so với ngày liền trước
    - nam, quy: Trường thời gian phục vụ groupby()
    """
    res = df.copy()
    
    # Nhận diện linh hoạt tên cột SJC mua/bán (chuẩn theo TV1 là sjc_ban, sjc_mua)
    sjc_ban_col = "sjc_ban" if "sjc_ban" in res.columns else ("sjc_sell" if "sjc_sell" in res.columns else "sjc")
    sjc_mua_col = "sjc_mua" if "sjc_mua" in res.columns else ("sjc_buy" if "sjc_buy" in res.columns else sjc_ban_col)
    
    # 1. Giá vàng thế giới quy đổi ra VNĐ/lượng
    res["gia_quy_doi"] = res["xauusd"] * res["usd_vnd"] * TROY_OUNCE_TO_TAEL
    
    # 2. Mức chênh lệch tuyệt đối (đồng/lượng)
    res["chenh_lech"] = res[sjc_ban_col] - res["gia_quy_doi"]
    
    # 3. Mức chênh lệch tương đối theo %
    res["chenh_lech_pct"] = (res["chenh_lech"] / res["gia_quy_doi"]) * 100
    
    # 4. Biên độ mua - bán SJC trong nước (đồng/lượng)
    res["bien_do_mua_ban"] = res[sjc_ban_col] - res[sjc_mua_col]
    
    # 5. Mức lỗ tức thì theo % giá bán SJC
    res["bien_do_pct"] = np.where(
        res[sjc_ban_col] > 0,
        (res["bien_do_mua_ban"] / res[sjc_ban_col]) * 100,
        0
    )
    
    # 6. Biến động giá bán SJC so với ngày giao dịch liền trước
    res["thay_doi_sjc"] = res[sjc_ban_col].diff().fillna(0)
    
    # 7. Các trường thời gian phục vụ gom nhóm phân tích (groupby)
    res["nam"] = res["ngay"].dt.year
    res["quy"] = res["ngay"].dt.to_period("Q").astype(str)
    
    # Làm tròn 2 chữ số thập phân cho các cột tính toán
    float_cols = ["gia_quy_doi", "chenh_lech", "chenh_lech_pct", "bien_do_mua_ban", "bien_do_pct", "thay_doi_sjc"]
    res[float_cols] = res[float_cols].round(2)
    return res

def build_final_dataset(
    df_sjc: pd.DataFrame,
    df_xau: pd.DataFrame,
    df_usd: pd.DataFrame,
    output_path: str = "data/processed/gold_final_merged.csv"
) -> pd.DataFrame:
    """Tổng hợp toàn bộ quy trình: ghép bảng, tính biến phái sinh, kiểm định và lưu file."""
    # Ghép 3 bảng
    df_merged = merge_gold_data(df_sjc, df_xau, df_usd)
    
    # Tính các cột phái sinh
    df_final = compute_features(df_merged)
    
    # Kiểm định điều kiện tối thiểu theo đề cương
    total_records = len(df_final)
    if total_records < MIN_RECORDS:
        raise ValueError(f"⚠️ Cảnh báo: File tổng hợp chỉ đạt {total_records} dòng (Yêu cầu tối thiểu >= {MIN_RECORDS} dòng)!")
        
    # Tự động tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Xuất ra file CSV sạch chuẩn
    df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Đã xuất thành công: {output_path}")
    print(f"📊 Tổng số bản ghi: {total_records:,} dòng | Tổng số cột: {len(df_final.columns)} cột")
    return df_final

# --- KHỐI CHẠY CHÍNH CHO THÀNH VIÊN 4 ---
if __name__ == "__main__":
    print("⏳ [1/3] Đang import các hàm làm sạch dữ liệu...")
    # Import linh hoạt: hỗ trợ cả khi chạy từ thư mục gốc lẫn bên trong thư mục src/
    try:
        from data_loader import clean_sjc
        from clean_xauusd import clean_xauusd
        from clean_usdvnd import clean_usdvnd
    except ModuleNotFoundError:
        from src.data_loader import clean_sjc
        from src.clean_xauusd import clean_xauusd
        from src.clean_usdvnd import clean_usdvnd
        
    print("⏳ [2/3] Đang đọc và làm sạch dữ liệu từ 3 file thô...")
    sjc = clean_sjc("data/raw/sjc_raw.csv")
    xau = clean_xauusd("data/raw/xauusd_raw.csv")
    usd = clean_usdvnd("data/raw/usdvnd_raw.csv")
    print(f" - SJC sạch: {len(sjc):,} dòng")
    print(f" - XAU/USD sạch: {len(xau):,} dòng")
    print(f" - USD/VND sạch: {len(usd):,} dòng")
    
    print("⏳ [3/3] Đang tiến hành ghép dữ liệu và tính toán biến phái sinh...")
    df_res = build_final_dataset(sjc, xau, usd, "data/processed/gold_final_merged.csv")
    print("\n====== KẾT QUẢ KIỂM THỬ 5 DÒNG ĐẦU TIÊN ======")
    cols_preview = ["ngay", "sjc_ban", "gia_quy_doi", "chenh_lech", "chenh_lech_pct"]
    print(df_res[[c for c in cols_preview if c in df_res.columns]].head())