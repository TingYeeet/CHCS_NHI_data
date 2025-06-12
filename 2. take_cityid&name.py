import pandas as pd

# 輸入檔案路徑
excel_file = "./各鄉鎮在保人數分布/2016-2019 年各鄉鎮在保人數分布.xlsx"  # 替換為你的檔名

# 強制將 ID1_CITY 視為字串，如果 Excel 存成數字仍可能讀成 int
df = pd.read_excel(excel_file)

# 將 ID1_CITY 補滿4碼（確保開頭0存在）
df['ID1_CITY'] = df['ID1_CITY'].astype(str).str.zfill(4)

# 去除重複並排序
result = df[['ID1_CITY', 'C_NAME']].drop_duplicates().sort_values(by='ID1_CITY')
print(result)

# 輸出成 CSV
result.to_csv("ID_CNAME.csv", index=False, encoding="utf-8-sig")

print("✅ 輸出完成：ID_CNAME.csv")
