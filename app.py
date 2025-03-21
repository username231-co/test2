import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🗺️ 地図型思い出日記")
st.caption("地図の中央にピンを立てて、その場所に思い出を記録しよう！")

# メモのタイトルを入力できるようにする
memo_title = st.text_input("思い出のタイトルを入力", "思い出の場所")

# 初期の位置（福岡）の地図を作成
m = folium.Map(location=[33.5902, 130.4017], zoom_start=12)

# ピンを立て、タイトルを設定
pin = folium.Marker(
    [33.5902, 130.4017],  # 初期位置の緯度・経度
    popup=memo_title,  # ピンをクリックしたときに表示されるタイトル
    draggable=True  # ピンをドラッグ可能にする
).add_to(m)

# 地図を表示
map_data = st_folium(m, width=700, height=500)

# メモを書くエリア
memo = st.text_area("✏️ 思い出メモを書く", "")

# メモを保存するボタン
if st.button("✅ 登録"):
    st.success(f"思い出を保存しました！\nタイトル: {memo_title}\n場所: 緯度 {33.5902}, 経度 {130.4017}\nメモ: {memo}")
