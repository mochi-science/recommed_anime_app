import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

def build_recommendation_system(df_user, df_anime, anime_type="TV"):
    df_anime_byType = df_anime[df_anime["視聴タイプ"] == anime_type]
    df_user_byType = pd.merge(df_user, df_anime_byType, on="作品番号")
    df_user_byType = df_user_byType[df_user_byType["ユーザー評価点"] != -1]

    sample = 7813737
    if len(df_user_byType) > sample:
        df_user_byType = df_user_byType.sample(n=sample, random_state=0)

    df_user_anime = df_user_byType.pivot_table(index="ユーザーID", columns="作品番号", values="ユーザー評価点")
    cnt_rating = df_user_anime.T.count()
    cnt_rating_id = cnt_rating[cnt_rating >= 10].index.to_list()
    df_user_anime = df_user_anime.loc[cnt_rating_id, :]

    cnt_user = df_user_anime.count()
    cnt_user_id = cnt_user[cnt_user >= 10].index.to_list()
    df_user_anime = df_user_anime[cnt_user_id]
    df_user_anime = df_user_anime.fillna(0)

    print("コサイン類似度の計算中...（かなり時間かかります）")
    user_user_sim = cosine_similarity(csr_matrix(df_user_anime))
    print("コサイン類似度の計算完了")
    df_sim = pd.DataFrame(user_user_sim, index=df_user_anime.index, columns=df_user_anime.index)

    return df_user_anime, df_sim
