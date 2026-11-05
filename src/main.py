from data_loader import clean_sjc 
# Sau này sẽ import thêm clean_usdvnd, clean_xauusd từ data_loader 
# và import merge_data từ feature_engineering 

def run_pipeline(): 
    print("--- BẮT ĐẦU QUY TRÌNH XỬ LÝ DỮ LIỆU GIÁ VÀNG SJC ---") 
    
    # 1. Đọc và làm sạch SJC 
    df_sjc = clean_sjc('data/raw/sjc_raw.csv') 
    print(f"Đã nạp dữ liệu SJC: {len(df_sjc)} bản ghi.") 
    
    # 2. Sau này sẽ gọi tiếp các hàm của TV2, TV3 và TV4 tại đây... 

if __name__ == '__main__': 
    run_pipeline()