import os
import pandas as pd
from scipy.stats import spearmanr, pearsonr, kendalltau
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
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

            # 基本三種相關性
            spearman_corr, _ = spearmanr(x.ravel(), y)
            pearson_corr, _ = pearsonr(x.ravel(), y)
            kendall_corr, _ = kendalltau(x.ravel(), y)

            # Mutual Information
            mutual_info = mutual_info_regression(x, y, discrete_features=False)[0]

            # 多項式 R²（2 次與 3 次）
            poly2 = PolynomialFeatures(degree=2)
            poly3 = PolynomialFeatures(degree=3)

            x_poly2 = poly2.fit_transform(x)
            x_poly3 = poly3.fit_transform(x)

            model2 = LinearRegression().fit(x_poly2, y)
            model3 = LinearRegression().fit(x_poly3, y)

            r2_poly2 = r2_score(y, model2.predict(x_poly2))
            r2_poly3 = r2_score(y, model3.predict(x_poly3))

            results.append({
                "平移量(月數)": shift_months,
                "Spearman 係數": spearman_corr,
                "Pearson 係數": pearson_corr,
                "Kendall Tau": kendall_corr,
                "Mutual Info": mutual_info,
                "R² (2次)": r2_poly2,
                "R² (3次)": r2_poly3
            })

    # 匯出結果
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Spearman 係數", ascending=False)
    output_path = os.path.join(output_folder, f"{file_name[:-4]}_lag.csv")
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 完成：{file_name}")

print("🎉 全部疾病完成分析，已儲存到 lag_corre_month+region/")
