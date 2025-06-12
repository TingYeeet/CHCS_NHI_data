import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# === 1. 讀取 GML 邊界檔 ===
gml_path = "TOWN_MOI_1131028.gml"
gdf = gpd.read_file(gml_path, encoding='utf-8')
gdf['名稱_clean'] = gdf['名稱'].str.replace("　", "").str.strip()

# === 2. 讀取 ID-C_NAME 對照表 ===
code_map = pd.read_csv("ID_CNAME.csv", dtype={'ID1_CITY': str})
code_map['C_NAME_clean'] = code_map['C_NAME'].str.replace("　", "").str.strip()

# === 3. 合併 GML 與地名對照 ===
gdf = gdf.merge(code_map[['ID1_CITY', 'C_NAME_clean']], 
                left_on='名稱_clean', right_on='C_NAME_clean', how='left')

# === 4. 移除離島地區（澎湖、金門、馬祖、綠島、蘭嶼） ===
# 額外使用地名關鍵字過濾離島
exclude_keywords = ['澎湖', '金門', '連江', '綠島', '蘭嶼', '琉球', '東沙', '南沙']

def is_main_island(row):
    city = row.get('ID1_CITY', '')
    name = row.get('名稱', '')

    # 安全地檢查 city
    if isinstance(city, str):
        if city.startswith('44') or city in ['4611', '4616']:
            return False

    # 安全地檢查地名是否包含離島關鍵字
    if isinstance(name, str) and any(kw in name for kw in exclude_keywords):
        return False

    return True

gdf = gdf[gdf.apply(is_main_island, axis=1)]

# === 5. 設定分群結果與輸出資料夾 ===
cluster_folder = "分群結果"
output_folder = "分群地圖"
os.makedirs(output_folder, exist_ok=True)

# === 6. 遍歷分群檔案並畫圖 ===
for filename in os.listdir(cluster_folder):
    if not filename.endswith("_分群地區.csv"):
        continue

    cluster_df = pd.read_csv(os.path.join(cluster_folder, filename), dtype={'city_id': str})

    # 合併地名
    cluster_df = cluster_df.merge(code_map, left_on='city_id', right_on='ID1_CITY', how='left')
    cluster_df['C_NAME_clean'] = cluster_df['C_NAME'].astype(str).str.replace("　", "").str.strip()

    for year, year_df in cluster_df.groupby('year'):
        year_df = year_df.copy()

        # === 1st 合併：直接名稱合併 ===
        merged = gdf.merge(year_df[['C_NAME_clean', 'cluster']], on='C_NAME_clean', how='left')

        # 群組對應色碼（手動定義）
        cluster_colors = {
            0: "#AA04AA",  # 紫
            1: '#FF0000',  # 紅
            2: '#FFA500',  # 橘
            3: '#FFFF00',  # 黃
            4: "#23B623",  # 綠
            6: '#A9A9A9'   # 深灰（缺週數）
        }

        # 加入顏色欄位，NaN 給淺灰
        merged['color'] = merged['cluster'].map(cluster_colors).fillna('#D3D3D3')

        # 畫圖
        fig, ax = plt.subplots(figsize=(10, 12))
        merged.plot(
            color=merged['color'],
            linewidth=0.2,
            edgecolor='black',
            ax=ax,
            legend=False
        )

        # === 手動圖例 ===
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor=cluster_colors[0], edgecolor='black', label='Cluster 0'),
            Patch(facecolor=cluster_colors[1], edgecolor='black', label='Cluster 1'),
            Patch(facecolor=cluster_colors[2], edgecolor='black', label='Cluster 2'),
            Patch(facecolor=cluster_colors[3], edgecolor='black', label='Cluster 3'),
            Patch(facecolor=cluster_colors[4], edgecolor='black', label='Cluster 4'),
            Patch(facecolor=cluster_colors[6], edgecolor='black', label='Cluster 6 (缺週數)'),
            Patch(facecolor='#D3D3D3', edgecolor='black', label='未對應地名')  # NaN 對應失敗
        ]

        ax.legend(handles=legend_elements, title="群組", loc='lower left')

        # 聚焦台灣本島
        ax.set_xlim(119.3, 122.2)
        ax.set_ylim(21.7, 25.4)

        # 標題與儲存
        disease_name = filename.replace("_分群地區.csv", "")
        ax.set_title(f"{disease_name} - {year} 年分群地圖", fontsize=16)
        ax.axis('off')

        out_path = os.path.join(output_folder, f"{disease_name}_{year}_cluster_map.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ 已輸出地圖：{out_path}")

