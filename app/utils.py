import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import seaborn as sns

# 視聴タイプ
TYPE_ONA   = "ONA"
TYPE_MOVIE = "Movie"
TYPE_TV    = "TV"

# 表示するユーザの人数
N_USERS = 50

type_list = [TYPE_TV, TYPE_ONA, TYPE_MOVIE]

class AnimeRecommend:
    def __init__(self):
        # データをロード
        self.load_pickel()
        
        # 検索条件の辞書を初期化
        self.search_dict = {
            "titles": [],
            "genres": [],
            "genres_or": False,
            "min_average_rating": self.df_user["ユーザー評価点"].min(),
            "max_average_rating": self.df_user["ユーザー評価点"].max(),
            "min_menber_count": self.df_anime["メンバー数"].min(),
            "max_menber_count": self.df_anime["メンバー数"].max(),
        }

    def load_data(self):

        # ユーザー評価の情報
        self.df_user = pd.read_csv("dataset/rating.csv", encoding='utf_8_sig')
        self.df_user.rename(columns={"user_id":"ユーザーID", "anime_id":"作品番号", "rating":"ユーザー評価点"}, inplace=True)

        # 作品の情報
        self.df_anime  = pd.read_csv("dataset/anime.csv", encoding='utf_8_sig')
        self.df_anime.rename(columns={"anime_id":"作品番号", "name":"タイトル", "genre":"ジャンル", "type":"視聴タイプ", 
                                "episodes":"エピソード", "rating":"平均評価点", "members":"メンバー数"}, inplace=True)
        #df_anime.set_index("作品番号", inplace=True)

        self.rows, self.columns = self.df_anime.shape

        # return self.df_user, self.df_anime, self.rows, self.columns
    
    # def select_type(self):

    #     self.anime_type = st.selectbox("アニメの視聴タイプを選択(おすすめ: TV)", type_list)
    #     self.df_anime_byType = self.df_anime[self.df_anime["視聴タイプ"]==self.anime_type]
    #     # データフレーム結合
    #     self.df_user_byType = pd.merge(self.df_user,self.df_anime_byType,on="作品番号")
    #     #欠損値があるデータ以外を抽出
    #     self.df_user_byType = self.df_user_byType[self.df_user_byType["ユーザー評価点"] != -1]

    #     # サンプル数の制限
    #     sample = st.number_input("サンプル数制限", min_value=10000, max_value=7813737, value=7813737)
    #     if(len(self.df_user_byType) > sample):
    #         self.df_user_byType = self.df_user_byType.sample(n=sample, random_state=0)
        

    def create_coss_table(self):
        # クロス集計の作成
        self.df_user_anime = self.df_user_byType.pivot_table(index   = "ユーザーID",      # 行方向
                                                columns = "作品番号",        # 列方向
                                                values  = "ユーザー評価点",) # セルに入る値


        # ユーザーの選抜（Y作品以上評価点を付けているユーザー）
        self.cnt_rating     = self.df_user_anime.T.count()                      # カウント
        self.cnt_rating_id  = self.cnt_rating[self.cnt_rating >= 10].index.to_list() # 10作品数以上評価点を付けているユーザーのIDのリスト

        self.df_user_anime  = self.df_user_anime.loc[self.cnt_rating_id, :]

        # 作品の選抜(X人以上が評価点を付けている作品)
        self.cnt_user      = self.df_user_anime.count()                          # カウント
        self.cnt_user_id   = self.cnt_user[self.cnt_user >= 10].index.to_list()       # 10人以上が評価点を付けている作品
        self.df_user_anime = self.df_user_anime[self.cnt_user_id]

        #欠損値(評価なし映画)に0を代入
        self.df_user_anime = self.df_user_anime.fillna(0)

    def calc_cos_sim(self):
        # データフレームが空でないことを確認
        if not self.df_user_anime.empty:
            # コサイン類似度の計算
            self.user_user_sim = cosine_similarity(csr_matrix(self.df_user_anime))
            # データフレームに挿入
            self.df_sim = pd.DataFrame(self.user_user_sim,
                                index   = self.df_user_anime.index,
                                columns = self.df_user_anime.index)
        else:
            print("データが不足しているため、類似度の計算をスキップします。")

    def select_user(self):
        st.write(f"対象ユーザ数：{len(sorted(list(self.df_user_anime.index)))}")
        self.target_user_id = st.selectbox("ユーザを選択", (sorted(list(self.df_user_anime.index))))

        # 対象ユーザーが既に見た作品の抽出（元データのdf_user_byTypeを使用）
        self.df_watched_byTarget = self.df_user_byType[self.df_user_byType["ユーザーID"]==self.target_user_id].sort_values(by=["ユーザー評価点","作品番号"], ascending=[False,True])

        # 表示（特定の列の値に基づいてセルを色付け）
        cmap = 'YlGnBu'  # カラーマップの選択（他にも多くのカラーマップが利用可能）
        st.dataframe(self.df_watched_byTarget.style.background_gradient(cmap=cmap, axis=None, subset=['ユーザー評価点']),
                     hide_index=True)

    def extract_users_similarity(self):
        # 類似度の高い上位XのユーザーIDを取得
        self.topX_user    = 10 # 上位X人
        self.sim_users    = self.df_sim[self.target_user_id].sort_values(ascending=False)[1:self.topX_user+1]
        self.df_sim_users = pd.DataFrame(self.sim_users) # シリーズ→データフレーム
        self.df_sim_users.columns = ['類似度']      # 列名変更

        # 高類似度ユーザーの類似度と評価値を結合
        self.df_user_anime_sim = pd.merge(self.df_sim_users,self.df_user_anime,how="left",left_index=True, right_index=True)
        #display(df_user_anime_sim)

        # 高類似度ユーザーの評価値を更新（おすすめ度=類似度×評価点）
        for i in self.df_user_anime_sim.columns.to_list():
            if i == "類似度":
                continue
            self.df_user_anime_sim[i]  = self.df_user_anime_sim["類似度"]*self.df_user_anime_sim[i]       # おすすめ度=評価点×類似度
            self.average_without_zeros = self.df_user_anime_sim[i][self.df_user_anime_sim[i] != 0].mean() # 0以外の値の平均値
            self.df_user_anime_sim.loc['おすすめ度',i] = self.average_without_zeros                  # おすすめ行を追加

    def display_recomend_anime(self):
        # 類似ユーザーの作品リストから対象ユーザーが既に評価した作品リストを除外
        self.sim_cols    = self.df_user_anime_sim.drop(columns=["類似度"]).columns.to_list() # 類似ユーザーの作品リスト
        self.target_cols = self.df_watched_byTarget["作品番号"].to_list()                    # 対象ユーザーが既に評価した作品リスト
        self.diff_cols   = sorted(set(self.sim_cols) - set(self.target_cols))                     # 除外後の作品リスト

        # おすすめ集計
        self.topX_recommend = 10  # おすすめ上位X個の指定
        self.df_recommend   = self.df_user_anime_sim[self.diff_cols]                   # 対象ユーザーが既に評価している作品を除外
        self.df_recommend   = pd.DataFrame(self.df_recommend.loc["おすすめ度",:]) # おすすめ度抽出（シリーズ→データフレーム）         
        self.df_recommend   = self.df_recommend.sort_values(by="おすすめ度", ascending=False).head(self.topX_recommend) # おすすめ上位X個を抽出 
        self.df_recommend   = pd.merge(self.df_recommend,self.df_anime,how="left",left_index=True,right_on="作品番号")  # 映画情報と結合
        self.df_recommend.index = range(1, len(self.df_recommend) + 1) # インデックスを順位に設定
        self.df_recommend.index.name = "順位"                     # インデックス名を付ける

        cmap = 'YlGnBu'  # カラーマップの選択（他にも多くのカラーマップが利用可能）
        st.write(self.df_recommend.style.background_gradient(cmap=cmap, axis=None, subset=['おすすめ度']))
        
    def analyze_system(self):
        self.create_coss_table()
        self.calc_cos_sim()

    def load_pickel(self):
        self.dataframes = pd.read_pickle("dataframes.pickle")
        self.df_user = self.dataframes['df_user']
        self.df_anime = self.dataframes['df_anime']
        # 今回はTVのみを対象とする
        self.df_anime = self.df_anime[self.df_anime["視聴タイプ"]=="TV"]
        # ジャンルリストを作成
        self.genres = []
        for i in self.df_anime["ジャンル"].dropna().unique():
            self.genres.extend([g for g in i.split(", ") if g not in self.genres])
        self.df_user_byType = self.dataframes['df_user_byType']
        self.df_user_anime = self.dataframes['df_user_anime']
        self.df_sim = self.dataframes['df_sim']
        
    def display_anime(self):
        with st.spinner("指定条件でアニメを絞り込み中 ...."):
            self.df_filtered_anime = self.filter_anime()
            with st.expander("アニメの絞り込み結果を確認（クリック）"):
                st.dataframe(self.df_filtered_anime, hide_index=True)
    
    def filter_anime(self):
        filtered_df = self.df_anime.copy()
        
        titles = self.search_dict["titles"]
        genres = self.search_dict["genres"]
        genres_or = self.search_dict["genres_or"]
        min_average_rating = self.search_dict["min_average_rating"]
        max_average_rating = self.search_dict["max_average_rating"]
        min_menber_count = self.search_dict["min_menber_count"]
        max_menber_count = self.search_dict["max_menber_count"]
        
        # タイトルで絞り込み
        if len(titles) > 0:
            filtered_df = filtered_df[filtered_df["タイトル"].isin(titles)]
            # filtered_df = filtered_df[(filtered_df["タイトル"].isin([titles]))]
        filtered_df = self.match_genre(filtered_df, genres, is_or=genres_or)
        filtered_df = filtered_df[filtered_df["平均評価点"].between(min_average_rating, max_average_rating)]
        filtered_df = filtered_df[filtered_df["メンバー数"].between(min_menber_count, max_menber_count)]
        
        self.df_filtered_anime = filtered_df
        return filtered_df
        
    def match_genre(self, df, target_genre, is_or=False):
        """ジャンルが一致するかどうかを判定する関数（通常ではAND検索）"""
        if len(target_genre)==0:
            return df
        df = df.dropna(subset=["ジャンル"])
        if is_or:
            filtered_df = df[[any([g in target_genre for g in row.split(", ")]) for row in df["ジャンル"]]]
        else:
            filtered_df = df[[sum([g in row.split(", ") for g in target_genre])==len(target_genre) for row in df["ジャンル"]]]
        return filtered_df
    
    # def match_genre(self, df, genre, is_or=False):
    #     df_filt_origin = df.copy()
    #     target_genre = df_filt_origin['ジャンル']

    #     if is_or:
    #         filtered_df = df_filt_origin[[any(g in row.split(", ") for g in genre) for row in target_genre]]
    #     else:
    #         filtered_df = df_filt_origin[[all(g in row.split(", ") for g in genre) for row in target_genre]]

    #     return filtered_df
    
    def display_user(self, n_users=N_USERS):
        with st.spinner("指定条件でユーザーを絞り込み中 ...."):
            self.df_filtered_users = self.filter_user().drop(["視聴タイプ", "エピソード"], axis=1)
            # st.write(len(self.df_filtered))
            with st.expander("ユーザー情報を確認（クリック）"):
                st.write(f"ユーザー数：{len(self.df_filtered_users)}")
                try:
                    # self.df_filtered = self.filter_user().drop(["視聴タイプ", "エピソード"], axis=1)
                    st.dataframe(self.df_filtered_users.head(n_users), hide_index=True)
                except Exception as e:
                    st.error("量が多すぎるので絞り込んでアニメ数を減らしてください")
                    # st.dataframe(self.df_filtered, hide_index=True)
            
    def filter_user(self):
        filtered_users = self.df_user_byType[self.df_user_byType['作品番号'].isin(
            self.df_filtered_anime['作品番号'])].sort_values(
                by=['ユーザーID','ユーザー評価点'], ascending=[True, False])
        # self.df_filtered_users = filtered_users
        return filtered_users
    
    def display_input_search_request(self):
        with st.expander("アニメの検索条件を設定"):
            # タイトルの選択
            self.search_dict["titles"] = st.multiselect("タイトルで絞込み", self.df_anime["タイトル"].dropna().unique())
            
            # ジャンルの選択
            cols = st.columns([8,2])
            with cols[0]:
                self.search_dict["genres"] = st.multiselect("ジャンルで絞込み", self.genres)
            with cols[1]:
                self.search_dict["genres_or"] = st.checkbox("OR検索（通常はAND検索になる）", value=False)
                
            min_average_rating = self.df_user["ユーザー評価点"].min()
            max_average_rating = self.df_user["ユーザー評価点"].max()
            min_menber_count = self.df_anime["メンバー数"].min()
            max_menber_count = self.df_anime["メンバー数"].max()
            
            self.search_dict["min_average_rating"], self.search_dict["max_average_rating"] = \
                st.slider("評価点", min_average_rating, max_average_rating, (min_average_rating, max_average_rating))
                
            self.search_dict["min_menber_count"], self.search_dict["max_menber_count"] = \
                st.slider("メンバー数", min_menber_count, max_menber_count, (min_menber_count, max_menber_count))