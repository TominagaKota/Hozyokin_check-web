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
/* ヒーローが下の要素のクリックを邪魔しないように */
.hero-wrap,
.hero-copy { pointer-events: none; }

/* メニューのオーバーレイは閉じてる時はクリック無効 */
.menu-panel { opacity: 0; pointer-events: none; transition: opacity .2s; }
.menu-panel.open { opacity: 1; pointer-events: auto; }

/* 下のセクションは通常レイヤーでOK */
.section { position: relative; z-index: 1; }

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
# ====== 東京都：型番 正式判定 ======
st.markdown('<div id="tokyo_check" class="container"></div>', unsafe_allow_html=True)
st.header("東京都：型番で正式判定（家庭用）")

TOKYO_CSV_PATH = "assets/tokyo_models.csv"  # ここにCSVを置く

def normalize_model(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s).upper()
    s = s.replace("–","-").replace("—","-").replace("−","-").replace("ー","-")
    s = re.sub(r"\s+", "", s)
    # 括弧の中身（色等）を除去
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    # 末尾の色記号だけ安全に除去（-W/-C/-K/-N/-S/-P/-T/-B/-H）
    s = re.sub(r"-(W|C|K|N|S|P|T|B|H)$", "", s)
    return s

@st.cache_data(show_spinner=False)
def load_tokyo_models():
    if not os.path.exists(TOKYO_CSV_PATH):
        return set(), pd.DataFrame()
    # 文字コードは自動判定 → ダメなら cp932
    try:
        df = pd.read_csv(TOKYO_CSV_PATH)
    except UnicodeDecodeError:
        df = pd.read_csv(TOKYO_CSV_PATH, encoding="cp932")
    # 型番っぽい列を抽出（列名に「型」「番」が入るものを優先）
    cand_cols = [c for c in df.columns if ("型" in c) or ("番" in c)]
    if not cand_cols:
        cand_cols = df.columns.tolist()
    vals = pd.Series(dtype=str)
    for c in cand_cols:
        vals = pd.concat([vals, df[c].astype(str)], ignore_index=True)
    vals = vals.dropna().map(normalize_model)
    model_set = set([v for v in vals if v])
    return model_set, df

tokyo_set, tokyo_df = load_tokyo_models()

st.caption(f"登録型番数（正規化後）: {len(tokyo_set)} 件")

user_input = st.text_area("判定したい型番を改行 or カンマ区切りで入力", height=120, placeholder="例）\nRAS–AJ36G\nS22ZTES-W\n... など")
do_check = st.button("正式判定する")

def split_models(s: str):
    if not s: return []
    parts = re.split(r"[\n,、/]+", s)
    return [p.strip() for p in parts if p.strip()]

if do_check:
    rows = []
    for raw in split_models(user_input):
        norm = normalize_model(raw)
        if not norm:
            continue
        exact = norm in tokyo_set
        near = difflib.get_close_matches(norm, list(tokyo_set), n=3, cutoff=0.72)
        rows.append({
            "入力": raw,
            "正規化": norm,
            "正式判定": "○（リスト一致）" if exact else "×（未登録）",
            "候補（近い順）": " / ".join(near[:3]) if not exact and near else ""
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("型番が入力されていません。")
