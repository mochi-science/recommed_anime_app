import matplotlib.pyplot as plt
import japanize_matplotlib

def exploratory_analysis(df_anime):
    # サブプロットを作成
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # 視聴タイプ別の作品数
    anime_types = df_anime["視聴タイプ"].value_counts()
    x = ["TV", "OVA", "Movie", "Special", "ONA", "Music"]
    y = anime_types[x]
    axes[0].bar(x, y)
    axes[0].set_title("視聴タイプ別の作品数", fontsize=20)
    axes[0].set_xlabel("視聴タイプ", fontsize=15)
    axes[0].set_ylabel("作品数", fontsize=15)
    axes[0].tick_params(axis="x", labelsize=15)
    axes[0].tick_params(axis="y", labelsize=15)
    axes[0].grid(axis="y")

    # 視聴タイプ別の平均評価点
    type_mean = df_anime.groupby("視聴タイプ")["平均評価点"].mean()
    y = type_mean[x]
    axes[1].bar(x, y)
    axes[1].set_title("視聴タイプ別の平均評価点", fontsize=20)
    axes[1].set_xlabel("視聴タイプ", fontsize=15)
    axes[1].set_ylabel("平均評価点", fontsize=15)
    axes[1].tick_params(axis="x", labelsize=15)
    axes[1].tick_params(axis="y", labelsize=15)
    axes[1].grid(axis="y")

    plt.tight_layout()
    plt.show()
