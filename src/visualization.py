"""
visualization.py - Module vẽ toàn bộ 4 biểu đồ trực quan hóa dự án phân tích giá vàng SJC.

Đầu vào : data/processed/gold_final_merged.csv (do feature_engineering.py xuất ra)
Đầu ra  : Các ảnh biểu đồ (.png) lưu tại data/processed/figures/
          - Hình 1 / Chart 1: Diễn biến giá bán SJC & giá thế giới quy đổi
          - Hình 2 / Chart 2: Chênh lệch tuyệt đối & tương đối theo thời gian
          - Hình 3 / Chart 3: Phân phối chênh lệch giá (Boxplot theo năm & Histogram)
          - Hình 4 / Chart 4: Tương quan Scatter Plot & Biên độ mua - bán SJC
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Chế độ headless cho môi trường máy trạm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def setup_style():
    """Thiết lập font chữ và theme đồ họa chuẩn báo cáo."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8

def load_merged_data(csv_path: str = "data/processed/gold_final_merged.csv") -> pd.DataFrame:
    """
    Đọc dữ liệu đã merge và chuẩn hóa đơn vị:
    - Chuyển 'ngay' về datetime
    - Đảm bảo các cột SJC và giá quy đổi ở đơn vị TRIỆU ĐỒNG / LƯỢNG
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Không tìm thấy tệp dữ liệu: {csv_path}")

    df = pd.read_csv(csv_path)

    # Chuẩn hóa tên cột ngày
    date_col = 'ngay' if 'ngay' in df.columns else ('Date' if 'Date' in df.columns else df.columns[0])
    df['ngay'] = pd.to_datetime(df[date_col])
    df = df.sort_values('ngay').reset_index(drop=True)

    # Chuẩn hóa tên cột SJC mua / bán
    sjc_ban_col = 'sjc_ban' if 'sjc_ban' in df.columns else ('sjc_sell' if 'sjc_sell' in df.columns else 'sjc')
    sjc_mua_col = 'sjc_mua' if 'sjc_mua' in df.columns else ('sjc_buy' if 'sjc_buy' in df.columns else sjc_ban_col)

    df['sjc_ban_val'] = df[sjc_ban_col]
    df['sjc_mua_val'] = df[sjc_mua_col]

    # Kiểm tra và quy đổi đơn vị về Triệu đồng/lượng
    if df['sjc_ban_val'].mean() > 1000:
        df['sjc_ban_trieu'] = df['sjc_ban_val'] / 1_000_000
        df['sjc_mua_trieu'] = df['sjc_mua_val'] / 1_000_000
    else:
        df['sjc_ban_trieu'] = df['sjc_ban_val']
        df['sjc_mua_trieu'] = df['sjc_mua_val']

    # Giá quy đổi
    if 'gia_quy_doi' in df.columns:
        df['gia_quy_doi_trieu'] = df['gia_quy_doi'] / 1_000_000 if df['gia_quy_doi'].mean() > 1000 else df['gia_quy_doi']
    else:
        TROY_OUNCE_TO_TAEL = 1.205653
        df['gia_quy_doi_trieu'] = (df['xauusd'] * TROY_OUNCE_TO_TAEL * df['usd_vnd']) / 1_000_000

    # Chênh lệch tuyệt đối & tương đối
    if 'chenh_lech' in df.columns:
        df['chenh_lech_trieu'] = df['chenh_lech'] / 1_000_000 if df['chenh_lech'].mean() > 1000 else df['chenh_lech']
    else:
        df['chenh_lech_trieu'] = df['sjc_ban_trieu'] - df['gia_quy_doi_trieu']

    if 'chenh_lech_pct' in df.columns:
        df['chenh_lech_pct_val'] = df['chenh_lech_pct']
    elif 'chech_lech_ptc' in df.columns:
        df['chenh_lech_pct_val'] = df['chech_lech_ptc']
    else:
        df['chenh_lech_pct_val'] = (df['chenh_lech_trieu'] / df['gia_quy_doi_trieu']) * 100

    # Biên độ mua - bán
    if 'bien_do_mua_ban' in df.columns:
        df['bien_do_trieu'] = df['bien_do_mua_ban'] / 1_000_000 if df['bien_do_mua_ban'].mean() > 1000 else df['bien_do_mua_ban']
    else:
        df['bien_do_trieu'] = df['sjc_ban_trieu'] - df['sjc_mua_trieu']

    df['nam'] = df['ngay'].dt.year
    return df


# -------------------------------------------------------------
# BIỂU ĐỒ 1: DIỄN BIẾN GIÁ BÁN SJC VÀ GIÁ THẾ GIỚI QUY ĐỔI
# -------------------------------------------------------------
def plot_chart1_price_trend(df: pd.DataFrame, output_dir: str):
    """Vẽ Biểu đồ 1: Diễn biến giá bán SJC và giá vàng thế giới quy đổi (2020–2026)."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)

    ax.plot(df['ngay'], df['sjc_ban_trieu'], label='Giá bán SJC', color='#d55e00', linewidth=2.0)
    ax.plot(df['ngay'], df['gia_quy_doi_trieu'], label='Giá thế giới quy đổi', color='#0072b2', linewidth=1.8, linestyle='--')

    ax.set_title("BIỂU ĐỒ 1: DIỄN BIẾN GIÁ BÁN SJC VÀ GIÁ VÀNG THẾ GIỚI QUY ĐỔI (2020–2026)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Thời gian", fontsize=10, labelpad=8)
    ax.set_ylabel("Giá vàng (Triệu VNĐ / Lượng)", fontsize=10, labelpad=8)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)

    fig.tight_layout()
    # Lưu đồng thời cả 2 tên file để tương thích
    fig.savefig(os.path.join(output_dir, "hinh1.png"), bbox_inches='tight', dpi=200)
    fig.savefig(os.path.join(output_dir, "chart1_trend.png"), bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f" ✅ Đã xuất Biểu đồ 1 -> {os.path.join(output_dir, 'hinh1.png')}")


