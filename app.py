import streamlit as st
import json
import os
from datetime import datetime

# データベースファイル
DATA_FILE = "player_database.json"

# データの読み込み
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            players = json.load(file)
            return players
    return []

# データの保存
def save_data(players):
    with open(DATA_FILE, "w") as file:
        json.dump(players, file, indent=4)

# 年齢計算
def calculate_age(birth_date):
    today = datetime.today()
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# ページ構成
st.sidebar.title("⚽️ メニュー")
page = st.sidebar.radio(
    "ページを選択してください",
    ["🏠 ホーム", "🔍 検索", "✏️ 編集・削除", "➕ 選手追加"]
)

# データの読み込み
players = load_data()

# ================================
# 🏠 ホーム画面
# ================================
if page == "🏠 ホーム":
    st.title("🏠 選手一覧")

    if not players:
        st.warning("データがありません。選手を追加してください。")
    else:
        st.write("📋 **登録選手の一覧**")
        data = []
        for p in players:
            data.append({
                "名前": p["name"],
                "ポジション": p["position"],
                "年齢": calculate_age(p["dob"]),
                "カテゴリ": p["category"],
                "所属チーム": p["team"],
                "スピード": p["skills"]["speed"],
                "技術": p["skills"]["technique"],
                "フィジカル": p["skills"]["physical"],
                "メンタル": p["skills"]["mental"],
                "身長(cm)": p["height"],
                "体重(kg)": p["weight"],
                "備考": p["notes"],
            })

        # テーブル表示
        st.dataframe(data, use_container_width=True)

# ================================
# 🔍 検索ページ
# ================================
elif page == "🔍 検索":
    st.title("🔍 選手の検索")

    # フィルター条件
    position_filter = st.selectbox("ポジションで絞り込み", ["すべて", "GK", "DF", "MF", "FW"])
    category_filter = st.selectbox("カテゴリで絞り込み", ["すべて", "J1", "J2", "J3"])
    max_age_filter = st.number_input("最大年齢", min_value=15, max_value=40, value=25)
    min_speed_filter = st.slider("最低スピード", 1, 100, 50)

    # フィルタ適用
    filtered_players = [
        p for p in players
        if (position_filter == "すべて" or p["position"] == position_filter)
        and (category_filter == "すべて" or p["category"] == category_filter)
        and calculate_age(p["dob"]) <= max_age_filter
        and p["skills"]["speed"] >= min_speed_filter
    ]

    # 検索結果表示
    if not filtered_players:
        st.warning("条件に合う選手が見つかりません。")
    else:
        st.write("📋 **検索結果**")
        data = []
        for p in filtered_players:
            data.append({
                "名前": p["name"],
                "ポジション": p["position"],
                "年齢": calculate_age(p["dob"]),
                "カテゴリ": p["category"],
                "所属チーム": p["team"],
                "スピード": p["skills"]["speed"],
                "技術": p["skills"]["technique"],
                "フィジカル": p["skills"]["physical"],
                "メンタル": p["skills"]["mental"],
                "身長(cm)": p["height"],
                "体重(kg)": p["weight"],
                "備考": p["notes"],
            })
        st.dataframe(data, use_container_width=True)

# ================================
# ✏️ 編集・削除ページ
# ================================
elif page == "✏️ 編集・削除":
    st.title("✏️ 選手の編集・削除")

    if not players:
        st.warning("選手データがありません。")
    else:
        selected_name = st.selectbox("編集・削除する選手を選択", [p["name"] for p in players])

        # 選手情報の取得
        selected_player = next((p for p in players if p["name"] == selected_name), None)

        if selected_player:
            st.write("✅ **選手情報の編集**")

            # 編集フォーム
            name = st.text_input("選手名", value=selected_player["name"])
            position = st.selectbox("ポジション", ["GK", "DF", "MF", "FW"], index=["GK", "DF", "MF", "FW"].index(selected_player["position"]))
            dob = st.date_input("生年月日", value=datetime.strptime(selected_player["dob"], "%Y-%m-%d"))
            category = st.selectbox("カテゴリ", ["J1", "J2", "J3"], index=["J1", "J2", "J3"].index(selected_player["category"]))
            team = st.text_input("所属チーム", value=selected_player["team"])

            st.subheader("スキル評価 (1-100)")
            speed = st.slider("スピード", 1, 100, selected_player["skills"]["speed"])
            technique = st.slider("技術", 1, 100, selected_player["skills"]["technique"])
            physical = st.slider("フィジカル", 1, 100, selected_player["skills"]["physical"])
            mental = st.slider("メンタル", 1, 100, selected_player["skills"]["mental"])

            height = st.number_input("身長 (cm)", min_value=100, max_value=250, value=selected_player["height"])
            weight = st.number_input("体重 (kg)", min_value=30, max_value=150, value=selected_player["weight"])
            notes = st.text_area("備考", value=selected_player["notes"])

            # 更新処理
            if st.button("✅ 更新"):
                updated_player = {
                    "name": name,
                    "position": position,
                    "dob": dob.strftime("%Y-%m-%d"),
                    "category": category,
                    "team": team,
                    "height": height,
                    "weight": weight,
                    "skills": {
                        "speed": speed,
                        "technique": technique,
                        "physical": physical,
                        "mental": mental,
                    },
                    "notes": notes,
                }

                # 選手情報の更新
                index = players.index(selected_player)
                players[index] = updated_player
                save_data(players)
                st.success(f"✅ {name} の情報を更新しました！")
                st.rerun()

            # 削除処理
            if st.button("❌ 削除"):
                players.remove(selected_player)
                save_data(players)
                st.success(f"❌ {selected_player['name']} を削除しました！")
                st.rerun()

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

    if st.button("✅ 追加"):
        new_player = {
            "name": name,
            "position": position,
            "dob": dob,
            "category": category,
            "team": team,
            "height": height,
            "weight": weight,
            "skills": {
                "speed": speed,
                "technique": technique,
                "physical": physical,
                "mental": mental,
            },
            "notes": notes,
        }

        players.append(new_player)
        save_data(players)
        st.success(f"✅ {name} を追加しました！")
        st.rerun()

