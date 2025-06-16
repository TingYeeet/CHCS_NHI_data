import pandas as pd
import os

# 地區群組定義：依據 ID1_CITY 前兩碼對應縣市
region_groups = {
    '北北基桃竹苗': ['01', '31', '11', '32', '33', '35'],   # 台北、新北、基隆、桃園、新竹、苗栗
    '中彰投':     ['03', '37', '38'],                      # 台中、彰化、南投
    '雲嘉南':     ['39', '40', '05'],                      # 雲林、嘉義、台南
    '高屏':       ['07', '43'],                            # 高雄、屏東
    '宜花東':     ['34', '45', '46']                       # 宜蘭、花蓮、台東
}

# 反向映射：ID1_CITY 前兩碼 → 地區名稱
city_to_region = {}
for region, prefixes in region_groups.items():
    for prefix in prefixes:
        city_to_region[prefix] = region

# 資料夾與路徑設定
input_folder = "月-呼吸道疾病就醫人數-移除外島"
output_folder = "月就醫比例(五群)"
pop_csv_path = "./各鄉鎮在保人數分布/total_population_2016_2019.csv"

# 建立輸出資料夾
os.makedirs(output_folder, exist_ok=True)

# 讀取人口總表並加入 region 欄位
pop_df = pd.read_csv(pop_csv_path, dtype={'ID1_CITY': str})
pop_df["region"] = pop_df["ID1_CITY"].str[:2].map(city_to_region)
pop_df = pop_df.rename(columns={"total_pop": "pop_total"})

# 處理每個 CSV 檔
for filename in os.listdir(input_folder):
    if not filename.endswith(".csv"):
        continue

    filepath = os.path.join(input_folder, filename)
    df = pd.read_csv(filepath, dtype={'ID1_CITY': str})

    # 合併人口與區域資料
    merged = pd.merge(df, pop_df, on=["ID1_CITY", "year"], how="left")

    # 確保沒有合併錯誤
    if merged["region"].isnull().any():
        print(f"⚠️ {filename} 中有未對應的城市代碼")

    # 各區每月總病例數與總人口
    grouped = merged.groupby(["region", "year", "month"]).agg({
        "case_c": "sum",
        "pop_total": "sum"
    }).reset_index()

    # 計算每千人病例比例
    grouped["case_per_capita(‰)"] = (grouped["case_c"] / grouped["pop_total"] * 1000).round(3)

    # 輸出
    output_path = os.path.join(output_folder, filename)
    grouped.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 已處理並輸出：{output_path}")