# -------------------------------------------------------------
# BIỂU ĐỒ 2: CHÊNH LỆCH TUYỆT ĐỐI VÀ TƯƠNG ĐỐI
# -------------------------------------------------------------
def plot_chart2_discrepancy(df: pd.DataFrame, output_dir: str):
    """Vẽ Biểu đồ 2: Chênh lệch tuyệt đối (Triệu đồng/lượng) và tương đối (%)."""
    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=200)

    color_abs = '#e69f00'
    color_pct = '#009e73'

    ax1.plot(df['ngay'], df['chenh_lech_trieu'], color=color_abs, linewidth=1.8, label='Chênh lệch tuyệt đối (Triệu đồng)')
    ax1.set_xlabel("Thời gian", fontsize=10, labelpad=8)
    ax1.set_ylabel("Chênh lệch tuyệt đối (Triệu VNĐ / Lượng)", color=color_abs, fontsize=10)
    ax1.tick_params(axis='y', labelcolor=color_abs)
    ax1.grid(True, linestyle=':', alpha=0.5)

    ax2 = ax1.twinx()
    ax2.plot(df['ngay'], df['chenh_lech_pct_val'], color=color_pct, linewidth=1.5, linestyle='-.', label='Chênh lệch tương đối (%)')
    ax2.set_ylabel("Chênh lệch tương đối (%)", color=color_pct, fontsize=10)
    ax2.tick_params(axis='y', labelcolor=color_pct)
    ax2.grid(False)

    ax1.axhline(0, color='#888888', linestyle='--', linewidth=0.8, alpha=0.7)
    plt.title("BIỂU ĐỒ 2: CHÊNH LỆCH TUYỆT ĐỐI VÀ TƯƠNG ĐỐI GIỮA GIÁ SJC VÀ THẾ GIỚI QUY ĐỔI", fontsize=12, fontweight='bold', pad=15)

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='white')

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "hinh2.png"), bbox_inches='tight', dpi=200)
    fig.savefig(os.path.join(output_dir, "chart2_discrepancy.png"), bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f" ✅ Đã xuất Biểu đồ 2 -> {os.path.join(output_dir, 'hinh2.png')}")


