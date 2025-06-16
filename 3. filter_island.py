import pandas as pd
import os

# 設定資料夾路徑
input_folder = "月-呼吸道疾病就醫人數"
output_folder = "月-呼吸道疾病就醫人數"

# 如果輸出資料夾不存在就建立
os.makedirs(output_folder, exist_ok=True)

# 取得所有 csv 檔案路徑
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(input_folder, filename)
        
        # 讀取檔案，保留ID1_CITY開頭的0
        df = pd.read_csv(filepath, dtype={'ID1_CITY': str})
        
        # 篩選條件
        df_filtered = df[
            ~df['ID1_CITY'].str.startswith('44') &
            ~df['ID1_CITY'].isin(['4611', '4616'])
        ]

        # 確保只保留需要的欄位（若需要）
        df_filtered = df_filtered[['ID1_CITY', 'year', 'month', 'case_c']]
        
        # 輸出檔案，加 "_filtered" 字尾
        output_path = os.path.join(output_folder, filename.replace(".csv", "_filtered.csv"))
        df_filtered.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ 輸出完成：{output_path}")
