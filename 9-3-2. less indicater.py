import os
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.linear_model import LinearRegression
import numpy as np

# 資料夾設定
input_folder = "就診千分比對pm2.5(五群)"
output_folder = "lag_corre_month+region"
os.makedirs(output_folder, exist_ok=True)

# 處理每個檔案
for file_name in os.listdir(input_folder):
    if not file_name.endswith(".csv"):
        continue

    file_path = os.path.join(input_folder, file_name)
    df = pd.read_csv(file_path)

    # 篩選並整理資料
    df = df[df['year'].between(2016, 2019)].copy()
    df = df[["region", "year", "month", "case_per_capita(‰)", "PM2.5"]].dropna()
    df["key"] = df["region"] + "_" + df["year"].astype(str) + "_" + df["month"].astype(str)

    results = []

    for shift_months in range(0, 40):
        df_shifted = df.copy()
        df_shifted["new_month"] = df_shifted["month"] + shift_months
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

        if len(merged) > 10:
            x = merged["PM2.5"].values.reshape(-1, 1)
            y = merged["case_per_capita(‰)"].values

            # Spearman & Pearson
            spearman_corr, _ = spearmanr(x.ravel(), y)
            pearson_corr, _ = pearsonr(x.ravel(), y)

            # 線性回歸斜率
            model = LinearRegression().fit(x, y)
            slope = model.coef_[0]

            results.append({
                "平移量(月數)": shift_months,
                "Spearman 係數": spearman_corr,
                "Pearson 係數": pearson_corr,
                "回歸斜率": slope
            })

    # 匯出結果
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Spearman 係數", ascending=False)
    output_path = os.path.join(output_folder, f"{file_name[:-4]}_lag.csv")
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 完成：{file_name}")

print("🎉 全部疾病完成分析，已儲存到 lag_corre_month+region/")