# -------------------------------------------------------------
# BIỂU ĐỒ 3: PHÂN PHỐI MỨC CHÊNH LỆCH GIÁ (BOXPLOT + HISTOGRAM)
# -------------------------------------------------------------
def plot_chart3_distribution(df: pd.DataFrame, output_dir: str):
    """Vẽ Biểu đồ 3: Boxplot phân phối chênh lệch theo từng năm + Histogram toàn kỳ."""
    fig, (ax_box, ax_hist) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)

    # 1. Boxplot theo từng năm
    years = sorted(df['nam'].unique())
    data_by_year = [df[df['nam'] == y]['chenh_lech_trieu'].dropna() for y in years]

    bp = ax_box.boxplot(
        data_by_year,
        labels=[str(y) for y in years],
        patch_artist=True,
        showmeans=True,
        meanprops=dict(marker='D', markeredgecolor='#0072b2', markerfacecolor='white', markersize=5),
        medianprops=dict(color='#d55e00', linewidth=2),
        boxprops=dict(facecolor='#ecefe6', color='#333333', linewidth=1),
        whiskerprops=dict(color='#555555', linewidth=1),
        capprops=dict(color='#555555', linewidth=1),
        flierprops=dict(marker='o', markersize=3, markerfacecolor='#999999', alpha=0.5)
    )
    ax_box.set_title("Phân phối mức chênh lệch theo năm (Boxplot)", fontsize=11, fontweight='bold', pad=10)
    ax_box.set_xlabel("Năm", fontsize=10)
    ax_box.set_ylabel("Mức chênh lệch (Triệu VNĐ / Lượng)", fontsize=10)
    ax_box.grid(True, axis='y', linestyle=':', alpha=0.6)

    # 2. Histogram toàn kỳ
    n, bins, patches = ax_hist.hist(df['chenh_lech_trieu'], bins=30, color='#0072b2', edgecolor='white', alpha=0.85)
    mean_val = df['chenh_lech_trieu'].mean()
    median_val = df['chenh_lech_trieu'].median()

    ax_hist.axvline(mean_val, color='#d55e00', linestyle='--', linewidth=1.8, label=f'Trung bình: {mean_val:.1f} triệu')
    ax_hist.axvline(median_val, color='#009e73', linestyle='-', linewidth=1.8, label=f'Trung vị: {median_val:.1f} triệu')

    ax_hist.set_title("Phân phối chênh lệch toàn kỳ (Histogram)", fontsize=11, fontweight='bold', pad=10)
    ax_hist.set_xlabel("Mức chênh lệch (Triệu VNĐ / Lượng)", fontsize=10)
    ax_hist.set_ylabel("Tần suất (Số ngày)", fontsize=10)
    ax_hist.grid(True, linestyle=':', alpha=0.6)
    ax_hist.legend(loc='upper right', frameon=True, facecolor='white')

    fig.suptitle("BIỂU ĐỒ 3: PHÂN PHỐI MỨC CHÊNH LỆCH GIÁ VÀNG SJC SO VỚI THẾ GIỚI QUY ĐỔI", fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(output_dir, "hinh3.png"), bbox_inches='tight', dpi=200)
    fig.savefig(os.path.join(output_dir, "chart3_distribution.png"), bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f" ✅ Đã xuất Biểu đồ 3 -> {os.path.join(output_dir, 'hinh3.png')}")


