import pandas as pd 

def clean_sjc(filepath: str) -> pd.DataFrame: 
    """ Đọc và làm sạch dữ liệu giá vàng SJC: 
    - Đổi tên cột Date/Ngày thành 'ngay' 
    - Ép kiểu ngày tháng và sắp xếp theo trình tự thời gian 
    - Loại bỏ các dòng khuyết thiếu (NaN) và trùng lặp 
    """ 
    # 1. Đọc file CSV 
    df = pd.read_csv(filepath) 
    
    # Chuẩn hóa tên cột gốc: xóa khoảng trắng thừa và ký tự đặc biệt 
    df.columns = [col.strip().replace('\ufeff', '') for col in df.columns] 
    
    # 2. Đổi tên cột ngày thành 'ngay' 
    rename_mapping = {} 
    for col in df.columns: 
        if col.lower() in ['date', 'ngày', 'ngay']: 
            rename_mapping[col] = 'ngay' 
        elif 'mua' in col.lower(): 
            rename_mapping[col] = 'sjc_mua' 
        elif 'ban' in col.lower() or 'bán' in col.lower(): 
            rename_mapping[col] = 'sjc_ban' 
    df = df.rename(columns=rename_mapping) 
    
    # 3. Chuẩn hóa cột ngày sang định dạng datetime 
    df['ngay'] = pd.to_datetime(df['ngay'], errors='coerce') 
    
    # 4. Ép kiểu số thực (float) cho 2 cột giá 
    df['sjc_mua'] = pd.to_numeric(df['sjc_mua'], errors='coerce') 
    df['sjc_ban'] = pd.to_numeric(df['sjc_ban'], errors='coerce') 
    
    # 5. Loại bỏ các dòng bị thiếu giá trị (như ngày nghỉ lễ 2020-01-01) 
    df = df.dropna(subset=['ngay', 'sjc_mua', 'sjc_ban']) 
    
    # 6. Loại bỏ bản ghi trùng ngày và sắp xếp tăng dần theo thời gian 
    df = df.drop_duplicates(subset=['ngay']) 
    df = df.sort_values('ngay').reset_index(drop=True) 
    
    return df[['ngay', 'sjc_mua', 'sjc_ban']] 

# --- KIỂM THỬ HÀM --- 
if __name__ == '__main__': 
    # Chạy thử với file của nhóm 
    df_sjc_clean = clean_sjc('data/raw/sjc_raw.csv') 
    
    print("✅ Đã làm sạch dữ liệu SJC thành công!") 
    print(f"- Số bản ghi hợp lệ: {len(df_sjc_clean)} dòng") 
    print(f"- Các cột hiện có: {list(df_sjc_clean.columns)}") 
    print(f"- Khoảng thời gian: Từ {df_sjc_clean['ngay'].min().strftime('%Y-%m-%d')} đến {df_sjc_clean['ngay'].max().strftime('%Y-%m-%d')}") 
    print("\n5 dòng đầu tiên:") 
    print(df_sjc_clean.head())