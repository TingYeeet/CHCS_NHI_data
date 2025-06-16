import pandas as pd
import os

# PM2.5 檔案路徑
pm25_path = "PM25_monthly_by_region.csv"
pm25_df = pd.read_csv(pm25_path)

# 疾病資料夾路徑
case_folder = "月就醫比例(五群)"  # 修改為你的實際資料夾名稱
output_folder = "就診千分比對pm2.5(五群)"
os.makedirs(output_folder, exist_ok=True)

# 處理每個疾病檔案
for filename in os.listdir(case_folder):
    if not filename.endswith(".csv"):
        continue

    case_path = os.path.join(case_folder, filename)
    case_df = pd.read_csv(case_path)

    # 合併 PM2.5
    merged = pd.merge(case_df, pm25_df, on=["region", "year", "month"], how="left")

    # 保留必要欄位
    output_df = merged[["region", "year", "month", "case_per_capita(‰)", "PM2.5"]]

    # 輸出檔案
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_with_PM25.csv")
    output_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"✅ 已輸出：{output_path}")
