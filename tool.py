import streamlit as st
import json, os
from pathlib import Path

BASE_DIR = Path(__file__).parent
img_path_webp = BASE_DIR / "assets" / "tomydenki_pic1.webp"
img_path_jpg  = BASE_DIR / "assets" / "tomydenki_hero.jpg"  # 予備

# まずWEBP、無ければJPGを表示
# ==== ヒーロー（画像＋中央キャッチコピー：切れない版）====
RAW_HERO_URL = "https://raw.githubusercontent.com/TominagaKota/Hozyokin_check-web/main/assets/tomydenki_hero.jpg"

st.markdown(f"""
<style>
.hero {{
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  margin: 8px 18px;
  box-shadow: 0 6px 22px rgba(0,0,0,.08);
}}
.hero-img {{
  width: 100%;
  height: auto;   /* ← これでトリミング無し */
  display: block;
  filter: saturate(1.02);
}}
.hero-title {{
  position: absolute;
  left: 50%;
  bottom: clamp(10px, 3vw, 24px);
  transform: translateX(-50%);
  background: rgba(15,23,42,.78);
  color: #fff;
  font-weight: 800;
  line-height: 1.28;
  padding: .45em .9em;
  border-radius: 12px;
  font-size: clamp(18px, 3.8vw, 28px);
  letter-spacing: .03em;
  text-align: center;
  white-space: nowrap;
}}
@media (max-width: 640px) {{
  .hero-title {{
    white-space: normal;              /* スマホは改行OK */
    max-width: 92%;
    padding: .5em .9em;
    font-size: clamp(16px, 4.6vw, 22px);
  }}
}}
</style>

<div class="hero">
  <img src="{RAW_HERO_URL}" alt="富永電機の現場写真" class="hero-img" />
  <div class="hero-title">補助金も富永電機におまかせ！</div>
</div>
""", unsafe_allow_html=True)
# ==== ヒーロー ここまで ====



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
