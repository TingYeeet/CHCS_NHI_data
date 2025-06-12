import pandas as pd
import os

# 資料夾與路徑設定
input_folder = "周-呼吸道疾病就醫人數"
output_folder = "補值後轉發病比(不補值)"
pop_csv_path = "./各鄉鎮在保人數分布/total_population_2016_2019.csv"

# 建立輸出資料夾
os.makedirs(output_folder, exist_ok=True)

# 讀取人口總表
pop_df = pd.read_csv(pop_csv_path, dtype={'ID1_CITY': str})
pop_df = pop_df.rename(columns={"total_pop": "pop_total"})

# 處理每個 CSV 檔
for filename in os.listdir(input_folder):
    if not filename.endswith(".csv"):
        continue

    filepath = os.path.join(input_folder, filename)
    df = pd.read_csv(filepath, dtype={'ID1_CITY': str})

    # 合併人口數
    merged = pd.merge(df, pop_df, on=["ID1_CITY", "year"], how="left")

    # 計算每千人病例數
    merged['case_per_capita(‰)'] = (merged['case_c'] / merged['pop_total'] * 1000).round(3)

    # 保留指定欄位
    merged = merged[['ID1_CITY', 'year', 'week', 'case_c', 'case_per_capita(‰)']]

    # 輸出
    output_path = os.path.join(output_folder, filename)
    merged.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 已處理並輸出：{output_path}")
