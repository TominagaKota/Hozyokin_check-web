import streamlit as st
import re

# 仮の補助対象型番
target_models = ["RZRP160BA", "CS-EX280D", "MSZ-ZXV5623S", "AY-L40H", "RAS-X40H2"]

st.title("🧾 補助金対象型番チェックツール")
st.write("型番を入力してください。複数ある場合はカンマ（,）区切りでOKです。")

input_text = st.text_input("型番を入力（例: RZRP160BA, XYZ123, AY-L40H）")

def extract_models(text):
    pattern = r"\b[A-Z]{2,5}-?[A-Z0-9]{3,}\b"
    return re.findall(pattern, text)

def check_model(model):
    if model in target_models:
        return f"✅ {model} は補助金対象です。"
    else:
        return f"❌ {model} は補助金対象ではありません。"

if input_text:
    models = extract_models(input_text)
    st.write("### 判定結果：")
    for m in models:
        st.write(check_model(m))
