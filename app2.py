import streamlit as st
import mysql.connector
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="地図型思い出日記", layout="centered")
st.title("🗺️ 地図型思い出日記")
st.caption("地図をクリックして、その場所に思い出を記録しよう！")

# 入力フォーム
memo_title = st.text_input("📌 思い出のタイトルを入力", "")
memo = st.text_area("📝 思い出メモを書く", "")

# --- 初期位置で地図作成（福岡） ---
initial_lat, initial_lng = 33.5902, 130.4017
m = folium.Map(location=[initial_lat, initial_lng], zoom_start=12)

# --- 保存済みピンを表示 ---
try:
    db = st.secrets["mysql"]
    conn = mysql.connector.connect(
        host=db["host"],
        user=db["user"],
        password=db["password"],
        database=db["database"]
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, memo, latitude, longitude FROM memories")
    results = cursor.fetchall()

    for row in results:
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"<b>{row['title']}</b><br>{row['memo']}",
            tooltip=row["title"],
            icon=folium.Icon(color="blue", icon="bookmark")
        ).add_to(m)

except mysql.connector.Error as e:
    st.error(f"MySQLエラー（保存済みピン）: {e}")
finally:
    if cursor: cursor.close()
    if conn: conn.close()

# --- 地図クリックの反応（ここで登録ピンを表示） ---
map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

lat, lng = None, None
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lng = map_data["last_clicked"]["lng"]

    # 💡 登録用ピンを同じマップに追加！
    folium.Marker(
        location=[lat, lng],
        popup="📍 登録予定の場所",
        icon=folium.Icon(color="red", icon="plus")
    ).add_to(m)

    # 再度マップ描画（登録ピンも反映された状態で）
    map_data = st_folium(m, width=700, height=500)
    st.success(f"📍 選択された座標：緯度 {lat:.5f}, 経度 {lng:.5f}")

else:
    # 初期描画（クリックされていないとき）
    st_folium(m, width=700, height=500)
    st.info("地図をクリックして思い出を登録する場所を選んでください。")

# --- 登録処理（ピンが選ばれていれば） ---
if lat and lng:
    if st.button("✅ この場所で思い出を登録"):
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (title, memo, latitude, longitude) VALUES (%s, %s, %s, %s)",
                (memo_title, memo, lat, lng)
            )
            conn.commit()
            st.success("🎉 思い出を登録しました！")

        except mysql.connector.Error as e:
            st.error(f"MySQLエラー（登録）: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

# --- 一覧表示セクション ---
st.markdown("---")
st.markdown("### 📖 登録済みの思い出一覧")

try:
    conn = mysql.connector.connect(
        host=db["host"],
        user=db["user"],
        password=db["password"],
        database=db["database"]
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, memo, latitude, longitude, created_at FROM memories ORDER BY created_at DESC")
    memories = cursor.fetchall()

    if memories:
        df = pd.DataFrame(memories)
        st.dataframe(df)
    else:
        st.info("まだ思い出は登録されていません。")

except mysql.connector.Error as e:
    st.error(f"MySQLエラー（一覧取得）: {e}")
finally:
    if cursor: cursor.close()
    if conn: conn.close()
