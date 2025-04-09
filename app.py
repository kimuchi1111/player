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

    if not filtered_df.empty:  # DataFrameが空でない場合のみ年齢計算を行う
        filtered_df['年齢'] = filtered_df['dob'].apply(calculate_age)
        filtered_df = filtered_df[filtered_df['年齢'] <= max_age_filter]
        filtered_df = filtered_df[filtered_df['speed'] >= min_speed_filter]

        if filtered_df.empty:
            st.warning("条件に合う選手が見つかりません。")
        else:
            st.write("📋 **検索結果**")
            st.dataframe(filtered_df[['name', 'position', '年齢', 'category', 'team', 'speed', 'technique', 'physical', 'mental', 'priority', 'height', 'weight', 'notes']], use_container_width=True)
    else:
        st.warning("条件に合う選手が見つかりません。") # 初期状態でデータがない場合も考慮
