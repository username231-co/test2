import streamlit as st
import mysql.connector

# --- MySQL接続情報（あなたのRDS情報で書き換えてください） ---
db_config = {
    'host': 'your-rds-endpoint.rds.amazonaws.com',
    'user': 'admin',  # あなたのMySQLユーザー名
    'password': 'your-password',  # パスワード
    'database': 'memory_map'
}

# 登録ボタンが押されたら
if st.button("✅ 登録"):
    try:
        # データベース接続
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # ピンの位置やメモの情報を入力から取得（例）
        memo_title = st.session_state.get("memo_title", "タイトルなし")
        memo = st.session_state.get("memo", "")
        latitude = st.session_state.get("latitude", 33.5902)
        longitude = st.session_state.get("longitude", 130.4017)

        # SQLを実行して保存
        insert_query = """
            INSERT INTO memories (title, memo, latitude, longitude)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (memo_title, memo, latitude, longitude))
        conn.commit()

        st.success("🎉 思い出を保存しました！")

    except mysql.connector.Error as e:
        st.error(f"MySQL接続エラー: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
