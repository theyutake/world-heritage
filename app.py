import os
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="世界遺産",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

C_ACTIVE   = "#0096D6"
C_DARK     = "#003DA5"
C_TEXT     = "#0D1E35"
C_SUB      = "#A8BBCC"
C_INACTIVE = "#B0C0CF"
C_BG       = "#F7FAFD"
C_ICON_BG  = "#EAF2F9"
C_CARD     = "#FFFFFF"

REGION_LABELS = {
    "Africa":                          "アフリカ",
    "Arab States":                     "アラブ諸国",
    "Asia and the Pacific":            "アジア・太平洋",
    "Europe and North America":        "ヨーロッパ・北米",
    "Latin America and the Caribbean": "中南米・カリブ海",
}
REGION_EMOJI = {
    "Africa":                          "🌍",
    "Arab States":                     "🕌",
    "Asia and the Pacific":            "🏯",
    "Europe and North America":        "🗼",
    "Latin America and the Caribbean": "🌎",
}
REGION_GRAD = {
    "Africa":                          "linear-gradient(135deg,#3DBAC8,#009AA8)",
    "Arab States":                     "linear-gradient(135deg,#4C6FA8,#003DA5)",
    "Asia and the Pacific":            "linear-gradient(135deg,#A8DAEF,#5BB6E8)",
    "Europe and North America":        "linear-gradient(135deg,#72C2F0,#0096D6)",
    "Latin America and the Caribbean": "linear-gradient(135deg,#00C4E8,#0096D6)",
}
CAT_LABEL = {"Cultural": "文化遺産", "Natural": "自然遺産", "Mixed": "複合遺産"}
CAT_ICON  = {"Cultural": "🏛️", "Natural": "🌿", "Mixed": "✨"}
CAT_GRAD  = {
    "Cultural": "linear-gradient(135deg,#4C6FA8,#003DA5)",
    "Natural":  "linear-gradient(135deg,#3DBAC8,#009AA8)",
    "Mixed":    "linear-gradient(135deg,#72C2F0,#0096D6)",
}

