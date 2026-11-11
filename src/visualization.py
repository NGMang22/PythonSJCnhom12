"""src/visualization.py - Trực quan hóa dữ liệu giá vàng SJC và giá thế giới. 
Do Thành viên 1 (Nguyễn Tuấn Minh) phụ trách: 
- Vẽ Biểu đồ 1: So sánh xu hướng giá bán SJC vs Giá thế giới quy đổi. 
- Vẽ Biểu đồ 2: Diễn biến mức chênh lệch tuyệt đối (Triệu đồng) và phần trăm (%). 
- Tự động xuất ảnh chất lượng cao vào data/processed/figures/ 
""" 
import os 
import matplotlib.pyplot as plt 
import pandas as pd 

# Thiết lập font và style cho biểu đồ đẹp mắt 
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default") 
plt.rcParams["font.family"] = "sans-serif" 
plt.rcParams["axes.edgecolor"] = "#cccccc" 
plt.rcParams["axes.linewidth"] = 0.8 

FIGURES_DIR = "data/processed/figures" 

def load_merged_data(csv_path: str = "data/processed/gold_final_merged.csv") -> pd.DataFrame: 
    """Đọc dữ liệu sạch và chuẩn hóa đơn vị hiển thị.""" 
    df = pd.read_csv(csv_path) 
    df["ngay"] = pd.to_datetime(df["ngay"]) 
    df = df.sort_values("ngay").reset_index(drop=True) 
    
    # Đảm bảo giá trị hiển thị ở đơn vị Triệu VNĐ/lượng để đồ thị gọn gàng 
    if df["sjc_ban"].mean() > 1_000: 
        df["sjc_ban_trieu"] = df["sjc_ban"] / 1_000_000 
        df["gia_quy_doi_trieu"] = df["gia_quy_doi"] / 1_000_000 
        df["chenh_lech_trieu"] = df["chenh_lech"] / 1_000_000 
    else: 
        df["sjc_ban_trieu"] = df["sjc_ban"] 
        df["gia_quy_doi_trieu"] = df["gia_quy_doi"] 
        df["chenh_lech_trieu"] = df["chenh_lech"] 
        
    return df 

def plot_price_trend(df: pd.DataFrame, output_dir: str = FIGURES_DIR) -> str: 
    """Biểu đồ 1: So sánh xu hướng giá bán SJC và Giá thế giới quy đổi (2020 - 2026).""" 
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300) 
    
    # Vẽ đường biểu diễn 
    ax.plot(df["ngay"], df["sjc_ban_trieu"], label="Giá bán SJC trong nước", color="#d9534f", linewidth=2) 
    ax.plot(df["ngay"], df["gia_quy_doi_trieu"], label="Giá thế giới quy đổi (VNĐ/lượng)", color="#0275d8", linewidth=1.8, linestyle="--") 
    
    # Trang trí biểu đồ 
    ax.set_title("BIỂU ĐỒ SO SÁNH XU HƯỚNG GIÁ VÀNG SJC VÀ GIÁ THẾ GIỚI QUY ĐỔI (2020 - 2026)", fontsize=13, fontweight="bold", pad=15) 
    ax.set_xlabel("Thời gian (Năm)", fontsize=11, labelpad=10) 
    ax.set_ylabel("Giá vàng (Triệu đồng / lượng)", fontsize=11, labelpad=10) 
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", fontsize=10) 
    ax.grid(True, linestyle=":", alpha=0.6) 
    
    # Tự động căn chỉnh và lưu ảnh 
    os.makedirs(output_dir, exist_ok=True) 
    file_path = os.path.join(output_dir, "chart1_trend.png") 
    plt.tight_layout() 
    plt.savefig(file_path, dpi=300) 
    plt.close() 
    
    print(f"✅ Đã xuất Biểu đồ 1: {file_path}") 
    return file_path 

def plot_price_discrepancy(df: pd.DataFrame, output_dir: str = FIGURES_DIR) -> str: 
    """Biểu đồ 2: Diễn biến mức chênh lệch giá (Tuyệt đối & Tương đối %).""" 
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, dpi=300) 
    
    # Đồ thị 1: Chênh lệch tuyệt đối (Triệu VNĐ/lượng) 
    ax1.plot(df["ngay"], df["chenh_lech_trieu"], color="#f0ad4e", linewidth=1.8, label="Chênh lệch tuyệt đối (Triệu đồng)") 
    ax1.axhline(0, color="gray", linestyle="--", linewidth=0.8) 
    ax1.set_title("DIỄN BIẾN MỨC CHÊNH LỆCH GIÁ VÀNG SJC SO VỚI THẾ GIỚI QUY ĐỔI", fontsize=13, fontweight="bold", pad=12) 
    ax1.set_ylabel("Chênh lệch (Triệu đồng/lượng)", fontsize=10) 
    ax1.legend(loc="upper left", frameon=True) 
    ax1.grid(True, linestyle=":", alpha=0.6) 
    
    # Đồ thị 2: Chênh lệch tương đối (%) 
    ax2.plot(df["ngay"], df["chenh_lech_pct"], color="#5cb85c", linewidth=1.8, label="Chênh lệch tương đối (%)") 
    ax2.axhline(0, color="gray", linestyle="--", linewidth=0.8) 
    ax2.set_xlabel("Thời gian (Năm)", fontsize=11, labelpad=10) 
    ax2.set_ylabel("Chênh lệch (%)", fontsize=10) 
    ax2.legend(loc="upper left", frameon=True) 
    ax2.grid(True, linestyle=":", alpha=0.6) 
    
    # Lưu ảnh 
    os.makedirs(output_dir, exist_ok=True) 
    file_path = os.path.join(output_dir, "chart2_discrepancy.png") 
    plt.tight_layout() 
    plt.savefig(file_path, dpi=300) 
    plt.close() 
    
    print(f"✅ Đã xuất Biểu đồ 2: {file_path}") 
    return file_path 

def generate_member1_charts(csv_path: str = "data/processed/gold_final_merged.csv", output_dir: str = FIGURES_DIR): 
    """Hàm tổng hợp dành cho TV1 để chạy xuất cả 2 biểu đồ.""" 
    print("⏳ [TV1] Đang tải dữ liệu để vẽ biểu đồ...") 
    df = load_merged_data(csv_path) 
    plot_price_trend(df, output_dir) 
    plot_price_discrepancy(df, output_dir) 
    print("🎉 [TV1] Hoàn thành 100% nhiệm vụ vẽ Biểu đồ 1 & Biểu đồ 2!") 

if __name__ == "__main__": 
    generate_member1_charts()
