import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from matplotlib.lines import Line2D
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 區域顏色對應
region_color_map = {
    "高屏": "#AA04AA",        # 紫
    "中彰投": '#FF0000',      # 紅
    "雲嘉南": '#FFA500',      # 橘
    "北北基桃竹苗": '#FFFF00', # 黃
    "宜花東": "#23B623"       # 綠
}

# 資料夾設定
correlation_folder = "lag_corre_month+region"
case_pm25_folder = "就診千分比對pm2.5(五群)"
output_plot_folder = "scatter_plots_region_shift"
os.makedirs(output_plot_folder, exist_ok=True)

# 處理每個疾病的相關性 CSV
for filename in os.listdir(correlation_folder):
    if not filename.endswith(".csv"):
        continue

    disease_name = filename.replace("_filtered_with_PM25_lag.csv", "")
    correlation_path = os.path.join(correlation_folder, filename)
    correlation_df = pd.read_csv(correlation_path)

    # 挑出 top5 Spearman lag
    top5_lags = correlation_df.head(5)

    # 讀入原始的就診 + PM2.5 資料
    case_pm25_path = os.path.join(case_pm25_folder, f"{disease_name}_filtered_with_PM25.csv")
    if not os.path.exists(case_pm25_path):
        print(f"⚠️ 缺少檔案：{case_pm25_path}")
        continue

    df = pd.read_csv(case_pm25_path)
    df = df[df['year'].between(2016, 2019)].copy()
    df = df[["region", "year", "month", "case_per_capita(‰)", "PM2.5"]].dropna()
    df["key"] = df["region"] + "_" + df["year"].astype(str) + "_" + df["month"].astype(str)

    for rank, (_, row) in enumerate(top5_lags.iterrows(), start=1):
        lag = int(row["平移量(月數)"])
        pearson = row["Pearson 係數"]
        spearman = row["Spearman 係數"]

        df_shifted = df.copy()
        df_shifted["new_month"] = df_shifted["month"] + lag
        df_shifted["new_year"] = df_shifted["year"] + (df_shifted["new_month"] - 1) // 12
        df_shifted["new_month"] = (df_shifted["new_month"] - 1) % 12 + 1
        df_shifted["new_key"] = df_shifted["region"] + "_" + df_shifted["new_year"].astype(str) + "_" + df_shifted["new_month"].astype(str)
        df_shifted["region_copy"] = df_shifted["region"]

        merged = pd.merge(
            df_shifted[["PM2.5", "new_key", "region_copy"]],
            df[["key", "case_per_capita(‰)"]],
            left_on="new_key",
            right_on="key",
            how="inner"
        )

        if len(merged) < 10:
            continue

        X = merged["PM2.5"].values.reshape(-1, 1)
        y = merged["case_per_capita(‰)"].values
        colors = merged["region_copy"].map(region_color_map)

        # 繪製散布圖
        plt.figure(figsize=(7, 6))
        plt.scatter(X, y, alpha=0.6, c=colors)
        plt.xlabel("PM2.5(μg/m³)")
        plt.ylabel("就診人數(‰)")
        plt.title(f"{disease_name}：lag={lag} 散布圖")

        # 左上角文字顯示 Spearman 與 Pearson
        stats_text = (
            f"          總體\n"
            f"Pearson: {pearson:.3f}\n"
            f"Spearman: {spearman:.3f}"
        )
        plt.text(
            0.02, 0.98,
            stats_text,
            transform=plt.gca().transAxes,
            verticalalignment='top',
            horizontalalignment='left',
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7)
        )

        # 每個群集畫自己的線性回歸線，並記錄斜率
        legend_elements = []
        for region, color in region_color_map.items():
            sub = merged[merged["region_copy"] == region]
            if len(sub) < 2:
                continue
            X_sub = sub["PM2.5"].values.reshape(-1, 1)
            y_sub = sub["case_per_capita(‰)"].values
            reg = LinearRegression().fit(X_sub, y_sub)
            slope = reg.coef_[0]
            x_range = np.linspace(X_sub.min(), X_sub.max(), 100).reshape(-1, 1)
            y_pred = reg.predict(x_range)
            plt.plot(x_range, y_pred, color=color, linewidth=1.8)
            
            # 將斜率數值直接加到圖例標籤中
            label_with_slope = f"{region} (m={slope:.4f})"
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', label=label_with_slope,
                    markerfacecolor=color, markersize=8)
            )

        # 圖例顯示在右下角，含斜率
        plt.legend(handles=legend_elements, title="區域", loc='lower right', frameon=True)

        plt.tight_layout()

        # 儲存圖檔
        plot_filename = f"{disease_name}_spearman_rank{rank}_lag{lag}.png"
        plt.savefig(os.path.join(output_plot_folder, plot_filename), dpi=300)
        plt.close()

        print(f"{disease_name} rank {rank} lag {lag}繪製完成")

print("✅ 所有疾病的相關性散布圖已完成（含顏色、圖例與群集回歸斜率）")
