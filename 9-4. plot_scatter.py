# Re-import necessary libraries after kernel reset
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 資料夾設定
correlation_folder = "lag_corre_month+region"
case_pm25_folder = "就診千分比對pm2.5(五群)"
output_plot_folder = "scatter_plots_region_shift+0"
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
        kendall = row["Kendall Tau"]

        df_shifted = df.copy()
        df_shifted["new_month"] = df_shifted["month"] + lag
        df_shifted["new_year"] = df_shifted["year"] + (df_shifted["new_month"] - 1) // 12
        df_shifted["new_month"] = (df_shifted["new_month"] - 1) % 12 + 1
        df_shifted["new_key"] = df_shifted["region"] + "_" + df_shifted["new_year"].astype(str) + "_" + df_shifted["new_month"].astype(str)

        merged = pd.merge(
            df_shifted[["PM2.5", "new_key"]],
            df[["key", "case_per_capita(‰)"]],
            left_on="new_key",
            right_on="key",
            how="inner"
        )

        if len(merged) < 10:
            continue

        X = merged["PM2.5"].values.reshape(-1, 1)
        y = merged["case_per_capita(‰)"].values

        # Mutual Information
        mi = mutual_info_regression(X, y, random_state=0)[0]

        # R² 2nd degree
        model2 = make_pipeline(PolynomialFeatures(2), LinearRegression())
        r2_2 = model2.fit(X, y).score(X, y)

        # R² 3rd degree
        model3 = make_pipeline(PolynomialFeatures(3), LinearRegression())
        r2_3 = model3.fit(X, y).score(X, y)

        # 繪製散布圖
        plt.figure(figsize=(6, 5))
        plt.scatter(X, y, alpha=0.6)
        plt.xlabel("PM2.5")
        plt.ylabel("就診人數千分比")
        plt.title(f"{disease_name}：lag={lag} 散布圖")

        text = (
            f"Pearson: {pearson:.3f}\n"
            f"Spearman: {spearman:.3f}\n"
            f"Kendall: {kendall:.3f}\n"
            f"Mutual Info: {mi:.3f}\n"
            f"R² (2次): {r2_2:.3f}\n"
            f"R² (3次): {r2_3:.3f}"
        )

        plt.text(
            0.05, 0.95,
            text,
            transform=plt.gca().transAxes,
            verticalalignment='top',
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.6)
        )
        plt.tight_layout()

        plot_filename = f"{disease_name}_spearman_rank{rank}_lag{lag}.png"
        plt.savefig(os.path.join(output_plot_folder, plot_filename), dpi=300)
        plt.close()

print("✅ 所有疾病的相關性散布圖已完成（含 Mutual Info 與多項式 R²）")
