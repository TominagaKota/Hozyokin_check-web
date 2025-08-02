
import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

st.title("補助金対象機器チェック＆金額試算ツール")

# 型番ごとの補助金・単価・補助率
target_models = {
    "RZRP160BA": [("省エネ補助金（国）", 500000, 1/3)],
    "CS-EX280D": [("省エネ補助金（国）", 350000, 1/3),
                  ("ゼロエミ補助金（東京都）", 350000, 2/3)],
    "AY-L40H": [("住宅省エネ2024キャンペーン", 200000, 0.1)],
    "RAS-X40H2": [("省エネ補助金（国）", 400000, 1/3)],
    "MSZ-ZXV5623S": [("省エネ補助金（国）", 420000, 1/3)]
}

# 型番抽出用の正規表現
def extract_models(text):
    pattern = r"[A-Z]{2,}-?[A-Z0-9]+"
    return re.findall(pattern, text)

# PDFからテキスト抽出
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 判定と金額試算（表形式）
def check_model_table(model, quantity):
    if model not in target_models:
        return pd.DataFrame([{
            "型番": model,
            "補助金名": "対象外",
            "定価（円）": "-",
            "補助率（%）": "-",
            "割引額（円）": "-",
            "合計補助金額（円）": "-"
        }])

    rows = []
    for entry in target_models[model]:
        name, unit_price, rate = entry
        discount = int(unit_price * rate)
        amount = int(discount * quantity)
        rows.append({
            "型番": model,
            "補助金名": name,
            "定価（円）": unit_price,
            "補助率（%）": int(rate * 100),
            "割引額（円）": discount,
            "合計補助金額（円）": amount
        })
    return pd.DataFrame(rows)

# PDFアップロード処理
uploaded_file = st.file_uploader("PDF請求書をアップロード（任意）", type="pdf")
if uploaded_file is not None:
    st.info("PDFから型番を抽出します。")
    text = extract_text_from_pdf(uploaded_file)
    models = extract_models(text)
    quantity = st.number_input("台数を入力してください（すべての型番に共通）", min_value=1, step=1, value=1)
    for m in models:
        df = check_model_table(m, quantity)
        st.dataframe(df)

# テキスト入力による型番チェック
input_text = st.text_input("型番を直接入力してください（例：RZRP160BA）")
quantity_input = st.number_input("台数を入力してください", min_value=1, step=1, value=1)

if input_text:
    models = extract_models(input_text)
    for m in models:
        df = check_model_table(m, quantity_input)
        st.dataframe(df)
