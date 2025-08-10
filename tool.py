import streamlit as st
import json, os
from pathlib import Path

BASE_DIR = Path(__file__).parent
img_path_webp = BASE_DIR / "assets" / "tomydenki_pic1.webp"
img_path_jpg  = BASE_DIR / "assets" / "tomydenki_hero.jpg"  # 予備

# まずWEBP、無ければJPGを表示
# ===== ヒーロー（画像＋中央キャッチコピー） =====
RAW_HERO_URL = (
    "https://raw.githubusercontent.com/TominagaKota/Hozyokin_check-web/"
    "11e569bd72839eca3392c1eda061c7840855ca/assets/tomydenki_hero.jpg"
)

st.markdown(f"""
<style>
/* ヒーロー全体 */
.hero-wrap {{
  position: relative;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 6px 22px rgba(0,0,0,0.12);
  margin: 8px 0 18px;
}}
/* 背景画像（アスペクトは自動・スマホでも崩れにくく） */
.hero-bg {{
  width: 100%;
  aspect-ratio: 16/7;         /* 画面比。必要なら 16/6 や 21/9 に調整可 */
  background-image: url('{RAW_HERO_URL}');
  background-size: cover;
  background-position: center;
  filter: saturate(1.02);
}}
/* 中央キャッチコピー */
.hero-copy {{
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;         /* 完全中央寄せ */
  text-align: center;
  padding: 0 4vw;
}}
.hero-copy .line1 {{
  font-weight: 800;
  color: #ffffff;
  text-shadow: 0 2px 14px rgba(0,0,0,.45);
  /* 画面幅に応じて自動スケール：最小1.2rem, 推奨3.0vw, 最大2.4rem */
  font-size: clamp(1.2rem, 3.4vw, 2.4rem);
  letter-spacing: .06em;
  line-height: 1.25;
  display: inline-block;
  background: linear-gradient(transparent 60%, rgba(255,153,0,.85) 60%);
  padding: .15em .25em;
  border-radius: 6px;
}}
@media (max-width: 768px) {{
  .hero-bg {{
    aspect-ratio: 16/9;        /* スマホは縦を少し広げて見やすく */
  }}
  .hero-copy .line1 {{
    font-size: clamp(1.05rem, 5.2vw, 1.6rem);
    letter-spacing: .04em;
  }}
}}
</style>

<div class="hero-wrap">
  <div class="hero-bg"></div>
  <div class="hero-copy">
    <span class="line1">補助金も富永電機におまかせ！</span>
  </div>
</div>
""", unsafe_allow_html=True)



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