# -------------------------------------------------------------
# BIỂU ĐỒ 4: TƯƠNG QUAN GIÁ VÀ BIÊN ĐỘ MUA - BÁN SJC
# -------------------------------------------------------------
def plot_chart4_correlation_spread(df: pd.DataFrame, output_dir: str):
    """Vẽ Biểu đồ 4: Scatter plot tương quan SJC vs Thế giới + Đường biến động biên độ Mua - Bán."""
    fig, (ax_scat, ax_spread) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)

    # 1. Scatter plot tương quan
    x = df['gia_quy_doi_trieu']
    y = df['sjc_ban_trieu']
    scatter = ax_scat.scatter(x, y, c=df['nam'], cmap='viridis', alpha=0.6, s=15, edgecolors='none')
    cbar = fig.colorbar(scatter, ax=ax_scat, pad=0.02)
    cbar.set_label('Năm', fontsize=9)

    # Đường xu hướng Hồi quy tuyến tính
    idx = np.isfinite(x) & np.isfinite(y)
    poly = np.polyfit(x[idx], y[idx], 1)
    poly_fn = np.poly1d(poly)
    x_range = np.linspace(x.min(), x.max(), 100)
    r_corr = np.corrcoef(x[idx], y[idx])[0, 1]

    ax_scat.plot(x_range, poly_fn(x_range), color='#d55e00', linewidth=2, linestyle='--', label=f'Hồi quy (r = {r_corr:.3f})')
    ax_scat.set_title("Tương quan giữa Giá TG quy đổi & Giá bán SJC", fontsize=11, fontweight='bold', pad=10)
    ax_scat.set_xlabel("Giá thế giới quy đổi (Triệu VNĐ / Lượng)", fontsize=10)
    ax_scat.set_ylabel("Giá bán SJC (Triệu VNĐ / Lượng)", fontsize=10)
    ax_scat.grid(True, linestyle=':', alpha=0.6)
    ax_scat.legend(loc='upper left', frameon=True, facecolor='white')

    # 2. Biên độ mua - bán SJC theo thời gian
    ax_spread.plot(df['ngay'], df['bien_do_trieu'], color='#cc79a7', linewidth=1.5, label='Biên độ Mua - Bán SJC')
    mean_spread = df['bien_do_trieu'].mean()
    ax_spread.axhline(mean_spread, color='#0072b2', linestyle='--', linewidth=1.5, label=f'Trung bình: {mean_spread:.2f} triệu')

    ax_spread.set_title("Biên độ mua – bán SJC theo thời gian", fontsize=11, fontweight='bold', pad=10)
    ax_spread.set_xlabel("Thời gian", fontsize=10)
    ax_spread.set_ylabel("Biên độ Mua - Bán (Triệu VNĐ / Lượng)", fontsize=10)
    ax_spread.xaxis.set_major_locator(mdates.YearLocator())
    ax_spread.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_spread.grid(True, linestyle=':', alpha=0.6)
    ax_spread.legend(loc='upper left', frameon=True, facecolor='white')

    fig.suptitle("BIỂU ĐỒ 4: TƯƠNG QUAN GIÁ VÀ BIÊN ĐỘ MUA – BÁN SJC", fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(output_dir, "hinh4.png"), bbox_inches='tight', dpi=200)
    fig.savefig(os.path.join(output_dir, "chart4_correlation_spread.png"), bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f" ✅ Đã xuất Biểu đồ 4 -> {os.path.join(output_dir, 'hinh4.png')}")


# -------------------------------------------------------------
# HÀM TỔNG HỢP GỌI TỪ MAIN.PY
# -------------------------------------------------------------
def generate_all_charts(csv_path: str = "data/processed/gold_final_merged.csv", output_dir: str = "data/processed/figures"):
    """
    Hàm chính thực thi xuất đầy đủ 4 biểu đồ trực quan hóa.
    """
    os.makedirs(output_dir, exist_ok=True)
    setup_style()

    print(f"\n🎨 Đang tiến hành vẽ và xuất trọn bộ 4 biểu đồ từ tệp: {csv_path}")
    df = load_merged_data(csv_path)

    plot_chart1_price_trend(df, output_dir)
    plot_chart2_discrepancy(df, output_dir)
    plot_chart3_distribution(df, output_dir)
    plot_chart4_correlation_spread(df, output_dir)

    print(f"🎉 ĐÃ HOÀN TẤT XUẤT 4 BIỂU ĐỒ VÀO THƯ MỤC: {output_dir}/\n")


# Alias giữ nguyên tương thích với hàm cũ trong main.py
def generate_member1_charts(csv_path: str = "data/processed/gold_final_merged.csv", output_dir: str = "data/processed/figures"):
    generate_all_charts(csv_path, output_dir)


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "data/processed/gold_final_merged.csv"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data/processed/figures"
    generate_all_charts(csv_file, out_dir)