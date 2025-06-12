import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 資料夾路徑
folder_path = "就診千分比對pm2.5(不補值)"

# 輸出圖表資料夾
output_dir = "scatter_plots_no_fill_filtered"
os.makedirs(output_dir, exist_ok=True)

for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)

        # 保留需要的欄位並移除缺失值
        df = df[["case_per_capita(‰)", "PM2.5"]].dropna()

        # 移除多個 case_per_capita 對應同一 PM2.5 的資料
        duplicated_pm25 = df["PM2.5"].duplicated(keep=False)
        filtered_df = df[~duplicated_pm25]

        if len(filtered_df) < 2:
            print(f"{file_name} 過濾後資料不足，跳過。")
            continue

        # 計算皮爾森與斯皮爾曼相關
        pearson_corr, _ = pearsonr(filtered_df["case_per_capita(‰)"], filtered_df["PM2.5"])
        spearman_corr, _ = spearmanr(filtered_df["case_per_capita(‰)"], filtered_df["PM2.5"])

        # 畫散點圖
        plt.figure(figsize=(16, 9))
        plt.scatter(filtered_df["PM2.5"], filtered_df["case_per_capita(‰)"], alpha=0.5)
        plt.title(f"{file_name[:-4]}: 就診千分比 vs PM2.5（過濾重複 PM2.5）")
        plt.xlabel("PM2.5")
        plt.ylabel("就診人數千分比 (‰)")

        # 顯示相關係數
        plt.text(
            0.05, 0.95,
            f"Pearson: {pearson_corr:.2f}\nSpearman: {spearman_corr:.2f}",
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7)
        )

        # 儲存圖檔
        output_path = os.path.join(output_dir, f"{file_name[:-4]}_scatter_filtered.png")
        plt.savefig(output_path)
        plt.close()

print("完成：已產生過濾重複 PM2.5 值後的相關性圖表。")
