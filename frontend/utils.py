import pandas as pd
import streamlit as st
import requests
from datetime import datetime, date, timedelta

def get_all_meals(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            all_meals = response.json().get("meals", [])
            return sorted([item['menu'] for item in all_meals])
        else:
            return []
    except requests.exceptions.RequestException:
        st.error("過去のメニューを取得できませんでした。")
        return []

def get_menu_options(url):
    return get_all_meals(url)

def get_selected_date():
    return st.date_input("日付を選択してください", value=date.today())

def get_menu_selection(menu_options):
    st.subheader("晩御飯メニューを選択または入力")
    selected_menu = st.selectbox("過去のメニューから選択してください", options=[""] + menu_options, index=0)
    new_menu = st.text_input("新しいメニューを入力してください")
    return selected_menu, new_menu

def submit_meal(url, selected_date, selected_menu, new_menu):
    if not selected_menu and not new_menu:
        st.error("メニューを選択または入力してください。")
        return

    meal_data = {
        "date": selected_date.strftime("%Y-%m-%d"),
        "menu": new_menu if new_menu else selected_menu
    }

    try:
        response = requests.post(url, json=meal_data)
        if response.status_code == 200:
            st.success("メニューが記録されました。")
        else:
            st.error(f"メニューの記録に失敗しました: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"メニューの記録中にエラーが発生しました: {e}")

def get_meals_for_date(url, selected_date):
    try:
        response = requests.get(f"{url}/{selected_date.strftime('%Y-%m-%d')}")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.exceptions.RequestException:
        st.error("メニューを取得できませんでした。")
        return []
