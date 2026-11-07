"""clean_xauusd.py - Đọc và làm sạch dữ liệu giá vàng thế giới XAU/USD (theo ngày).""" 
import sys 
import warnings 
import pandas as pd 

# Ngưỡng yêu cầu tối thiểu số bản ghi hợp lệ theo đề cương đề tài 
MIN_RECORDS = 300 

# Ánh xạ tên cột gốc về tên chuẩn theo đề cương 
RENAME_MAP = { 
    "date": "ngay", 
    "ngày": "ngay", 
    "ngay": "ngay", 
    "datetime": "ngay", 
    "close": "xauusd", 
    "adj close": "xauusd", 
    "price": "xauusd", 
    "xau_close": "xauusd", 
    "xauusd": "xauusd", 
    "open": "xau_open", 
    "high": "xau_high", 
    "low": "xau_low", 
    "change": "xau_change_pct", 
    "change %": "xau_change_pct" 
} 

def _to_number(s: pd.Series) -> pd.Series: 
    """Xóa dấu phẩy, dấu % và ép kiểu về số thực (float).""" 
    s = s.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False) 
    return pd.to_numeric(s.str.strip(), errors="coerce") 

def _to_date(s: pd.Series) -> pd.Series: 
    """Chuẩn hóa cột ngày tháng sang kiểu datetime (YYYY-MM-DD), loại bỏ phần giờ.""" 
    s = s.astype(str).str.strip() 
    d = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce") 
    miss = d.isna() 
    if miss.any(): 
        with warnings.catch_warnings(): 
            warnings.simplefilter("ignore") 
            d[miss] = pd.to_datetime(s[miss], errors="coerce") 
    return d.dt.normalize() 

def clean_xauusd(filepath: str) -> pd.DataFrame: 
    """Đọc và làm sạch dữ liệu XAU/USD chuẩn hóa cho bước ghép bảng. 
    Tham số: filepath (str): Đường dẫn đến file raw (.csv hoặc .xlsx). 
    Trả về: pd.DataFrame: Bảng sạch gồm 2 cột ['ngay', 'xauusd'] đã được sắp xếp tăng dần. 
    """ 
    # 1. Đọc dữ liệu 
    if filepath.lower().endswith((".xlsx", ".xls")): 
        df = pd.read_excel(filepath) 
    else: 
        df = pd.read_csv(filepath, encoding="utf-8-sig") 
        
    report = {"raw_rows": len(df)} 
    
    # 2. Xóa ký tự BOM ẩn (\ufeff) và khoảng trắng thừa ở tiêu đề cột 
    df.columns = [col.strip().replace("\ufeff", "") for col in df.columns] 
    
    # 3. Chuẩn hóa tên cột theo bảng ánh xạ 
    df.columns = [RENAME_MAP.get(str(c).strip().lower(), str(c).strip().lower()) for c in df.columns] 
    df = df.loc[:, ~df.columns.duplicated()] 
    
    # Kiểm tra tính toàn vẹn: bắt buộc phải có cột ngày và giá đóng cửa (xauusd) 
    if "ngay" not in df.columns or "xauusd" not in df.columns: 
        raise ValueError(f"Thiếu cột 'ngay' hoặc 'xauusd' (giá đóng cửa). Các cột hiện có: {list(df.columns)}") 
        
    # 4. Ép kiểu dữ liệu 
    df["ngay"] = _to_date(df["ngay"]) 
    df["xauusd"] = _to_number(df["xauusd"]) 
    
    # Ép kiểu tạm thời High/Low để kiểm tra tính hợp lệ dữ liệu (nếu có trong file thô) 
    for c in ["xau_high", "xau_low"]: 
        if c in df.columns: 
            df[c] = _to_number(df[c]) 
            
    # 5. Loại bỏ bản ghi thiếu ngày, thiếu giá hoặc giá <= 0 
    n = len(df) 
    df = df.dropna(subset=["ngay", "xauusd"]) 
    df = df[df["xauusd"] > 0] 
    report["dropped_missing_or_bad"] = n - len(df) 
    
    # 6. Kiểm định logic nghiệp vụ: Giá cao nhất (High) không được nhỏ hơn giá thấp nhất (Low) 
    if {"xau_high", "xau_low"}.issubset(df.columns): 
        n = len(df) 
        df = df[~(df["xau_high"] < df["xau_low"])] 
        report["dropped_high_lt_low"] = n - len(df) 
        
    # 7. Loại bỏ bản ghi trùng lặp ngày giao dịch và sắp xếp tăng dần theo thời gian 
    n = len(df) 
    df = df.drop_duplicates(subset=["ngay"], keep="last") 
    report["dropped_duplicates"] = n - len(df) 
    df = df.sort_values("ngay").reset_index(drop=True) 
    
    # 8. Trích xuất đúng 2 cột chuẩn theo đề cương phục vụ ghép bảng với SJC 
    df_clean = df[["ngay", "xauusd"]].copy() 
    
    # Lưu báo cáo kiểm định vào thuộc tính attrs để phục vụ viết báo cáo Mốc 03 
    report["clean_rows"] = len(df_clean) 
    if len(df_clean): 
        report["date_min"] = df_clean["ngay"].min().strftime("%Y-%m-%d") 
        report["date_max"] = df_clean["ngay"].max().strftime("%Y-%m-%d") 
        
    df_clean.attrs["report"] = report 
    return df_clean 

def summarize(df: pd.DataFrame, min_records: int = MIN_RECORDS) -> str: 
    """Tạo báo cáo tóm tắt chất lượng dữ liệu để đưa vào Báo cáo Mốc 03.""" 
    rep = df.attrs.get("report", {"clean_rows": len(df)}) 
    ok = rep.get("clean_rows", len(df)) >= min_records 
    lines = [f"- {k}: {v}" for k, v in rep.items()] 
    lines.append(f"- Tiêu chí >= {min_records} bản ghi hợp lệ: {'ĐẠT ✅' if ok else 'KHÔNG ĐẠT ❌'}") 
    return "\n".join(lines) 

# --- KHỐI CHẠY THỬ NGHIỆM ĐỘC LẬP CHO THÀNH VIÊN 3 --- 
if __name__ == "__main__": 
    src_file = sys.argv[1] if len(sys.argv) > 1 else "data/raw/xauusd_raw.csv" 
    print("⏳ Đang tiến hành làm sạch dữ liệu XAU/USD...") 
    try: 
        df_xau = clean_xauusd(src_file) 
        print("\n====== BÁO CÁO KIỂM THỬ XAU/USD (THÀNH VIÊN 3) ======") 
        print(summarize(df_xau)) 
        print(f"- Danh sách cột đầu ra: {list(df_xau.columns)}") 
        print("\n5 dòng đầu tiên:") 
        print(df_xau.head()) 
        print("\n5 dòng gần nhất:") 
        print(df_xau.tail()) 
        print("====================================================") 
    except Exception as e: 
        print(f"❌ Có lỗi xảy ra: {e}")