# ─── CSS ─────────────────────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    /* ── Global reset ── */
    body {{ color: {C_TEXT}; }}
    [data-testid="stAppViewContainer"] {{
        background: {C_BG} !important;
        max-width: 480px;
        margin: 0 auto;
    }}
    [data-testid="stHeader"]  {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{
        padding: 0 16px 80px 16px !important;
        max-width: 480px !important;
    }}
    /* ── Screen header ── */
    .screen-header {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 14px 4px 10px; margin-bottom: 2px;
    }}
    .screen-title {{
        font-size: 22px; font-weight: 800; color: {C_TEXT};
        letter-spacing: -0.3px; margin: 0;
    }}
    .h-icons {{ display: flex; gap: 8px; }}
    .h-icon {{
        width: 34px; height: 34px; background: {C_ICON_BG};
        border-radius: 11px; display: flex; align-items: center; justify-content: center;
    }}
    /* ── Section row ── */
    .sec-row {{
        display: flex; justify-content: space-between; align-items: center;
        margin: 14px 0 8px;
    }}
    .sec-title {{ font-size: 14px; font-weight: 800; color: {C_TEXT}; }}
    /* ── Chip ── */
    .chip {{
        display: inline-flex; align-items: center; gap: 6px;
        margin: 0 0 10px; padding: 5px 13px; background: #fff;
        border-radius: 20px; box-shadow: 0 1px 6px rgba(0,50,130,0.09);
        font-size: 11px; font-weight: 700; color: {C_TEXT};
    }}
    .chip-dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: linear-gradient(135deg, {C_ACTIVE}, {C_DARK});
    }}
    /* ── Region card ── */
    .region-card {{
        background: {C_CARD}; border-radius: 18px; padding: 10px 14px;
        margin-bottom: 10px; box-shadow: 0 2px 10px rgba(0,50,130,0.07);
        display: flex; align-items: center; gap: 11px;
    }}
    .r-flag {{
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 17px; flex-shrink: 0;
    }}
    .r-label {{ font-size: 10px; color: {C_SUB}; font-weight: 500; }}
    .r-name  {{ font-size: 13px; font-weight: 700; color: {C_TEXT}; }}
    .r-count {{ margin-left: auto; font-size: 12px; color: {C_INACTIVE}; }}
    /* ── Daily card ── */
    .daily-card {{
        background: {C_ICON_BG}; border-radius: 20px; padding: 14px 16px;
        margin-bottom: 10px; display: flex; align-items: center; gap: 14px;
    }}
    .circ-wrap {{ position: relative; width: 60px; height: 60px; flex-shrink: 0; }}
    .circ-wrap svg {{ transform: rotate(-90deg); }}
    .circ-label {{
        position: absolute; inset: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 800; color: {C_ACTIVE};
    }}
    .task-sup {{ font-size: 10px; font-weight: 600; color: #5DB5D8; text-transform: uppercase; letter-spacing:.06em; margin-bottom: 3px; }}
    .task-txt {{ font-size: 13px; font-weight: 700; color: {C_TEXT}; line-height: 1.4; }}
    /* ── XP card ── */
    .xp-card {{
        background: {C_CARD}; border-radius: 20px; padding: 14px 16px;
        margin-bottom: 10px; box-shadow: 0 2px 12px rgba(0,50,130,0.07);
    }}
    .xp-sub {{ font-size: 11px; color: {C_SUB}; margin-bottom: 10px; }}
    .xp-sub b {{ color: {C_ACTIVE}; font-size: 13px; }}
    .bars {{ display: flex; align-items: flex-end; gap: 5px; height: 46px; }}
    .bar {{ flex: 1; border-radius: 4px 4px 0 0; }}
    .bar-on  {{ background: linear-gradient(180deg, {C_ACTIVE} 0%, {C_DARK} 100%); }}
    .bar-off {{ background: #D8EDF8; }}
    .days {{ display: flex; gap: 5px; margin-top: 5px; }}
    .day {{ flex: 1; text-align: center; font-size: 8px; font-weight: 600; color: #B8C8D8; }}
    .day-on {{ color: {C_ACTIVE}; }}
    /* ── Level card ── */
    .lvl-card {{
        background: {C_CARD}; border-radius: 20px; padding: 12px 14px;
        margin-bottom: 10px; box-shadow: 0 2px 12px rgba(0,50,130,0.07);
        display: flex; align-items: center; gap: 12px;
    }}
    .lvl-icon {{
        width: 42px; height: 42px; border-radius: 14px;
        background: linear-gradient(135deg, {C_ACTIVE}, {C_DARK});
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; flex-shrink: 0;
    }}
    .lvl-name  {{ font-size: 13px; font-weight: 700; color: {C_TEXT}; margin-bottom: 5px; }}
    .lvl-track {{ height: 5px; background: #D8EDF8; border-radius: 3px; }}
    .lvl-fill  {{ height: 100%; background: linear-gradient(90deg, {C_ACTIVE}, #00C4E8); border-radius: 3px; }}
    .lvl-badge {{ margin-left: auto; padding: 4px 11px; background: {C_ICON_BG}; color: {C_ACTIVE}; font-size: 10px; font-weight: 700; border-radius: 20px; }}
    /* ── Region grid ── */
    .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }}
    .gc {{
        height: 90px; border-radius: 18px; overflow: hidden; position: relative;
        display: flex; align-items: center; justify-content: center;
    }}
    .gc .em {{ font-size: 30px; }}
    .gc-lbl {{
        position: absolute; bottom: 0; left: 0; right: 0; padding: 6px 10px;
        background: linear-gradient(transparent, rgba(0,18,56,.65));
        font-size: 10px; font-weight: 700; color: #fff; line-height: 1.3;
    }}
    /* ── hcard ── */
    .hcard {{
        background: {C_CARD}; border-radius: 18px; padding: 10px 12px;
        margin-bottom: 10px; display: flex; align-items: center; gap: 10px;
        box-shadow: 0 2px 10px rgba(0,50,130,0.07);
    }}
    .hthumb {{
        width: 66px; height: 66px; border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 26px; flex-shrink: 0;
    }}
    .hcard-title {{ font-size: 12px; font-weight: 700; color: {C_TEXT}; margin-bottom: 2px; line-height: 1.4; }}
    .hcard-loc   {{ font-size: 10px; color: {C_SUB}; margin-bottom: 5px; }}
    .htag {{ font-size: 9px; font-weight: 600; padding: 2px 7px; border-radius: 20px; margin-right: 3px; }}
    .htag-c {{ background: #EAF2F9; color: {C_DARK}; }}
    .htag-n {{ background: #E6F9F7; color: #007A6E; }}
    .htag-m {{ background: {C_ICON_BG}; color: {C_ACTIVE}; }}
    .htag-d {{ background: #FDECEA; color: #C62828; }}
    /* ── Quiz card ── */
    .quiz-q-card {{
        background: linear-gradient(135deg, {C_ACTIVE} 0%, {C_DARK} 100%);
        border-radius: 20px; padding: 20px; color: white;
        margin-bottom: 14px; box-shadow: 0 4px 20px rgba(0,58,154,0.28);
    }}
    .quiz-q-sup {{ font-size: 10px; opacity: 0.75; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }}
    .quiz-q-title {{ font-size: 17px; font-weight: 800; line-height: 1.3; }}
    /* ── ボタン全体リセット（背景・文字色を明示） ── */
    div[data-testid="stButton"] > button {{
        background: #fff !important;
        color: {C_TEXT} !important;
        border: 1.5px solid #E0EAF5 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: #F0F8FF !important;
        border-color: {C_ACTIVE} !important;
        color: {C_ACTIVE} !important;
        box-shadow: none !important;
    }}
    div[data-testid="stButton"] > [data-testid="baseButton-primary"] {{
        background: {C_ACTIVE} !important;
        color: white !important;
        border: none !important;
    }}
    div[data-testid="stButton"] > [data-testid="baseButton-primary"]:hover {{
        background: {C_DARK} !important;
        color: white !important;
    }}
    /* ── フォーム要素リセット ── */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] > div > div {{
        background: transparent !important;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] input {{
        background: #fff !important;
        color: {C_TEXT} !important;
        border: 1.5px solid #D0DFF0 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        caret-color: {C_TEXT} !important;
    }}
    div[data-testid="stTextInput"] input::placeholder {{ color: {C_SUB} !important; opacity: 1; }}
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextInput"] label p {{ color: {C_TEXT} !important; }}
    /* ── セレクトボックス ライトテーマ ── */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p {{ color: {C_TEXT} !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: #fff !important;
        border: 1.5px solid #D0DFF0 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div > div {{
        background: transparent !important;
        color: {C_TEXT} !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
        color: {C_TEXT} !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{
        fill: {C_TEXT} !important;
        color: {C_TEXT} !important;
    }}
    div[data-baseweb="popover"] [role="listbox"],
    div[data-baseweb="popover"] ul {{ background: #fff !important; }}
    div[data-baseweb="popover"] [role="option"] {{
        background: #fff !important; color: {C_TEXT} !important;
    }}
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [aria-selected="true"] {{
        background: {C_ICON_BG} !important;
    }}
    /* ── タブ ── */
    div[data-testid="stTabs"] button[role="tab"] {{ color: {C_TEXT} !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {C_ACTIVE} !important; }}
    /* ── Bottom nav (st.bottom内部) ── */
    [data-testid="stBottom"] {{
        background: #fff !important;
        border-top: 1px solid #EDF2F8 !important;
        box-shadow: 0 -2px 16px rgba(0,50,130,0.08) !important;
    }}
    [data-testid="stBottom"] > div {{
        padding: 0 !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }}
    /* nav-item-wrap: アイコン＋ラベルの見た目 */
    .nav-item-wrap {{
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; gap: 3px;
        height: 62px; padding-top: 8px;
        font-size: 9px; font-weight: 700; color: {C_INACTIVE};
    }}
    .nav-item-wrap.on {{ color: {C_ACTIVE}; }}
    .nav-item-wrap svg {{ stroke: {C_INACTIVE}; }}
    .nav-item-wrap.on svg {{ stroke: {C_ACTIVE}; }}
    /* nav-item-wrap の直後ボタンを透明オーバーレイ */
    div.element-container:has(div.nav-item-wrap) {{ margin-bottom: 0 !important; }}
    div.element-container:has(div.nav-item-wrap) + div.element-container {{
        margin-top: -62px !important; height: 62px !important;
        position: relative; z-index: 10;
    }}
    div.element-container:has(div.nav-item-wrap) + div.element-container button {{
        height: 62px !important; width: 100% !important;
        opacity: 0 !important; cursor: pointer !important;
        border: none !important; background: transparent !important;
        padding: 0 !important; box-shadow: none !important;
    }}
    /* ── Overlay buttons on cards ── */
    div.element-container:has(div.region-card) {{ margin-bottom: 0 !important; }}
    div.element-container:has(div.region-card) + div.element-container {{
        margin-top: -68px !important; height: 68px; position: relative; z-index: 10;
    }}
    div.element-container:has(div.region-card) + div.element-container button {{
        height: 68px !important; width: 100% !important; opacity: 0 !important;
        cursor: pointer !important; border: none !important;
        background: transparent !important; padding: 0 !important;
    }}
    div.element-container:has(div.hcard) {{ margin-bottom: 0 !important; }}
    div.element-container:has(div.hcard) + div.element-container {{
        margin-top: -96px !important; height: 96px; position: relative; z-index: 10;
    }}
    div.element-container:has(div.hcard) + div.element-container button {{
        height: 96px !important; width: 100% !important; opacity: 0 !important;
        cursor: pointer !important; border: none !important;
        background: transparent !important; padding: 0 !important;
    }}
    div.element-container:has(div.gc) {{ margin-bottom: 0 !important; }}
    div.element-container:has(div.gc) + div.element-container {{
        margin-top: -98px !important; height: 98px; position: relative; z-index: 10;
    }}
    div.element-container:has(div.gc) + div.element-container button {{
        height: 98px !important; width: 100% !important; opacity: 0 !important;
        cursor: pointer !important; border: none !important;
        background: transparent !important; padding: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ─── データ読み込み（CSV） ──────────────────────────────────────
@st.cache_data
def load_heritage_df():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heritage.csv")
    df = pd.read_csv(path)
    # unique_number を id として使用（Supabase の auto-increment id の代替）
    if "id" not in df.columns:
        df["id"] = df["unique_number"]
    if "danger" in df.columns:
        df["danger"] = df["danger"].fillna(False).astype(bool)
    return df

def fetch_all_heritage():
    df = load_heritage_df()
    cols = ["id", "name_en", "name_ja", "category", "states_name_en", "date_inscribed", "region_en", "danger"]
    return df[[c for c in cols if c in df.columns]].fillna("").to_dict("records")

def fetch_heritage_total_count():
    return len(load_heritage_df())

def fetch_heritage_list(region, category, kw):
    df = load_heritage_df().copy()
    if region:
        df = df[df["region_en"] == region]
    if category:
        df = df[df["category"] == category]
    if kw:
        mask = (
            df["name_ja"].fillna("").str.contains(kw, case=False) |
            df["name_en"].fillna("").str.contains(kw, case=False) |
            df["states_name_en"].fillna("").str.contains(kw, case=False)
        )
        df = df[mask]
    df = df.sort_values("date_inscribed")
    cols = ["id", "name_en", "name_ja", "category", "states_name_en", "region_en", "date_inscribed", "danger", "criteria_txt"]
    return df[[c for c in cols if c in df.columns]].head(200).fillna("").to_dict("records")

def fetch_heritage_detail(hid):
    df = load_heritage_df()
    row = df[df["id"] == hid]
    if row.empty:
        return {}
    return row.iloc[0].where(pd.notna(row.iloc[0]), other="").to_dict()

# ─── セッション ───────────────────────────────────────────────────
def init_session():
    defaults = {
        "tab": "home", "selected_id": None,
        "detail_from": "list", "show_search": False, "search_kw": "",
        "quiz_data": None, "quiz_answered": False, "quiz_correct": False,
        "quiz_score": 0, "quiz_count": 0, "quiz_selected_idx": -1,
        "filter_region": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── ヘルパー ────────────────────────────────────────────────────
def disp(row):
    return row.get("name_ja") or row.get("name_en", "")

SEARCH_SVG  = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'
BELL_SVG    = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'
FILTER_SVG  = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="12" y1="18" x2="20" y2="18"/></svg>'
PIN_SVG     = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 1 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
CAL_SVG     = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
TAG_SVG     = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>'
AREA_SVG    = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>'
STAR_SVG    = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
TARGET_SVG  = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
TEMPLE_SVG  = '<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="2" y="20" width="20" height="2"/><rect x="4" y="11" width="2" height="9"/><rect x="11" y="11" width="2" height="9"/><rect x="18" y="11" width="2" height="9"/><path d="M12 3L2 9h20z"/></svg>'

def screen_header(title, icons_html=""):
    st.markdown(
        f'<div class="screen-header"><span class="screen-title">{title}</span>'
        f'<div class="h-icons">{icons_html}</div></div>',
        unsafe_allow_html=True,
    )

# ─── ホーム ──────────────────────────────────────────────────────
def page_home():
    screen_header("Home", f'<div class="h-icon">{BELL_SVG}</div>')

    all_h = fetch_all_heritage()

    day_seed = __import__("datetime").date.today().toordinal()
    if all_h:
        today       = all_h[day_seed % len(all_h)]
        region_en   = today.get("region_en", "")
        region_grad = REGION_GRAD.get(region_en, f"linear-gradient(135deg,{C_ACTIVE},{C_DARK})")
        region_em   = REGION_EMOJI.get(region_en, "🌍")
        st.markdown(
            f'<div class="region-card">'
            f'<div class="r-flag" style="background:{region_grad}">{region_em}</div>'
            f'<div><div class="r-label">Today\'s Heritage</div>'
            f'<div class="r-name">{disp(today)}</div></div>'
            f'<div class="r-count">›</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("　", key="hero_btn", use_container_width=True):
            st.session_state.selected_id = today["id"]
            st.session_state.detail_from = "home"
            st.session_state.tab = "detail"
            st.rerun()

    # Daily quiz progress
    score = st.session_state.quiz_score
    count = st.session_state.quiz_count
    pct   = int(score / max(count, 1) * 100)
    offset = int(144 * (1 - pct / 100))
    st.markdown(
        f'<div class="daily-card">'
        f'<div class="circ-wrap">'
        f'<svg width="60" height="60" viewBox="0 0 60 60">'
        f'<circle fill="none" stroke="#C8E8F6" stroke-width="4" cx="30" cy="30" r="23"/>'
        f'<circle fill="none" stroke="{C_ACTIVE}" stroke-width="4" stroke-linecap="round" stroke-dasharray="144" stroke-dashoffset="{offset}" cx="30" cy="30" r="23"/>'
        f'</svg><div class="circ-label">{pct}%</div></div>'
        f'<div><div class="task-sup">Daily Quiz</div>'
        f'<div class="task-txt">スコア {score} / {max(count,1)}<br>クイズに挑戦しよう</div></div></div>',
        unsafe_allow_html=True,
    )

    # XP stats
    total    = len(all_h)
    cultural = sum(1 for h in all_h if h.get("category") == "Cultural")
    natural  = sum(1 for h in all_h if h.get("category") == "Natural")
    mixed    = sum(1 for h in all_h if h.get("category") == "Mixed")
    danger   = sum(1 for h in all_h if h.get("danger"))
    vals     = [cultural // 20, natural // 10, mixed * 2, danger, total // 100, 18, 10]
    max_v    = max(vals) or 1
    bar_html = "".join(
        f'<div class="bar {"bar-on" if i < 5 else "bar-off"}" style="height:{max(4,int(v/max_v*46))}px"></div>'
        for i, v in enumerate(vals)
    )
    st.markdown('<div class="sec-row"><span class="sec-title">データベース統計</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="xp-card">'
        f'<div class="xp-sub">Total <b>{total} Sites</b> · 文化 {cultural} · 自然 {natural} · 危機 {danger}</div>'
        f'<div class="bars">{bar_html}</div>'
        f'<div class="days">'
        f'<span class="day day-on">文化</span><span class="day day-on">自然</span>'
        f'<span class="day day-on">複合</span><span class="day day-on">危機</span>'
        f'<span class="day day-on">総数</span><span class="day"></span><span class="day"></span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Level card
    level      = max(1, score // 5 + 1)
    level_name = ["Beginner", "Explorer", "Traveler", "Expert", "Master"][min(level - 1, 4)]
    fill_pct   = (score % 5) * 20
    st.markdown('<div class="sec-row"><span class="sec-title">Heritage Level</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="lvl-card">'
        f'<div class="lvl-icon">🏛️</div>'
        f'<div style="flex:1"><div class="lvl-name">{level_name} · Lv.{level}</div>'
        f'<div class="lvl-track"><div class="lvl-fill" style="width:{fill_pct}%"></div></div></div>'
        f'<div class="lvl-badge">{score} XP</div></div>',
        unsafe_allow_html=True,
    )

    # Region list
    st.markdown('<div class="sec-row"><span class="sec-title">地域から探す</span></div>', unsafe_allow_html=True)
    region_counts: dict = {}
    for h in all_h:
        r = h.get("region_en", "")
        region_counts[r] = region_counts.get(r, 0) + 1

    for r_en, cnt in sorted(region_counts.items(), key=lambda x: -x[1]):
        label = REGION_LABELS.get(r_en, r_en)
        em    = REGION_EMOJI.get(r_en, "🌍")
        grad  = REGION_GRAD.get(r_en, f"linear-gradient(135deg,{C_ACTIVE},{C_DARK})")
        st.markdown(
            f'<div class="region-card">'
            f'<div class="r-flag" style="background:{grad}">{em}</div>'
            f'<div><div class="r-label">World Heritage</div><div class="r-name">{label}</div></div>'
            f'<div class="r-count">{cnt}件 ›</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("　", key=f"region_{r_en}", help=label, use_container_width=True):
            st.session_state.tab = "list"
            st.session_state.filter_region = r_en
            st.rerun()

# ─── リスト (Sites) ──────────────────────────────────────────────
def page_list():
    screen_header("Sites", f'<div class="h-icon">{SEARCH_SVG}</div><div class="h-icon">{FILTER_SVG}</div>')

    total_cnt = fetch_heritage_total_count()
    st.markdown(
        f'<div class="chip"><div class="chip-dot"></div>World Heritage · {total_cnt} Sites</div>',
        unsafe_allow_html=True,
    )

    # 2×2 region grid
    grid_data = [
        ("Asia and the Pacific",     "🏯", "linear-gradient(135deg,#A8DAEF,#5BB6E8)"),
        ("Europe and North America", "🗼", "linear-gradient(135deg,#72C2F0,#0096D6)"),
        ("Arab States",              "🕌", "linear-gradient(135deg,#4C6FA8,#003DA5)"),
        ("Africa",                   "🌍", "linear-gradient(135deg,#3DBAC8,#009AA8)"),
    ]
    cols = st.columns(2)
    for i, (r_en, em, grad) in enumerate(grid_data):
        label = REGION_LABELS.get(r_en, r_en)
        with cols[i % 2]:
            st.markdown(
                f'<div class="gc" style="background:{grad}">'
                f'<span class="em">{em}</span>'
                f'<div class="gc-lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("　", key=f"grid_{r_en}", help=label, use_container_width=True):
                st.session_state.filter_region = r_en
                st.rerun()

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        cur_region    = st.session_state.get("filter_region")
        region_opts   = ["すべて"] + list(REGION_LABELS.keys())
        default_idx   = region_opts.index(cur_region) if cur_region in region_opts else 0
        region_sel    = st.selectbox(
            "地域", region_opts,
            format_func=lambda x: "すべて" if x == "すべて" else REGION_LABELS[x],
            index=default_idx, key="filter_region_sel",
        )
        st.session_state.filter_region = region_sel if region_sel != "すべて" else None
    with col2:
        cat_sel = st.selectbox(
            "種別", ["すべて", "Cultural", "Natural", "Mixed"],
            format_func=lambda x: "すべて" if x == "すべて" else CAT_LABEL[x],
            key="filter_cat_sel",
        )

    kw = st.text_input("", placeholder="遺産名・国名で検索…",
                       label_visibility="collapsed", key="search_input").strip()

    rows = fetch_heritage_list(
        region_sel if region_sel != "すべて" else None,
        cat_sel if cat_sel != "すべて" else None,
        kw,
    )

    st.markdown(
        f'<p style="font-size:12px;color:{C_SUB};margin:0 0 10px">'
        f'{len(rows)}件{"（上限200）" if len(rows)==200 else ""}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:13px;font-weight:800;color:{C_TEXT};margin-bottom:8px">Curated for you</div>',
        unsafe_allow_html=True,
    )

    for row in rows:
        name    = disp(row)
        cat     = row.get("category", "Cultural")
        em      = CAT_ICON.get(cat, "🌍")
        grad    = CAT_GRAD.get(cat, f"linear-gradient(135deg,{C_ACTIVE},{C_DARK})")
        loc     = row.get("states_name_en", "")
        year    = row.get("date_inscribed", "")
        crit    = (row.get("criteria_txt") or "").strip()
        tag_cls = {"Cultural": "htag-c", "Natural": "htag-n", "Mixed": "htag-m"}.get(cat, "htag-c")

        tags = f'<span class="htag {tag_cls}">{year}年登録</span>'
        if crit:
            tags += f'<span class="htag {tag_cls}">{crit}</span>'
        if row.get("danger"):
            tags += '<span class="htag htag-d">⚠️危機遺産</span>'

        st.markdown(
            f'<div class="hcard">'
            f'<div class="hthumb" style="background:{grad}">{em}</div>'
            f'<div style="flex:1;min-width:0">'
            f'<div class="hcard-title">{name}</div>'
            f'<div class="hcard-loc">📍 {loc}</div>'
            f'<div style="display:flex;gap:3px;flex-wrap:wrap">{tags}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("　", key=f"list_{row['id']}", help=name, use_container_width=True):
            st.session_state.selected_id = row["id"]
            st.session_state.detail_from = "list"
            st.session_state.tab = "detail"
            st.rerun()

# ─── 詳細 ────────────────────────────────────────────────────────
def page_detail():
    hid = st.session_state.selected_id
    h   = fetch_heritage_detail(hid)

    if st.button("← 戻る", key="back"):
        st.session_state.tab = st.session_state.get("detail_from", "list")
        st.rerun()

    name     = disp(h)
    cat      = h.get("category", "Cultural")
    em       = CAT_ICON.get(cat, "🌍")
    grad     = CAT_GRAD.get(cat, f"linear-gradient(135deg,{C_ACTIVE},{C_DARK})")
    cat_lbl  = CAT_LABEL.get(cat, "")
    r_label  = REGION_LABELS.get(h.get("region_en", ""), h.get("region_en", ""))

    name_en_part = (
        f'<div style="font-size:11px;opacity:0.75;margin-bottom:6px">{h["name_en"]}</div>'
        if (h.get("name_ja") and h.get("name_en")) else ""
    )
    danger_badge = (
        '<span style="background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700">⚠️ 危機遺産</span>'
        if h.get("danger") else ""
    )
    st.markdown(
        f'<div style="background:{grad};border-radius:20px;padding:20px;margin-bottom:14px;color:white;box-shadow:0 4px 20px rgba(0,58,154,0.28)">'
        f'<div style="font-size:36px;margin-bottom:8px">{em}</div>'
        f'<div style="font-size:18px;font-weight:800;line-height:1.3;margin-bottom:6px">{name}</div>'
        f'{name_en_part}'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap">'
        f'<span style="background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700">{cat_lbl}</span>'
        f'{danger_badge}</div></div>',
        unsafe_allow_html=True,
    )

    area_part = (
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px;display:flex;align-items:center;gap:5px">{AREA_SVG} {h["area_hectares"]} ha</div>'
        if h.get("area_hectares") else ""
    )
    crit_part = (
        f'<div style="font-size:12px;color:{C_SUB};display:flex;align-items:center;gap:5px">{TAG_SVG} {h["criteria_txt"]}</div>'
        if h.get("criteria_txt") else ""
    )
    st.markdown(
        f'<div style="background:white;border-radius:18px;padding:14px 16px;margin-bottom:12px;box-shadow:0 2px 10px rgba(0,50,130,0.07)">'
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px;display:flex;align-items:center;gap:5px">{PIN_SVG} {h.get("states_name_en","")} · {r_label}</div>'
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px;display:flex;align-items:center;gap:5px">{CAL_SVG} {h.get("date_inscribed","")}年 UNESCO登録</div>'
        f'{area_part}{crit_part}</div>',
        unsafe_allow_html=True,
    )

    if h.get("description_en"):
        st.markdown(f'<div class="sec-row"><span class="sec-title">概要</span></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:13px;color:{C_TEXT};line-height:1.7;margin-bottom:14px">{h["description_en"]}</div>',
            unsafe_allow_html=True,
        )

    if h.get("latitude") and h.get("longitude"):
        st.map(pd.DataFrame([{"lat": float(h["latitude"]), "lon": float(h["longitude"])}]), zoom=4)

# ─── クイズ ──────────────────────────────────────────────────────
def page_quiz():
    screen_header("Quiz", f'<div class="h-icon">{BELL_SVG}</div>')

    def new_question():
        df = load_heritage_df()
        cols = ["id", "name_en", "name_ja", "states_name_en", "category", "region_en", "date_inscribed"]
        pool = df[
            df["name_ja"].notna() & (df["name_ja"] != "") &
            df["states_name_en"].notna() & (df["states_name_en"] != "")
        ][[c for c in cols if c in df.columns]].fillna("").to_dict("records")
        if len(pool) < 4:
            return
        correct = random.choice(pool)
        wrongs  = random.sample([h for h in pool if h["id"] != correct["id"]], 3)
        choices = [correct] + wrongs
        random.shuffle(choices)
        st.session_state.quiz_data     = {"correct": correct, "choices": choices}
        st.session_state.quiz_answered = False
        st.session_state.quiz_correct  = False

    if st.session_state.quiz_data is None:
        new_question()

    qd = st.session_state.quiz_data
    if qd is None:
        st.error("クイズデータの読み込みに失敗しました")
        return

    correct = qd["correct"]
    choices = qd["choices"]
    cat     = correct.get("category", "Cultural")
    em      = CAT_ICON.get(cat, "🌍")
    cat_lbl = CAT_LABEL.get(cat, "")

    score = st.session_state.quiz_score
    count = st.session_state.quiz_count
    if count > 0:
        st.markdown(
            f'<div style="background:white;border-radius:18px;padding:12px 16px;margin-bottom:12px;'
            f'box-shadow:0 2px 10px rgba(0,50,130,0.07);display:flex;align-items:center;justify-content:space-between">'
            f'<span style="font-size:13px;color:{C_SUB}">スコア</span>'
            f'<span style="font-size:20px;font-weight:800;color:{C_ACTIVE}">{score} / {count}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="quiz-q-card">'
        f'<div class="quiz-q-sup">{em} {cat_lbl} · この世界遺産がある国は？</div>'
        f'<div class="quiz-q-title">{disp(correct)}</div></div>',
        unsafe_allow_html=True,
    )

    answered     = st.session_state.quiz_answered
    selected_idx = st.session_state.get("quiz_selected_idx", -1)

    for i, choice in enumerate(choices):
        country           = choice.get("states_name_en", "")
        is_correct_choice = choice["id"] == correct["id"]
        if answered:
            if is_correct_choice:
                st.success(f"✅ {country}")
            elif i == selected_idx:
                st.error(f"❌ {country}")
            else:
                st.markdown(
                    f'<div style="background:white;border:1px solid #E8EFF8;border-radius:12px;'
                    f'padding:12px 16px;margin:6px 0;opacity:0.45;font-size:14px;color:{C_TEXT}">{country}</div>',
                    unsafe_allow_html=True,
                )
        else:
            if st.button(country, key=f"quiz_sel_{i}", use_container_width=True):
                st.session_state.quiz_answered     = True
                st.session_state.quiz_correct      = is_correct_choice
                st.session_state.quiz_selected_idx = i
                st.session_state.quiz_count       += 1
                if is_correct_choice:
                    st.session_state.quiz_score += 1
                st.rerun()

    if answered:
        msg = "🎉 正解！" if st.session_state.quiz_correct else f"😢 不正解…（正解: {correct.get('states_name_en','')}）"
        st.markdown(f"**{msg}**")
        if st.button("次の問題 →", use_container_width=True, type="primary"):
            st.session_state.quiz_data         = None
            st.session_state.quiz_selected_idx = -1
            st.rerun()

# ─── スタッツ ───────────────────────────────────────────────────
def page_stats():
    screen_header("Stats", f'<div class="h-icon">{BELL_SVG}</div>')

    score      = st.session_state.quiz_score
    count      = st.session_state.quiz_count
    level      = max(1, score // 5 + 1)
    level_name = ["Beginner", "Explorer", "Traveler", "Expert", "Master"][min(level - 1, 4)]
    fill_pct   = (score % 5) * 20

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{C_ACTIVE},{C_DARK});border-radius:20px;padding:24px;'
        f'margin-bottom:14px;text-align:center;color:white;box-shadow:0 4px 20px rgba(0,58,154,0.28)">'
        f'<div style="margin-bottom:8px;opacity:0.9">{TEMPLE_SVG}</div>'
        f'<div style="font-size:22px;font-weight:800;margin-bottom:4px">{level_name}</div>'
        f'<div style="font-size:13px;opacity:0.8">Lv.{level} · {score} XP</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lvl-card">'
        f'<div class="lvl-icon" style="display:flex;align-items:center;justify-content:center">{STAR_SVG}</div>'
        f'<div style="flex:1"><div class="lvl-name">クイズ正解率</div>'
        f'<div class="lvl-track"><div class="lvl-fill" style="width:{int(score/max(count,1)*100)}%"></div></div></div>'
        f'<div class="lvl-badge">{score}/{max(count,1)}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lvl-card">'
        f'<div class="lvl-icon" style="display:flex;align-items:center;justify-content:center">{TARGET_SVG}</div>'
        f'<div style="flex:1"><div class="lvl-name">次のレベルまで</div>'
        f'<div class="lvl-track"><div class="lvl-fill" style="width:{fill_pct}%"></div></div></div>'
        f'<div class="lvl-badge">{5 - score % 5} 問</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("スコアをリセット", use_container_width=True):
        st.session_state.quiz_score = 0
        st.session_state.quiz_count = 0
        st.rerun()

# ─── ボトムナビ ──────────────────────────────────────────────────
def bottom_nav():
    current = st.session_state.tab
    tabs = [("home", "Home"), ("list", "Sites"), ("quiz", "Quiz"), ("stats", "Stats")]

    def nav_svg(tab_key):
        s = 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        if tab_key == "home":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" {s}>'
                    f'<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
                    f'<polyline points="9 22 9 12 15 12 15 22"/></svg>')
        elif tab_key == "list":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" {s}>'
                    f'<circle cx="11" cy="11" r="8"/>'
                    f'<line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>')
        elif tab_key == "quiz":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" {s}>'
                    f'<circle cx="12" cy="12" r="10"/>'
                    f'<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>'
                    f'<line x1="12" y1="17" x2="12.01" y2="17"/></svg>')
        else:
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" {s}>'
                    f'<line x1="18" y1="20" x2="18" y2="10"/>'
                    f'<line x1="12" y1="20" x2="12" y2="4"/>'
                    f'<line x1="6" y1="20" x2="6" y2="14"/></svg>')

    nav_ctx = st.bottom if hasattr(st, "bottom") else st.container()
    with nav_ctx:
        cols = st.columns(4)
        for col, (tab_key, label) in zip(cols, tabs):
            active = current == tab_key or (tab_key == "list" and current == "detail")
            cls = "on" if active else ""
            with col:
                st.markdown(
                    f'<div class="nav-item-wrap {cls}">{nav_svg(tab_key)}'
                    f'<span>{label}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button("　", key=f"nav_{tab_key}", use_container_width=True):
                    st.session_state.tab = tab_key
                    st.rerun()

# ─── ルーティング ────────────────────────────────────────────────
inject_css()

tab = st.session_state.tab
if tab == "home":
    page_home()
elif tab == "detail":
    page_detail()
elif tab == "list":
    page_list()
elif tab == "quiz":
    page_quiz()
elif tab == "stats":
    page_stats()

bottom_nav()
