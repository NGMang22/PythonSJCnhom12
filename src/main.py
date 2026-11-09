import os
import sys

# Đảm bảo Python nhận diện được cả thư mục gốc và thư mục src/ khi import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# 1. IMPORT CÁC MODULE LÀM SẠCH VÀ GHÉP NỐI
try:
    from data_loader import clean_sjc
    from clean_xauusd import clean_xauusd
    from clean_usdvnd import clean_usdvnd
    from feature_engineering import build_final_dataset
except ModuleNotFoundError:
    from src.data_loader import clean_sjc
    from src.clean_xauusd import clean_xauusd
    from src.clean_usdvnd import clean_usdvnd
    from src.feature_engineering import build_final_dataset

# 2. IMPORT HÀM RUN TỪ DESCRIPTIVE_STATS_2
try:
    from descriptive_stats import run as run_stats
except ModuleNotFoundError:
    try:
        from src.descriptive_stats import run as run_stats
    except ModuleNotFoundError:
        # Dự phòng trường hợp bạn đã đổi tên file thành descriptive_stats.py
        try:
            from descriptive_stats import run as run_stats
        except ModuleNotFoundError:
            from src.descriptive_stats import run as run_stats

def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU CHẠY TOÀN BỘ PIPELINE: DỰ ÁN PHÂN TÍCH GIÁ VÀNG SJC")
    print("=" * 60)

    # ĐƯỜNG DẪN DỮ LIỆU
    path_sjc = "data/raw/sjc_raw.csv"
    path_xau = "data/raw/xauusd_raw.csv"
    path_usd = "data/raw/usdvnd_raw.csv"
    output_merged = "data/processed/gold_final_merged.csv"

    # -------------------------------------------------------------
    # BƯỚC 1: LÀM SẠCH DỮ LIỆU ĐẦU VÀO (TV1, TV2, TV3)
    # -------------------------------------------------------------
    print("\n⏳ [1/3] Đang làm sạch dữ liệu từ 3 file thô...")
    try:
        df_sjc = clean_sjc(path_sjc)
        df_xau = clean_xauusd(path_xau)
        df_usd = clean_usdvnd(path_usd)
        print(f" - SJC (TV1) : {len(df_sjc):,} dòng hợp lệ")
        print(f" - XAU/USD (TV3) : {len(df_xau):,} dòng hợp lệ")
        print(f" - USD/VND (TV2) : {len(df_usd):,} dòng hợp lệ")
    except Exception as e:
        print(f"❌ Lỗi tại Bước 1 (Làm sạch dữ liệu): {e}")
        return

    # -------------------------------------------------------------
    # BƯỚC 2: GHÉP DỮ LIỆU & TẠO BIẾN PHÁI SINH (TV4)
    # -------------------------------------------------------------
    print("\n⏳ [2/3] Đang ghép 3 bảng và tính toán các thuộc tính phái sinh...")
    try:
        df_merged = build_final_dataset(df_sjc, df_xau, df_usd, output_path=output_merged)
        print(f" ✅ Đã lưu file tổng hợp: {output_merged} ({len(df_merged):,} dòng)")
    except Exception as e:
        print(f"❌ Lỗi tại Bước 2 (Ghép bảng TV4): {e}")
        return

    # -------------------------------------------------------------
    # BƯỚC 3: THỐNG KÊ MÔ TẢ & XUẤT 6 BẢNG SỐ LIỆU (TV5)
    # -------------------------------------------------------------
    print("\n⏳ [3/3] Đang chạy thống kê mô tả từ descriptive_stats_2.py...")
    try:
        # Gọi trực tiếp hàm run() của descriptive_stats_2
        run_stats(path=output_merged)
    except Exception as e:
        print(f"❌ Lỗi tại Bước 3 (Thống kê TV5): {e}")
        return

    print("\n" + "=" * 60)
    print("🎉 CHÚC MỪNG: PIPELINE ĐÃ HOÀN TẤT THÀNH CÔNG 100%!")
    print("👉 File dữ liệu sạch: data/processed/gold_final_merged.csv")
    print("👉 6 bảng thống kê đã có trong: data/processed/stats/")
    print("=" * 60)

if __name__ == "__main__":
    main()