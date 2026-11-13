"""src/visualization.py - Trực quan hóa dữ liệu giá vàng SJC và giá thế giới. 
Do Thành viên 1 (Nguyễn Tuấn Minh) phụ trách: 
- Vẽ Biểu đồ 1: So sánh xu hướng giá bán SJC vs Giá thế giới quy đổi. 
- Vẽ Biểu đồ 2: Diễn biến mức chênh lệch tuyệt đối (Triệu đồng) và phần trăm (%). 
- Tự động xuất ảnh chất lượng cao vào data/processed/figures/ 
""" 
import os 
import matplotlib.pyplot as plt 
import numpy as np
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

"""
Do Thành viên 2 (Vũ Thị Thùy Trang) phụ trách:
- Vẽ Biểu đồ 3: Boxplot phân phối mức chênh lệch giá theo từng năm (2020 - 2026)
  kèm Histogram phân phối chung của cả giai đoạn.
- Vẽ Biểu đồ 4: Scatter Plot tương quan giữa giá bán SJC và giá thế giới quy đổi
  (kèm đường xu hướng, hệ số tương quan r) và biểu đồ biên độ mua - bán SJC theo thời gian.
"""
def _ensure_trieu_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Bổ sung cột biên độ mua-bán (triệu đồng) nếu load_merged_data chưa tạo."""
    df = df.copy()
    if "bien_do_trieu" not in df.columns:
        if "bien_do_mua_ban" in df.columns:
            bien_do = df["bien_do_mua_ban"]
        else:  # không có sẵn thì tự tính từ giá bán - giá mua
            bien_do = df["sjc_ban"] - df["sjc_mua"]
        df["bien_do_trieu"] = bien_do / 1_000_000 if df["sjc_ban"].mean() > 1_000 else bien_do
    df["nam"] = df["ngay"].dt.year
    return df
 
 
def plot_discrepancy_distribution(df: pd.DataFrame, output_dir: str = FIGURES_DIR) -> str:
    """Biểu đồ 3: Boxplot (theo từng năm) + Histogram phân phối mức chênh lệch giá."""
    df = _ensure_trieu_columns(df)
    nam_list = sorted(df["nam"].unique())
    du_lieu = [df.loc[df["nam"] == n, "chenh_lech_trieu"].dropna() for n in nam_list]
 
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300,
                                   gridspec_kw={"width_ratios": [2, 1]})
 
    # Boxplot chênh lệch theo từng năm
    bp = ax1.boxplot(du_lieu, patch_artist=True,
                     showmeans=True, flierprops={"markersize": 3, "alpha": 0.5},
                     meanprops={"marker": "D", "markerfacecolor": "white",
                                "markeredgecolor": "black", "markersize": 5})
    ax1.set_xticklabels([str(n) for n in nam_list])
    for hop in bp["boxes"]:
        hop.set_facecolor("#8ecae6")
        hop.set_edgecolor("#023047")
    for median in bp["medians"]:
        median.set_color("#d9534f")
        median.set_linewidth(2)
    ax1.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_title("Phân phối mức chênh lệch giá theo từng năm", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Năm", fontsize=11)
    ax1.set_ylabel("Chênh lệch SJC - thế giới quy đổi (Triệu đồng/lượng)", fontsize=10)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
 
    # Histogram toàn giai đoạn
    chenh_lech = df["chenh_lech_trieu"].dropna()
    ax2.hist(chenh_lech, bins=30, color="#8ecae6", edgecolor="#023047", alpha=0.9)
    ax2.axvline(chenh_lech.mean(), color="#d9534f", linestyle="--", linewidth=1.8,
                label=f"Trung bình: {chenh_lech.mean():.1f} triệu")
    ax2.axvline(chenh_lech.median(), color="#5cb85c", linestyle="-", linewidth=1.8,
                label=f"Trung vị: {chenh_lech.median():.1f} triệu")
    ax2.set_title("Phân phối chung (cả giai đoạn)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Chênh lệch (Triệu đồng/lượng)", fontsize=10)
    ax2.set_ylabel("Số ngày", fontsize=10)
    ax2.legend(loc="upper right", frameon=True, fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6)
 
    fig.suptitle("BIỂU ĐỒ 3: PHÂN PHỐI MỨC CHÊNH LỆCH GIÁ VÀNG SJC SO VỚI THẾ GIỚI QUY ĐỔI",
                 fontsize=13, fontweight="bold")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "chart3_boxplot.png")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()
 
    print(f"✅ Đã xuất Biểu đồ 3: {file_path}")
    return file_path
 
 
def plot_correlation_spread(df: pd.DataFrame, output_dir: str = FIGURES_DIR) -> str:
    """Biểu đồ 4: Scatter plot tương quan SJC - thế giới quy đổi + biên độ mua-bán SJC."""
    df = _ensure_trieu_columns(df)
    x = df["gia_quy_doi_trieu"]
    y = df["sjc_ban_trieu"]
    hop_le = x.notna() & y.notna()
    r = np.corrcoef(x[hop_le], y[hop_le])[0, 1]
    he_so = np.polyfit(x[hop_le], y[hop_le], 1)
 
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300,
                                   gridspec_kw={"width_ratios": [1, 1.2]})
 
    # Scatter: tô màu theo năm
    sc = ax1.scatter(x, y, c=df["nam"], cmap="viridis", s=12, alpha=0.7)
    xs = np.linspace(x[hop_le].min(), x[hop_le].max(), 100)
    ax1.plot(xs, he_so[0] * xs + he_so[1], color="#d9534f", linewidth=2,
             label=f"Đường xu hướng (r = {r:.3f})")
    cbar = fig.colorbar(sc, ax=ax1)
    cbar.set_label("Năm", fontsize=10)
    ax1.set_title("Tương quan giá SJC và giá thế giới quy đổi", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Giá thế giới quy đổi (Triệu đồng/lượng)", fontsize=10)
    ax1.set_ylabel("Giá bán SJC (Triệu đồng/lượng)", fontsize=10)
    ax1.legend(loc="upper left", frameon=True, fontsize=10)
    ax1.grid(True, linestyle=":", alpha=0.6)
 
    # Biên độ mua - bán SJC theo thời gian
    ax2.plot(df["ngay"], df["bien_do_trieu"], color="#f0ad4e", linewidth=1.4,
             label="Biên độ mua - bán SJC")
    ax2.axhline(df["bien_do_trieu"].mean(), color="gray", linestyle="--", linewidth=1,
                label=f"Trung bình: {df['bien_do_trieu'].mean():.2f} triệu")
    ax2.set_title("Biên độ mua - bán SJC theo thời gian", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Thời gian (Năm)", fontsize=10)
    ax2.set_ylabel("Biên độ (Triệu đồng/lượng)", fontsize=10)
    ax2.legend(loc="upper left", frameon=True, fontsize=10)
    ax2.grid(True, linestyle=":", alpha=0.6)
 
    fig.suptitle("BIỂU ĐỒ 4: TƯƠNG QUAN GIÁ VÀNG VÀ BIÊN ĐỘ MUA - BÁN SJC",
                 fontsize=13, fontweight="bold")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "chart4_correlation.png")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()
 
    print(f"✅ Đã xuất Biểu đồ 4: {file_path} (hệ số tương quan r = {r:.3f})")
    return file_path
 
 
def generate_charts_3_4(csv_path: str = "data/processed/gold_final_merged.csv",
                        output_dir: str = FIGURES_DIR):
    """Hàm tổng hợp: chạy xuất Biểu đồ 3 và Biểu đồ 4."""
    print("Đang tải dữ liệu để vẽ Biểu đồ 3 & 4...")
    df = load_merged_data(csv_path)
    plot_discrepancy_distribution(df, output_dir)
    plot_correlation_spread(df, output_dir)
    print("Hoàn thành Biểu đồ 3 & Biểu đồ 4!")
                            
if __name__ == "__main__": 
    generate_member1_charts()
    generate_charts_3_4()    
