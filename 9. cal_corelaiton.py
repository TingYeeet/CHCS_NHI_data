import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 設定資料夾路徑
folder_path = "就診千分比對pm2.5(不補值)"

# 建立輸出圖表資料夾
output_dir = "scatter_plots_no_fill"
os.makedirs(output_dir, exist_ok=True)

# 遍歷所有 csv 檔案
for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)

        # 移除缺失值
        df = df[["year", "case_per_capita(‰)", "PM2.5"]].dropna()

        # 依照年份分組
        for year, group in df.groupby("year"):
            if group.empty:
                continue

            # 計算三種相關係數
            pearson_corr, _ = pearsonr(group["case_per_capita(‰)"], group["PM2.5"])
            spearman_corr, _ = spearmanr(group["case_per_capita(‰)"], group["PM2.5"])
            kendall_corr, _ = kendalltau(group["case_per_capita(‰)"], group["PM2.5"])

            # 畫圖
            plt.figure(figsize=(16, 9))
            plt.scatter(group["PM2.5"], group["case_per_capita(‰)"], alpha=0.5)
            disease_name = file_name[:-4]
            plt.title(f"{disease_name}（{year}年）: 就診千分比 vs PM2.5")
            plt.xlabel("PM2.5")
            plt.ylabel("就診人數千分比 (‰)")

            # 標註相關係數
            plt.text(
                0.05, 0.95,
                f"Pearson: {pearson_corr:.2f}\nSpearman: {spearman_corr:.2f}\nKendall Tau: {kendall_corr:.2f}",
                transform=plt.gca().transAxes,
                fontsize=10,
                verticalalignment="top",
                bbox=dict(facecolor="white", alpha=0.7)
            )

            # 儲存圖檔
            output_path = os.path.join(output_dir, f"{disease_name}_{year}_scatter.png")
            plt.savefig(output_path)
            plt.close()

print("依疾病與年份分析與圖表已完成，結果儲存在 scatter_plots_by_year 資料夾中。")
