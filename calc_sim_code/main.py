from data_loader import load_data
from exploratory_analysis import exploratory_analysis
from recommendation_system import build_recommendation_system
from utils import save_dataframes

def main():
    # データの読み込み
    df_user, df_anime = load_data()

    # 探索的分析
    exploratory_analysis(df_anime)

    # レコメンドシステムの構築
    df_user_anime, df_sim = build_recommendation_system(df_user, df_anime)

    # データの保存
    dataframes = {
        'df_user': df_user,
        'df_anime': df_anime,
        'df_user_anime': df_user_anime,
        'df_sim': df_sim
    }
    save_dataframes(dataframes, output_file="../dataframes.pickle")

if __name__ == "__main__":
    main()
