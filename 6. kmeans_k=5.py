import pandas as pd
import os
from sklearn.cluster import KMeans
import numpy as np

input_folder = "補值後CSV"
output_folder = "分群結果"
os.makedirs(output_folder, exist_ok=True)

# 遍歷每個疾病檔案
for filename in os.listdir(input_folder):
    if not filename.endswith(".csv"):
        continue

    df = pd.read_csv(os.path.join(input_folder, filename), dtype={'ID1_CITY': str})

    # 只保留必要欄位
    df = df[['ID1_CITY', 'year', 'week', 'case_c']]

    # 分群結果暫存器
    all_assignments = []
    all_summary = []

    # 以 groupby('year') 遍歷每年
    for year, group in df.groupby('year'):
        # 建立 53 維向量資料（先不轉進 pivot）
        week_counts = group.groupby('ID1_CITY')['week'].nunique()
        full_ids = week_counts[week_counts == 53].index
        partial_ids = week_counts[week_counts < 53].index

        if len(full_ids) == 0:
            print(f"⚠️ {filename} 的 {year} 沒有任何地區滿 53 週，全部歸 cluster 6")
            # 整年都歸類 cluster 6
            cluster_df = pd.DataFrame({
                'city_id': partial_ids,
                'cluster': 6,
                'year': year
            })
            all_assignments.append(cluster_df)

            summary = pd.DataFrame({
                'cluster': [6],
                '地區數量': [len(partial_ids)],
                '地區列表': [','.join(partial_ids)],
                '就醫人數年平均': [group[group['ID1_CITY'].isin(partial_ids)].groupby('ID1_CITY')['case_c'].mean().mean()],
                'year': [year]
            })
            all_summary.append(summary)
            continue

        # ➤ 執行分群前先建立 pivot 資料（只針對滿 53 週的地區）
        pivot = group[group['ID1_CITY'].isin(full_ids)].pivot_table(
            index='ID1_CITY', columns='week', values='case_c', fill_value=0
        )

        # ➤ 執行 KMeans
        kmeans = KMeans(n_clusters=5, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(pivot)

        # ➤ 地區分群結果
        cluster_df = pd.DataFrame({
            'city_id': pivot.index,
            'cluster': cluster_labels,
            'year': year
        })

        # ➤ 若有部分資料缺週，補上 cluster = 6
        if len(partial_ids) > 0:
            print(f"⚠️ {filename} 中以下 city_id 在 {year} 年週數不足 53 週，歸為 cluster 6：{', '.join(partial_ids)}")
            partial_df = pd.DataFrame({
                'city_id': partial_ids,
                'cluster': 6,
                'year': year
            })
            cluster_df = pd.concat([cluster_df, partial_df], ignore_index=True)

        all_assignments.append(cluster_df)

        # ➤ 群組摘要
        summary = (
            cluster_df
            .groupby('cluster')['city_id']
            .agg(['count', lambda x: ','.join(x)])
            .rename(columns={'count': '地區數量', '<lambda_0>': '地區列表'})
            .reset_index()
        )

        # ➤ 加上就醫人數年平均（僅 cluster ≠ 6 的平均來自 pivot）
        pivot['cluster'] = cluster_labels
        pivot['avg'] = pivot.drop(columns='cluster').mean(axis=1)
        avg_summary = pivot.groupby('cluster')['avg'].mean().reset_index(name='就醫人數年平均')

        # ➤ cluster 6 的補法（取 group 裡 partial_ids 的平均）
        if len(partial_ids) > 0:
            c6_avg = group[group['ID1_CITY'].isin(partial_ids)].groupby('ID1_CITY')['case_c'].mean().mean()
            avg_summary = pd.concat([
                avg_summary,
                pd.DataFrame({'cluster': [6], '就醫人數年平均': [c6_avg]})
            ], ignore_index=True)

        # ➤ 重新排序 cluster（0~4）根據年平均，最高為 0，最低為 4
        valid_clusters = avg_summary[avg_summary['cluster'] != 6]
        sorted_clusters = valid_clusters.sort_values('就醫人數年平均', ascending=False).reset_index(drop=True)
        cluster_remap = {old: new for new, old in enumerate(sorted_clusters['cluster'])}

        # ➤ 保留 cluster 6 不變
        cluster_remap[6] = 6

        # ➤ 套用到 cluster_df 與 avg_summary、summary
        cluster_df['cluster'] = cluster_df['cluster'].map(cluster_remap)
        avg_summary['cluster'] = avg_summary['cluster'].map(cluster_remap)
        summary['cluster'] = summary['cluster'].map(cluster_remap)

        merged_summary = pd.merge(summary, avg_summary, on='cluster')
        merged_summary['year'] = year
        merged_summary = merged_summary.sort_values(by='cluster').reset_index(drop=True)
        all_summary.append(merged_summary)

    # 匯出檔案 1（每筆分群）
    full_assign_df = pd.concat(all_assignments, ignore_index=True)
    assign_path = os.path.join(output_folder, f"{filename.replace('.csv', '')}_分群地區.csv")
    full_assign_df.to_csv(assign_path, index=False, encoding='utf-8-sig')

    # 匯出檔案 2（群組摘要）
    full_summary_df = pd.concat(all_summary, ignore_index=True)
    summary_path = os.path.join(output_folder, f"{filename.replace('.csv', '')}_分群摘要.csv")
    full_summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')

    print(f"✅ 已完成分群：{filename}")
