import pandas as pd

def load_data():
    df_user = pd.read_csv("dataset/rating.csv", encoding='utf_8_sig')
    df_user.rename(columns={"user_id": "ユーザーID", "anime_id": "作品番号", "rating": "ユーザー評価点"}, inplace=True)

    df_anime = pd.read_csv("dataset/anime.csv", encoding='utf_8_sig')
    df_anime.rename(columns={"anime_id": "作品番号", "name": "タイトル", "genre": "ジャンル", "type": "視聴タイプ",
                             "episodes": "エピソード", "rating": "平均評価点", "members": "メンバー数"}, inplace=True)

    return df_user, df_anime
