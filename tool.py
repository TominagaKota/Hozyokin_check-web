
import streamlit as st
import re
from PyPDF2 import PdfReader

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

# 判定と金額試算
def check_model(model, quantity):
    if model in target_models:
        entries = target_models[model]
        result = f"✅ {model} は補助金対象です。\n"
        for entry in entries:
            name, unit_price, rate = entry
            amount = unit_price * rate * quantity
            result += f"・{name}：1台あたり¥{int(unit_price * rate):,} → 合計補助金：¥{int(amount):,}\n"
        return result
    else:
        return f"❌ {model} は補助金対象ではありません。"

# PDFアップロード処理
uploaded_file = st.file_uploader("PDF請求書をアップロード（任意）", type="pdf")
if uploaded_file is not None:
    st.info("PDFから型番を抽出します。")
    text = extract_text_from_pdf(uploaded_file)
    models = extract_models(text)
    quantity = st.number_input("台数を入力してください（すべての型番に共通）", min_value=1, step=1, value=1)
    for m in models:
        st.write(check_model(m, quantity))

# テキスト入力による型番チェック
input_text = st.text_input("型番を直接入力してください（例：RZRP160BA）")
quantity_input = st.number_input("台数を入力してください", min_value=1, step=1, value=1)

if input_text:
    models = extract_models(input_text)
    for m in models:
        st.write(check_model(m, quantity_input))
