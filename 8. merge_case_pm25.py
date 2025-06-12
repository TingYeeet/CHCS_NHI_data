import pandas as pd
import os

input_folder = "不補值轉發病比"
output_folder = "就診千分比對pm2.5(不補值)"
os.makedirs(output_folder, exist_ok=True)

df_pm25 = pd.read_csv('PM25_weekly_by_town.csv')
df_code = pd.read_csv('ID_CNAME.csv', dtype={'ID1_CITY': str})

# 去除空白（避免匹配錯誤）
df_code['C_NAME'] = df_code['C_NAME'].str.strip()

for filename in os.listdir(input_folder):
    if not filename.endswith(".csv"):
        continue

    # 讀取資料
    df_case = pd.read_csv(os.path.join(input_folder, filename), dtype={'ID1_CITY': str})

    # 1️⃣ 將 ID1_CITY 對應到中文地區名稱
    df_case = df_case.merge(df_code, on='ID1_CITY', how='left')

    # 檢查有沒有轉換不到的
    missing = df_case[df_case['C_NAME'].isna()]
    if not missing.empty:
        print("⚠️ 以下地區代碼無法對應：")
        print(missing[['ID1_CITY']].drop_duplicates())

    # 2️⃣ 將 C_NAME 改成 'town'，以利與 PM2.5 合併
    df_case.rename(columns={'C_NAME': 'town'}, inplace=True)

    # 3️⃣ 合併疾病與 PM2.5 資料
    df_merged = pd.merge(df_case, df_pm25, on=['town', 'year', 'week'], how='inner')

    # 4️⃣ 選取指定欄位並輸出
    df_final = df_merged[['town', 'year', 'week', 'case_per_capita(‰)', 'PM2.5']]
    df_final.to_csv(os.path.join(output_folder, filename), index=False, encoding='utf-8-sig')

    print(f"✅ 合併完成，已輸出為 {filename}")
