import pandas as pd

# 原始 Excel 檔案名稱
input_file = './各鄉鎮在保人數分布/2016-2019 年各鄉鎮在保人數分布.xlsx'  # <- 替換為你的檔名
output_csv = 'total_population_2016_2019.csv'

# 讀取所有工作表
all_sheets = pd.read_excel(input_file, sheet_name=None)

# 存所有年度加總資料
all_years_combined = []

for sheet_name, df in all_sheets.items():
    # 加總人口數 pop_c，依照行政區、名稱、年份
    grouped = df.groupby(['ID1_CITY', 'C_NAME', 'year'], as_index=False)['pop_c'].sum()
    grouped = grouped.rename(columns={'pop_c': 'total_pop'})
    
    all_years_combined.append(grouped)

# 合併所有年度資料
final_df = pd.concat(all_years_combined, ignore_index=True)
final_df['ID1_CITY'] = final_df['ID1_CITY'].astype(str).str.zfill(4)

# 輸出成 CSV
final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f'已成功匯出至：{output_csv}')
