import pandas as pd

# 1. Đọc dữ liệu 
df = pd.read_csv("usdvnd_raw.csv", thousands=",")

# 2. Đổi tên cột sang tiếng Anh
df = df.rename(columns={
    "Ngày": "Date",
    "Lần cuối": "Close",
    "Mở": "Open",
    "Cao": "High",
    "Thấp": "Low",
    "KL": "Volume",
    "% Thay đổi": "Change_pct",
})

# 3. Chuẩn hóa cột ngày 
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")

# 4. Chuyển "0.02K" -> 20 và "-0.01%" -> -0.01
df["Volume"] = (df["Volume"].astype(str)
                .str.replace("K", "", regex=False)
                .replace("nan", None)
                .astype(float) * 1000)
df["Change_pct"] = df["Change_pct"].astype(str).str.replace("%", "", regex=False).astype(float)

# 5. Sắp xếp, bỏ trùng, tạo đủ các ngày liên tục (cả thứ 7, chủ nhật)
df = df.sort_values("Date").drop_duplicates("Date").set_index("Date")
full_range = pd.date_range(df.index.min(), df.index.max(), freq="D")
df = df.reindex(full_range)
df.index.name = "Date"

# 6. Forward fill giá; ngày nghỉ thì khối lượng và % thay đổi = 0
price_cols = ["Close", "Open", "High", "Low"]
df[price_cols] = df[price_cols].ffill()
df[["Volume", "Change_pct"]] = df[["Volume", "Change_pct"]].fillna(0)

# 7. Lưu kết quả
df.reset_index().to_csv("usdvnd_clean.csv", index=False)
print(df.head(12))