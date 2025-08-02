import streamlit as st
import re
import PyPDF2

st.title("エアコン型番 補助金判定ツール")

target_models = ["RZRP160BA", "CS-EX280D", "MSZ-ZXV5623S", "AY-L40H", "RAS-X40H2"]

def extract_models(text):
    pattern = r"[A-Z]{2,}-?[A-Z0-9]+"
    return re.findall(pattern, text)

def check_model(model):
    if model in target_models:
        return f"✅ {model} は補助金対象です。"
    else:
        return f"❌ {model} は補助金対象ではありません。"

# PDFをアップロード
uploaded_file = st.file_uploader("PDF請求書をアップロードしてください", type="pdf")

if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    models = extract_models(text)
    st.write("🔍 検出された型番一覧:")
    for m in models:
        st.write(check_model(m))

# テキスト入力も可能
input_text = st.text_input("もしくは型番を直接入力してください（例：RZRP160BA）")

if input_text:
    models = extract_models(input_text)
    for m in models:
        st.write(check_model(m))

