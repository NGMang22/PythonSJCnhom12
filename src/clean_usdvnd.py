"""clean_usdvnd.py - Đọc và làm sạch dữ liệu tỷ giá USD/VND (theo ngày). 
Nhiệm vụ Thành viên 2: 
- Nhận đường dẫn tệp thô (usdvnd_raw.csv). 
- Xóa ký tự BOM ẩn, chuẩn hóa định dạng ngày và số. 
- Tạo chuỗi ngày liên tục và ffill cho các ngày nghỉ/cuối tuần. 
- Trả về DataFrame gồm đúng 2 cột chuẩn: ['ngay', 'usd_vnd']. 
""" 
import sys 
import pandas as pd 

MIN_RECORDS = 300 # Ngưỡng tối thiểu của đề tài 

def clean_usdvnd(filepath: str) -> pd.DataFrame: 
    """Đọc và làm sạch dữ liệu tỷ giá USD/VND theo đúng tiêu chuẩn đề tài.""" 
    # 1. Đọc file thô và loại bỏ dấu phẩy ngăn cách hàng nghìn 
    df = pd.read_csv(filepath, thousands=",") 
    
    # 2. Xóa sạch ký tự BOM ẩn (\ufeff) và khoảng trắng ở tiêu đề cột 
    df.columns = [col.strip().replace("\ufeff", "").replace('"', '') for col in df.columns] 
    
    # 3. Chuẩn hóa tên cột sang chuẩn đề cương: 'ngay' và 'usd_vnd' 
    rename_mapping = {} 
    for col in df.columns: 
        c_low = col.lower() 
        if c_low in ["ngày", "date", "ngay"]: 
            rename_mapping[col] = "ngay" 
        elif c_low in ["lần cuối", "close", "đóng cửa", "price", "usd_vnd"]: 
            rename_mapping[col] = "usd_vnd" 
            
    df = df.rename(columns=rename_mapping) 
    
    if "ngay" not in df.columns or "usd_vnd" not in df.columns: 
        raise ValueError(f"Thiếu cột 'ngay' hoặc 'usd_vnd'. Cột hiện có: {list(df.columns)}") 
        
    # 4. Chuẩn hóa định dạng ngày (ngày đứng trước: DD/MM/YYYY) và ép kiểu số thực 
    df["ngay"] = pd.to_datetime(df["ngay"], dayfirst=True, format="mixed") 
    df["usd_vnd"] = pd.to_numeric(df["usd_vnd"], errors="coerce") 
    
    # 5. Sắp xếp, xóa trùng lặp theo ngày và đặt làm index 
    df = df.dropna(subset=["ngay", "usd_vnd"]) 
    df = df.sort_values("ngay").drop_duplicates(subset=["ngay"]).set_index("ngay") 
    
    # 6. Tạo dải ngày liên tục và forward-fill tỷ giá cho ngày nghỉ/cuối tuần 
    full_range = pd.date_range(df.index.min(), df.index.max(), freq="D") 
    df = df.reindex(full_range) 
    df.index.name = "ngay" 
    df["usd_vnd"] = df["usd_vnd"].ffill() 
    
    # 7. Trích xuất đúng 2 cột chuẩn theo đề cương 
    df_clean = df.reset_index()[["ngay", "usd_vnd"]] 
    df_clean = df_clean.dropna(subset=["ngay", "usd_vnd"]) 
    
    # Kiểm tra điều kiện tiên quyết >= 300 dòng 
    assert len(df_clean) >= MIN_RECORDS, f"Dữ liệu chỉ có {len(df_clean)} dòng, chưa đạt tối thiểu {MIN_RECORDS}!" 
    
    return df_clean 

# --- KHỐI KIỂM THỬ ĐỘC LẬP CHO THÀNH VIÊN 2 --- 
if __name__ == "__main__": 
    src_file = sys.argv[9] if len(sys.argv) > 1 else "data/raw/usdvnd_raw.csv" 
    print("⏳ Đang làm sạch dữ liệu USD/VND...") 
    df_usd = clean_usdvnd(src_file) 
    print("\n====== BÁO CÁO KIỂM THỬ USD/VND (THÀNH VIÊN 2) ======") 
    print(f"- Số bản ghi hợp lệ: {len(df_usd):,} dòng") 
    print(f"- Đạt yêu cầu >= {MIN_RECORDS} dòng: {'ĐẠT ✅' if len(df_usd) >= MIN_RECORDS else 'KHÔNG ĐẠT ❌'}") 
    print(f"- Khoảng thời gian: từ {df_usd['ngay'].min().strftime('%Y-%m-%d')} đến {df_usd['ngay'].max().strftime('%Y-%m-%d')}") 
    print(f"- Các cột đầu ra: {list(df_usd.columns)}") 
    print("\n5 dòng đầu:") 
    print(df_usd.head()) 
    print("====================================================")