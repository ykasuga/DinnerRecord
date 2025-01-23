import pandas as pd
import streamlit as st
import requests
from datetime import datetime, date, timedelta

from utils import *

# BASE_URL = "http://localhost:3000"
BASE_URL = "http://backend:3000"  # Docker環境用

# 曜日を日本語の漢字一文字に変換する辞書
weekday_mapping = {
    "Monday": "月",
    "Tuesday": "火",
    "Wednesday": "水",
    "Thursday": "木",
    "Friday": "金",
    "Saturday": "土",
    "Sunday": "日"
}

# メニューの記録
def record_meal():
    st.header("晩御飯メニューを記録")

    url_add_meal = f"{BASE_URL}/add-meal"
    url_all_meals = f"{BASE_URL}/all-meals"
    url_get_meals_for_date = f"{BASE_URL}/get-meals"

    selected_date = get_selected_date()
    menu_options = get_menu_options(url_all_meals)

    # Display existing menu for the selected date
    existing_meals = get_meals_for_date(url_get_meals_for_date, selected_date)
    if existing_meals:
        st.subheader(f"{selected_date.strftime('%Y-%m-%d')} の既存メニュー")
        for meal in existing_meals:
            st.write(f"メニュー: {meal['menu']}")
    else:
        st.subheader(f"{selected_date.strftime('%Y-%m-%d')} の既存メニュー")
        st.write("メニューはありません")

    selected_menu, new_menu = get_menu_selection(menu_options)

    if st.button("記録"):
        submit_meal(url_add_meal, selected_date, selected_menu, new_menu)

# メニューの記録削除機能
def delete_meals():
    st.header("晩御飯の記録削除")

    date = st.date_input("削除する日付を選択してください")
    if st.button("記録を削除"):
        if not date:
            st.error("日付を選択してください")
            return

        # リクエスト送信
        url = f"{BASE_URL}/delete-meals"
        payload = {"date": str(date)}

        try:
            response = requests.delete(url, json=payload)
            if response.status_code == 200 and response.json().get("success"):
                st.success(f"{date} の記録を削除しました")
            else:
                st.error(f"削除に失敗しました: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"エラーが発生しました: {e}")

# 一週間分の記録表示機能
def display_weekly_meals():
    st.header("一週間分の晩御飯記録")

    # ユーザーが週の開始日を入力
    start_date = st.date_input("週の開始日を選んでください", value=date.today() - timedelta(days=6), min_value=date(2020, 1, 1))
    start_date_str = start_date.strftime('%Y-%m-%d')

    if st.button("記録を表示"):
        try:
            # 一週間分の記録を取得
            response = requests.get(f"{BASE_URL}/meals-week", params={"startDate": start_date_str})
            if response.status_code == 200:
                meals = response.json().get("meals", [])
                if meals:
                    # データをテーブル形式に変換
                    table_data = pd.DataFrame(meals)
                    table_data.rename(columns={"date": "日付", "menu": "メニュー"}, inplace=True)

                    # 曜日情報を追加（日本語の漢字一文字で）
                    table_data["曜日"] = table_data["日付"].apply(
                        lambda x: weekday_mapping[datetime.strptime(x, '%Y-%m-%d').strftime('%A')]
                    )

                    # メニューをカンマ区切りでまとめる（同じ日付のものを1行にする）
                    table_data = table_data.groupby(["日付", "曜日"])["メニュー"].apply(", ".join).reset_index()

                    # テーブル表示
                    st.subheader(f"{start_date_str} から 1週間分の記録")
                    st.table(table_data)
                else:
                    st.info("記録が見つかりませんでした。")
            else:
                st.error(f"記録の取得に失敗しました: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"リクエストの送信中にエラーが発生しました: {e}")

# Streamlitのレイアウト
def main():
    st.sidebar.title("晩御飯記録アプリ")
    page = st.sidebar.radio("メニュー", ["メニューを記録", "記録の表示", "記録の削除"])

    if page == "メニューを記録":
        record_meal()
    elif page == "記録の表示":
        # view_meals()
        display_weekly_meals()
    elif page == "記録の削除":
        delete_meals()

if __name__ == "__main__":
    main()
