import pandas as pd
import numpy as np

TROY_OUNCE_TO_TAEL = 1.205653
MIN_RECORDS = 300


def merge_gold_data(df_sjc: pd.DataFrame, df_usd: pd.DataFrame, df_xau: pd.DataFrame) -> pd.DataFrame:
    """
    Ghép 3 DataFrame (SJC, USD/VND, XAU/USD) theo cột 'ngay'.
    Sử dụng Inner Join hoặc Outer Join kết hợp Forward Fill để đảm bảo tính liên tục dữ liệu.
    """
    # Đảm bảo cột 'ngay' ở dạng datetime
    for df in [df_sjc, df_usd, df_xau]:
        df['ngay'] = pd.to_datetime(df['ngay'])

    # Ghép bảng lần lượt theo cột 'ngay'
    merged = pd.merge(df_sjc, df_usd, on='ngay', how='inner')
    merged = pd.merge(merged, df_xau, on='ngay', how='inner')

    # Sắp xếp theo ngày tăng dần
    merged = merged.sort_values('ngay').reset_index(drop=True)
    return merged


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán các cột chỉ số phái sinh theo chuẩn tài chính:
    - gia_quy_doi: Giá vàng thế giới quy đổi ra Triệu VNĐ/lượng
    - chech_lech: Chênh lệch tuyệt đối SJC (giá bán) vs Thế giới quy đổi
    - chech_lech_ptc: % Chênh lệch SJC vs Thế giới quy đổi
    - bien_do_mua_ban: Khoảng cách giá Bán - Giá Mua SJC
    - bien_do_ptc: % Biên độ Mua/Bán trên giá Mua
    - thay_doi_sjc: Biến động giá bán SJC so với phiên trước
    """
    res = df.copy()

    # Giả định cột SJC mua/bán chuẩn tên là 'sjc_buy' và 'sjc_sell'
    # Nếu dữ liệu SJC thô chỉ có 1 cột giá đóng cửa 'sjc', dùng 'sjc' cho cả buy và sell.
    sjc_sell_col = 'sjc_sell' if 'sjc_sell' in res.columns else 'sjc'
    sjc_buy_col = 'sjc_buy' if 'sjc_buy' in res.columns else sjc_sell_col

    # Giá thế giới quy đổi (Triệu VNĐ / lượng)
    # xauusd (USD/oz) * 1.205653 (oz/lượng) * usd_vnd (VNĐ/USD) / 1,000,000
    res['gia_quy_doi'] = (res['xauusd'] * TROY_OUNCE_TO_TAEL * res['usd_vnd']) / 1_000_000

    # Chênh lệch tuyệt đối (Triệu VNĐ/lượng)
    res['chech_lech'] = res[sjc_sell_col] - res['gia_quy_doi']

    # Chênh lệch phần trăm (%)
    res['chech_lech_ptc'] = (res['chech_lech'] / res['gia_quy_doi']) * 100

    # Biên độ mua bán (Triệu VNĐ/lượng)
    res['bien_do_mua_ban'] = res[sjc_sell_col] - res[sjc_buy_col]

    # Biên độ phần trăm (%)
    res['bien_do_ptc'] = np.where(
        res[sjc_buy_col] > 0,
        (res['bien_do_mua_ban'] / res[sjc_buy_col]) * 100,
        0
    )

    # Biến động giá SJC so với phiên trước (Triệu VNĐ/lượng)
    res['thay_doi_sjc'] = res[sjc_sell_col].diff().fillna(0)

    float_cols = ['gia_quy_doi', 'chech_lech', 'chech_lech_ptc', 'bien_do_mua_ban', 'bien_do_ptc', 'thay_doi_sjc']
    res[float_cols] = res[float_cols].round(2)

    return res


def build_final_dataset(df_sjc: pd.DataFrame, df_usd: pd.DataFrame, df_xau: pd.DataFrame, output_path: str = "gold_final_merged.csv") -> pd.DataFrame:
    """Hàm tổng hợp toàn bộ quy trình merge, tính toán và xuất file CSV."""
    df_merged = merge_gold_data(df_sjc, df_usd, df_xau)
    df_final = compute_features(df_merged)

    # Kiểm định yêu cầu số lượng dòng theo đề cương
    if len(df_final) < MIN_RECORDS:
        print(f"⚠️ Cảnh báo: File tổng hợp chỉ đạt {len(df_final)} dòng (Yêu cầu >= {MIN_RECORDS}).")

    # Xuất ra file CSV sạch
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Đã xuất thành công file sạch: {output_path} ({len(df_final)} dòng)")
    return df_final

if __name__ == "__main__":
    from clean_usdvnd import clean_usdvnd
    from clean_xauusd import clean_xauusd

    print("⏳ Đang tải và làm sạch dữ liệu từ các module...")
    
    # Gọi làm sạch dữ liệu
    try:
        df_usd = clean_usdvnd("data/raw/usdvnd_raw.csv")
        df_xau = clean_xauusd("data/raw/xauusd_raw.csv")
    except Exception as e:
        print("⚠️ Không tìm thấy file dữ liệu thô thực tế, đang khởi tạo dữ liệu giả lập để kiểm thử logic...")
        # Tạo dữ liệu mẫu giả định để chạy test
        dates = pd.date_range("2024-01-01", periods=350, freq="D")
        df_usd = pd.DataFrame({'ngay': dates, 'usd_vnd': 25400.0})
        df_xau = pd.DataFrame({'ngay': dates, 'xauusd': 2350.0})

    # Giả định dữ liệu SJC
    dates = df_usd['ngay']
    df_sjc = pd.DataFrame({
        'ngay': dates,
        'sjc_buy': 82.5,
        'sjc_sell': 84.5
    })

    # Tiến hành merge và tính toán
    print("⏳ Đang tiến hành ghép bảng và tính toán các thuộc tính phái sinh...")
    df_res = build_final_dataset(df_sjc, df_usd, df_xau, "gold_final_merged.csv")

    print("\n====== KẾT QUẢ TÍNH TOÁN ======")
    print(f"- Tổng số dòng: {len(df_res):,} dòng")
    print(f"- Các cột đầu ra ({len(df_res.columns)} cột): {list(df_res.columns)}")
    print("\n5 dòng dữ liệu đầu tiên:")
    print(df_res.head())
