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

# 晩御飯の記録
def record_meal():
    st.header("晩御飯晩御飯を記録")

    url_add_meal = f"{BASE_URL}/add-meal"
    url_all_meals = f"{BASE_URL}/all-meals"
    url_get_meals_for_date = f"{BASE_URL}/get-meals"

    selected_date = get_selected_date()
    menu_options = get_menu_options(url_all_meals)

    # Display existing menu for the selected date
    existing_meals = get_meals_for_date(url_get_meals_for_date, selected_date)
    if existing_meals:
        st.subheader(f"{selected_date.strftime('%Y-%m-%d')} の既存晩御飯")
        for meal in existing_meals:
            st.write(f"晩御飯: {meal['menu']}")
    else:
        st.subheader(f"{selected_date.strftime('%Y-%m-%d')} の既存晩御飯")
        st.write("晩御飯はありません")

    selected_menu, new_menu = get_menu_selection(menu_options)

    if st.button("記録"):
        submit_meal(url_add_meal, selected_date, selected_menu, new_menu)

# 晩御飯の記録削除機能
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
                    table_data.rename(columns={"date": "日付", "menu": "晩御飯"}, inplace=True)

                    # 曜日情報を追加（日本語の漢字一文字で）
                    table_data["曜日"] = table_data["日付"].apply(
                        lambda x: weekday_mapping[datetime.strptime(x, '%Y-%m-%d').strftime('%A')]
                    )

                    # 晩御飯をカンマ区切りでまとめる（同じ日付のものを1行にする）
                    table_data = table_data.groupby(["日付", "曜日"])["晩御飯"].apply(", ".join).reset_index()

                    # テーブル表示
                    st.subheader(f"{start_date_str} から 1週間分の記録")
                    st.table(table_data)
                else:
                    st.info("記録が見つかりませんでした。")
            else:
                st.error(f"記録の取得に失敗しました: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"リクエストの送信中にエラーが発生しました: {e}")

def display_menu_counts():
    st.header("過去の晩御飯")

    url_menu_counts = f"{BASE_URL}/menu-counts"

    try:
        menu_counts = get_menu_counts(url_menu_counts)
        if menu_counts:
            df = pd.DataFrame(menu_counts)
            df.columns = ["晩御飯", "記録回数"]
            st.table(df)
        else:
            st.info("晩御飯が見つかりませんでした。")
    except requests.exceptions.RequestException as e:
        st.error(f"晩御飯の取得中にエラーが発生しました: {e}")

# Streamlitのレイアウト
def main():
    st.sidebar.title("晩御飯記録アプリ")
    page = st.sidebar.radio("おしながき", ["晩御飯を記録", "記録の表示", "過去の晩御飯", "記録の削除"])

    if page == "晩御飯を記録":
        record_meal()
    elif page == "記録の表示":
        display_weekly_meals()
    elif page == "過去の晩御飯":
        display_menu_counts()
    elif page == "記録の削除":
        delete_meals()

if __name__ == "__main__":
    main()
