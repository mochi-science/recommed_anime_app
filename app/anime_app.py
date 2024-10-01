import streamlit as st
from utils import AnimeRecommend

st.write("# アニメおすすめアプリ")

if "client" not in st.session_state:
    with st.spinner("データをロード中 ...."):
        ar_client = AnimeRecommend()
        st.session_state["client"] = ar_client
else:
    ar_client = st.session_state["client"]
    
ar_client.display_input_search_request()
ar_client.display_anime()
ar_client.display_user()

if "client" in st.session_state:
    ar_client.select_user()
    if st.button("おすすめを表示する"):
        ar_client.extract_users_similarity()
        ar_client.display_recomend_anime()
