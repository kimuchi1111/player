import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_FILE = "player_database.db"

# データベース接続
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
    return conn

# テーブル作成 (初回のみ実行)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            dob TEXT NOT NULL,
            category TEXT NOT NULL,
            team TEXT NOT NULL,
            height INTEGER,
            weight INTEGER,
            speed INTEGER,
            technique INTEGER,
            physical INTEGER,
            mental INTEGER,
            notes TEXT,
            priority TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

# 年齢計算関数 (変更なし)
def calculate_age(birth_date):
    today = datetime.today()
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# データの取得
def load_players():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM players", conn)
    conn.close()
    return df.to_dict('records')

# 選手の追加
def add_player(name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO players (name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority))
    conn.commit()
    conn.close()
    st.success(f"✅ {name} を追加しました！")
    st.rerun()

# 選手の更新
def update_player(player_id, name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE players SET
            name = ?,
            position = ?,
            dob = ?,
            category = ?,
            team = ?,
            height = ?,
            weight = ?,
            speed = ?,
            technique = ?,
            physical = ?,
            mental = ?,
            notes = ?,
            priority = ?
        WHERE id = ?
    """, (name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority, player_id))
    conn.commit()
    conn.close()
    st.success(f"✅ {name} の情報を更新しました！")
    st.rerun()

# 選手の削除
def delete_player(player_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    st.success(f"❌ {name} を削除しました！")
    st.rerun()

# ページ構成 (大幅に変更)
st.sidebar.title("⚽️ メニュー")
page = st.sidebar.radio(
    "ページを選択してください",
    ["🏠 ホーム", "🔍 検索", "✏️ 編集・削除", "➕ 選手追加"]
)

# データの読み込み
players_df = pd.DataFrame(load_players())
players = players_df.to_dict('records')

# ================================
# 🏠 ホーム画面
# ================================
if page == "🏠 ホーム":
    st.title("🏠 選手一覧")
    if players_df.empty:
        st.warning("データがありません。選手を追加してください。")
    else:
        st.write("📋 **登録選手の一覧**")
        players_df['年齢'] = players_df['dob'].apply(calculate_age)
        st.dataframe(players_df[['name', 'position', '年齢', 'category', 'team', 'speed', 'technique', 'physical', 'mental', 'priority', 'height', 'weight', 'notes']], use_container_width=True)

# ================================
# 🔍 検索ページ
# ================================
elif page == "🔍 検索":
    st.title("🔍 選手の検索")

    position_filter = st.selectbox("ポジションで絞り込み", ["すべて", "GK", "DF", "MF", "FW"])
    category_filter = st.selectbox("カテゴリで絞り込み", ["すべて", "J1", "J2", "J3"])
    max_age_filter = st.number_input("最大年齢", min_value=15, max_value=40, value=25)
    min_speed_filter = st.slider("最低スピード", 1, 100, 50)

    filtered_df = players_df.copy()

    if position_filter != "すべて":
        filtered_df = filtered_df[filtered_df['position'] == position_filter]
    if category_filter != "すべて":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    filtered_df['年齢'] = filtered_df['dob'].apply(calculate_age)
    filtered_df = filtered_df[filtered_df['年齢'] <= max_age_filter]
    filtered_df = filtered_df[filtered_df['speed'] >= min_speed_filter]

    if filtered_df.empty:
        st.warning("条件に合う選手が見つかりません。")
    else:
        st.write("📋 **検索結果**")
        st.dataframe(filtered_df[['name', 'position', '年齢', 'category', 'team', 'speed', 'technique', 'physical', 'mental', 'priority', 'height', 'weight', 'notes']], use_container_width=True)

# ================================
# ✏️ 編集・削除ページ
# ================================
elif page == "✏️ 編集・削除":
    st.title("✏️ 選手の編集・削除")

    if players_df.empty:
        st.warning("選手データがありません。")
    else:
        selected_name = st.selectbox("編集・削除する選手を選択", players_df['name'].tolist())
        selected_player = players_df[players_df['name'] == selected_name].iloc[0]
        player_id = selected_player['id']

        st.write("✅ **選手情報の編集**")

        name = st.text_input("選手名", value=selected_player["name"])
        position = st.selectbox("ポジション", ["GK", "DF", "MF", "FW"], index=["GK", "DF", "MF", "FW"].index(selected_player["position"]))
        dob = st.date_input("生年月日", value=datetime.strptime(selected_player["dob"], "%Y-%m-%d"))
        category = st.selectbox("カテゴリ", ["J1", "J2", "J3"], index=["J1", "J2", "J3"].index(selected_player["category"]))
        team = st.text_input("所属チーム", value=selected_player["team"])

        st.subheader("スキル評価 (1-100)")
        speed = st.slider("スピード", 1, 100, selected_player["speed"])
        technique = st.slider("技術", 1, 100, selected_player["technique"])
        physical = st.slider("フィジカル", 1, 100, selected_player["physical"])
        mental = st.slider("メンタル", 1, 100, selected_player["mental"])

        height = st.number_input("身長 (cm)", min_value=100, max_value=250, value=selected_player["height"])
        weight = st.number_input("体重 (kg)", min_value=30, max_value=150, value=selected_player["weight"])
        notes = st.text_area("備考", value=selected_player["notes"])
        priority = st.selectbox("獲得希望度", ["◎", "◯", "△", "要チェック"], index=["◎", "◯", "△", "要チェック"].index(selected_player.get("priority", "要チェック")))

        if st.button("✅ 更新"):
            update_player(player_id, name, position, dob.strftime("%Y-%m-%d"), category, team, height, weight, speed, technique, physical, mental, notes, priority)

        if st.button("❌ 削除"):
            delete_player(player_id, selected_player['name'])

# ================================
# ➕ 選手追加ページ
# ================================
elif page == "➕ 選手追加":
    st.title("➕ 新規選手の追加")

    name = st.text_input("選手名を入力")
    position = st.selectbox("ポジションを選択", ["GK", "DF", "MF", "FW"])
    dob = st.date_input("生年月日 (YYYY-MM-DD)").strftime("%Y-%m-%d")
    category = st.selectbox("カテゴリを選択", ["J1", "J2", "J3"])
    team = st.text_input("所属チーム")

    st.subheader("スキル評価 (1-100)")
    speed = st.slider("スピード", 1, 100, 50)
    technique = st.slider("技術", 1, 100, 50)
    physical = st.slider("フィジカル", 1, 100, 50)
    mental = st.slider("メンタル", 1, 100, 50)

    height = st.number_input("身長 (cm)", min_value=100, max_value=250, value=175)
    weight = st.number_input("体重 (kg)", min_value=30, max_value=150, value=70)
    notes = st.text_area("備考")
    priority = st.selectbox("獲得希望度", ["◎", "◯", "△", "要チェック"])

    if st.button("✅ 追加"):
        add_player(name, position, dob, category, team, height, weight, speed, technique, physical, mental, notes, priority)
