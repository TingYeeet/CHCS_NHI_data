import pandas as pd
import os

input_folder = "周-呼吸道疾病就醫人-移除外島"
missing_info_path = "少週數的.csv"
output_folder = "補值後CSV"
os.makedirs(output_folder, exist_ok=True)

# 讀取少週數的條目
missing_df = pd.read_csv(missing_info_path, dtype={'ID1_CITY': str})
missing_df = missing_df[(missing_df['week_count'] >= 27) & (missing_df['week_count'] < 53)]

# 依 source_file 群組
for filename, group in missing_df.groupby("source_file"):
    filepath = os.path.join(input_folder, filename)
    df = pd.read_csv(filepath, dtype={'ID1_CITY': str})

    # 對該檔案中所有需要補值的 ID1_CITY + year 做補值
    for _, row in group.iterrows():
        city = row['ID1_CITY']
        year = row['year']

        subset = df[(df['ID1_CITY'] == city) & (df['year'] == year)]

        # 建立完整週數表
        full_weeks = pd.DataFrame({'week': list(range(1, 54))})
        full_weeks['ID1_CITY'] = city
        full_weeks['year'] = year

        # 合併現有資料
        merged = pd.merge(full_weeks, subset, on=['ID1_CITY', 'year', 'week'], how='left')

        # 補值
        merged['case_c'] = (
            merged['case_c']
            .astype(float)
            .interpolate(method='linear', limit_direction='both')
            .fillna(method='ffill')  # ← 如果中間內插不到，就往前補
            .fillna(method='bfill')  # ← 如果一開始都缺，就往後補
            .round()
            .astype('Int64')
        )

        # 補上其他欄位（若存在）
        other_cols = [col for col in df.columns if col not in ['ID1_CITY', 'year', 'week', 'case_c']]
        for col in other_cols:
            if col not in merged.columns:
                merged[col] = None

        # 移除原資料中該城市該年的舊資料
        df = df[~((df['ID1_CITY'] == city) & (df['year'] == year))]

        # 插入補值後資料
        df = pd.concat([df, merged[df.columns]], ignore_index=True)

        print(f'{city} {year} 補值完成')

    # 輸出檔案
    output_path = os.path.join(output_folder, filename)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 補值完成並輸出：{output_path}")
