import os
import pandas as pd
from scipy.stats import spearmanr, pearsonr, kendalltau

# 輸入資料夾路徑
input_folder = "就診千分比對pm2.5(不補值)"

# 輸出資料夾
output_folder = "lag_correlation_results"
os.makedirs(output_folder, exist_ok=True)

# 處理每個 csv 檔案
for file_name in os.listdir(input_folder):
    if not file_name.endswith(".csv"):
        continue

    file_path = os.path.join(input_folder, file_name)
    df = pd.read_csv(file_path)

    # 篩選年份、欄位與缺失值
    df = df[df['year'].between(2016, 2019)].copy()
    df = df[["town", "year", "week", "case_per_capita(‰)", "PM2.5"]].dropna()
    df["key"] = df["town"] + "_" + df["year"].astype(str) + "_" + df["week"].astype(str)

    # 儲存每個平移的結果
    results = []

    for shift_weeks in range(1, 200):
        df_shifted = df.copy()

        # 計算新的 year 和 week
        df_shifted["new_week"] = df_shifted["week"] + shift_weeks
        df_shifted["new_year"] = df_shifted["year"]
        df_shifted["new_year"] += (df_shifted["new_week"] - 1) // 53
        df_shifted["new_week"] = (df_shifted["new_week"] - 1) % 53 + 1

        df_shifted["new_key"] = df_shifted["town"] + "_" + df_shifted["new_year"].astype(str) + "_" + df_shifted["new_week"].astype(str)

        # 合併資料
        merged = pd.merge(
            df_shifted[["PM2.5", "new_key"]],
            df[["key", "case_per_capita(‰)"]],
            left_on="new_key",
            right_on="key",
            how="inner"
        )

        if len(merged) > 10:
            spearman_corr, _ = spearmanr(merged["PM2.5"], merged["case_per_capita(‰)"])
            pearson_corr, _ = pearsonr(merged["PM2.5"], merged["case_per_capita(‰)"])
            kendall_corr, _ = kendalltau(merged["PM2.5"], merged["case_per_capita(‰)"])

            results.append({
                "平移量(週數)": shift_weeks,
                "Spearman 係數": spearman_corr,
                "Pearson 係數": pearson_corr,
                "Kendall Tau": kendall_corr
            })

    # 結果轉換成 DataFrame 並依 Spearman 排序
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Spearman 係數", ascending=False)

    # 儲存結果
    output_path = os.path.join(output_folder, f"{file_name[:-4]}_lag.csv")
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"完成：{file_name}")

print("✅ 全部疾病的平移分析已完成，結果儲存在 lag_correlation_results/")
