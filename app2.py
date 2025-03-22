import streamlit as st
import mysql.connector
import folium
from streamlit_folium import st_folium

st.title("🗺️ 地図型思い出日記")
st.caption("地図の中央にピンを立てて、その場所に思い出を記録しよう！!!!")

memo_title = st.text_input("思い出のタイトルを入力", "思い出の場所")
memo = st.text_area("✏️ 思い出メモを書く", "")

# 地図初期表示（福岡）
initial_lat, initial_lng = 33.5902, 130.4017
m = folium.Map(location=[initial_lat, initial_lng], zoom_start=12)
folium.Marker(
    [initial_lat, initial_lng],
    popup=memo_title,
    draggable=True
).add_to(m)
map_data = st_folium(m, width=700, height=500)

# 緯度経度を変数に
lat, lng = initial_lat, initial_lng
if map_data and map_data["last_object_clicked"]:
    lat = map_data["last_object_clicked"]["lat"]
    lng = map_data["last_object_clicked"]["lng"]

# 登録ボタンを押したときの処理
if st.button("✅ 登録"):
    try:
        # ✅ secrets.toml から安全に接続情報を取得
        db_config = st.secrets["mysql"]

        # ✅ MySQLに接続
        conn = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        cursor = conn.cursor()

        # ✅ INSERTクエリでデータ保存
        cursor.execute(
            "INSERT INTO memories (title, memo, latitude, longitude) VALUES (%s, %s, %s, %s)",
            (memo_title, memo, lat, lng)
        )
        conn.commit()
        st.success("🎉 思い出を保存しました！")

    except mysql.connector.Error as e:
        st.error(f"MySQLエラー: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

import pandas as pd

# データベース接続（secrets.toml から取得）
db_config = st.secrets["mysql"]

try:
    conn = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )
    cursor = conn.cursor(dictionary=True)  # ← dict形式で取得するのがポイント！

    # SQLで全件取得（新しい順）
    cursor.execute("SELECT title, memo, latitude, longitude, created_at FROM memories ORDER BY created_at DESC")
    results = cursor.fetchall()

    # pandasで整形（表示しやすく）
    if results:
        df = pd.DataFrame(results)
        st.markdown("### 📝 登録済みの思い出一覧")
        st.dataframe(df)
    else:
        st.info("まだ登録された思い出はありません。")

except mysql.connector.Error as e:
    st.error(f"MySQLエラー（一覧取得）: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
