import os
from src.data_loader import clean_sjc
from src.clean_xauusd import clean_xauusd
from src.clean_usdvnd import clean_usdvnd
from src.feature_engineering import build_final_dataset
from src.descriptive_stats import export_statistics, descriptive_statistics

def main():
    print("🚀 Bắt đầu chạy toàn bộ quy trình dự án Phân tích giá vàng...")
    
    # 1. Làm sạch dữ liệu
    df_sjc = clean_sjc("data/raw/sjc_raw.csv")
    df_xau = clean_xauusd("data/raw/xauusd_raw.csv")
    df_usd = clean_usdvnd("data/raw/usdvnd_raw.csv")
    
    # 2. Ghép dữ liệu và tạo biến phái sinh
    df_final = build_final_dataset(df_sjc, df_xau, df_usd, "data/processed/gold_final_merged.csv")
    
    # 3. Chạy thống kê mô tả ban đầu
    export_statistics(df_final, output_dir="data/processed/stats")
    
    print("🎉 Hoàn tất toàn bộ pipeline của Mốc 03!")

if __name__ == "__main__":
    main()