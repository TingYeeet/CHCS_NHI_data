import pandas as pd
from collections import defaultdict
import re

# 讀取 Excel 檔案
excel_path = "./每月呼吸道疾病就醫人數/2016-2019 年每月呼吸道疾病就醫人數.xlsx"  # 修改為你的檔案名稱
xls = pd.ExcelFile(excel_path, engine='openpyxl')

# 建立一個 dict 來儲存同一病名的資料
disease_data = defaultdict(list)

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    df['ID1_CITY'] = df['ID1_CITY'].astype(str).str.zfill(4)

    # 聚合 case_c（合併 sex）
    grouped = df.groupby(['ID1_CITY', 'year', 'month'], as_index=False)['case_c'].sum()

    # 從工作表名稱擷取病名（去除年份）
    match = re.match(r"(.+?)\s*\d{4}$", sheet_name)
    disease_name = match.group(1).strip() if match else sheet_name

    disease_data[disease_name].append(grouped)

# 合併相同病名的資料並輸出成 csv
for disease, dfs in disease_data.items():
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.groupby(['ID1_CITY', 'year', 'month'], as_index=False)['case_c'].sum()
    combined_df.to_csv(f"./月-呼吸道疾病就醫人數/{disease}.csv", index=False, encoding='utf-8-sig')
    print(f"輸出完成：{disease}.csv")
