import pandas as pd
import os

# 輸入篩選後資料夾
# input_folder = "周-呼吸道疾病就醫人-移除外島"
input_folder = "補值後CSV"

# 用來儲存所有資料
all_data = []

# 讀取所有 CSV 檔案
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(input_folder, filename)
        df = pd.read_csv(filepath, dtype={'ID1_CITY': str})
        df['source_file'] = filename  # 可追溯資料來源
        all_data.append(df)

# 合併成一個總表
merged_df = pd.concat(all_data, ignore_index=True)

# 計算每個 ID1_CITY + year 的週數出現次數
week_counts = (
    merged_df.groupby(['ID1_CITY', 'year', 'source_file'])
    .agg(week_count=('week', 'nunique'))
    .reset_index()
)

# 篩選出週數少於 53 的項目
missing_weeks = week_counts[week_counts['week_count'] < 53]

# 輸出為 CSV
missing_weeks.to_csv("少週數的_補值後.csv", index=False, encoding="utf-8-sig")

print("✅ 已找出缺少週數的鄉鎮市區，輸出為：缺少週數的鄉鎮市區.csv")
