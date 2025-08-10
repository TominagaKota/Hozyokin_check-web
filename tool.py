# --- ここは先頭の import のすぐ下に置いてOK ---
import streamlit as st
import pandas as pd
import unicodedata, re, difflib, os
from pathlib import Path

# ====== 表示系（スマホ最適化＋文言） ======
st.set_page_config(page_title="富永電機 補助金代行", page_icon="🛠️", layout="wide")

# 画像（ヒーロー）は切らさずに見せるため contain + 横に余白
st.markdown("""
<style>
:root{ --fg:#0f172a; --fg2:#1f2937; --muted:#475569; --line:#e5e7eb;
       --brand:#ff8a00; --bg:#fafaf9; --radius:14px; }
html {font-size:16px;}
body { color:var(--fg2); background:var(--bg); line-height:1.75; }
.container{ max-width:980px; margin:0 auto; padding: 0 14px; }
h1{font-weight:800; color:var(--fg); margin:14px 0 10px; font-size:clamp(20px,5vw,28px); line-height:1.3}
h2{font-weight:700; color:var(--fg); margin:20px 0 12px; font-size:clamp(18px,4.5vw,22px); line-height:1.35}
p{margin:0 0 0.9rem}

.hero-wrap{ margin:10px 0 16px; }
.hero {
  border-radius: var(--radius);
  overflow: hidden;
  background:#fff;
  box-shadow: 0 6px 22px rgba(0,0,0,.08);
  padding: 0 8px; /* ← 横に余白: スマホで切れにくくする */
}
.hero img{
  width:100%;
  height:auto;
  border-radius: var(--radius);
  object-fit: contain;        /* ← 切らずに表示 */
  aspect-ratio: 16/7;         /* 高さを安定させる */
  background: #fff;
}
.note{font-size:12px; color:var(--muted); margin-top:6px; text-align:center}
.btn-row{ display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin: 10px 0 12px;}
.btn{
  display:inline-flex; align-items:center; justify-content:center;
  padding:12px 14px; border-radius:999px; font-weight:700; text-decoration:none;
  background:var(--brand); color:#fff; box-shadow:0 6px 16px rgba(255,138,0,.25)
}
.btn-outline{background:#fff; color:var(--brand); border:2px solid var(--brand)}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown("### 富永電機 補助金代行")

# ヒーロー画像（リポジトリの JPG を参照）
RAW_HERO = "https://raw.githubusercontent.com/TominagaKota/Hozyokin_check-web/main/assets/tomydenki_hero.jpg"

st.markdown('<div class="hero-wrap"><div class="hero">', unsafe_allow_html=True)
st.image(RAW_HERO, use_column_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown("#### 補助金も富永電機におまかせ！")

# 上部ボタン
colA, colB = st.columns(2)
with colA:
    st.markdown('<a class="btn" href="#tokyo_check">東京都補助金を仮判定</a>', unsafe_allow_html=True)
with colB:
    st.markdown('<a class="btn btn-outline" href="#contact">今すぐ相談</a>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # .container をクローズ





# -----------------------
# 補助金判定関数
# -----------------------
def check_hojo(apf, kw, category, region_list, units):
    hojo_files = [
        "kuni_hojo_2025.json",
        "tokyo_hojo_2025.json",
        "edogawa_hojo_2025.json"
    ]
    results = []
    total_sum = 0

    for filename in hojo_files:
        if not os.path.exists(filename):
            continue

        with open(filename, "r", encoding="utf-8") as f:
            hojo = json.load(f)

        name = hojo["補助金名"]
        required_category = hojo["カテゴリ"]
        target_region = hojo["対象地域"]
        condition = hojo["条件"]
        amount_per_unit = hojo["補助金額"]
        max_total = hojo["上限額"]
        is_multiple_allowed = hojo["重複可"]

        if (
            category in required_category and
            any(area in target_region for area in region_list) and
            apf >= condition["APF_min"] and
            condition["kW_range"][0] <= kw <= condition["kW_range"][1]
        ):
            total = min(amount_per_unit * units, max_total)
            results.append({
                "name": name,
                "補助金額": total,
                "重複可": "可能" if is_multiple_allowed else "不可"
            })
            total_sum += total

    return results, total_sum

# -----------------------
# Streamlit アプリ本体
# -----------------------
st.title("補助金自動判定ツール")

# 型番から抽出された数値（テスト用の仮データ）
apf = st.number_input("APF (通年エネルギー消費効率)", value=5.9)
kw = st.number_input("kW (冷房能力)", value=2.8)
category = st.selectbox("カテゴリ", ["家庭用", "業務用"])
region_input = st.text_input("地域（例：東京都江戸川区）", value="東京都 江戸川区")
units = st.number_input("台数", value=1, min_value=1)

# 地域をスペースや・で区切って配列に
region_list = region_input.replace("、", " ").replace("・", " ").split()

# ボタン
if st.button("補助金を判定する"):
    results, total = check_hojo(apf, kw, category, region_list, units)

    if results:
        st.write("\n✅ 該当する補助金一覧：")
        for res in results:
            st.markdown(f"- **{res['name']}**")
            st.write(f"　→ 補助金額：{res['補助金額']}円")
            st.write(f"　→ 重複申請：{res['重複可']}")
        st.markdown(f"### 💰 合計補助金額（{units}台分）：**{total}円**")
    else:
        st.warning("該当する補助金はありませんでした。")
