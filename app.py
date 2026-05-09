import random
import streamlit as st
from supabase import create_client, Client

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
    /* ── Bottom nav：HTML nav + position:absolute オーバーレイ方式 ── */
    div[data-testid="stBottom"] > div {{
        position: relative !important;
        padding: 0 !important;
        height: 68px !important;
        max-width: 480px;
        margin: 0 auto;
        overflow: hidden;
    }}
    /* HTML ナビ（見た目レイヤー, z-index:1） */
    .bnav {{
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 68px;
        background: #fff;
        border-top: 1px solid #EDF2F8;
        box-shadow: 0 -2px 16px rgba(0,50,130,0.08);
        display: flex; align-items: center; justify-content: space-around;
        padding: 0 4px 10px;
        z-index: 1;
    }}
    .n-item {{
        display: flex; flex-direction: column; align-items: center; gap: 3px;
        font-size: 9px; font-weight: 700; color: {C_INACTIVE};
        min-width: 56px;
    }}
    .n-item.on {{ color: {C_ACTIVE}; }}
    /* ボタンレイヤー（クリック用, z-index:20）を nav 上に重ねる */
    div[data-testid="stBottom"] [data-testid="stHorizontalBlock"],
    div[data-testid="stBottom"] [data-testid="stColumns"] {{
        position: absolute !important;
        top: 0 !important; left: 0 !important; right: 0 !important;
        height: 68px !important;
        z-index: 20 !important;
        gap: 0 !important; padding: 0 !important; margin: 0 !important;
        background: transparent !important;
    }}
    div[data-testid="stBottom"] [data-testid="stColumn"],
    div[data-testid="stBottom"] [data-testid="stVerticalBlock"] {{
        padding: 0 !important; gap: 0 !important;
        min-width: 0 !important; height: 68px !important;
        background: transparent !important;
    }}
    div[data-testid="stBottom"] .element-container {{
        margin: 0 !important; padding: 0 !important; height: 68px !important;
        background: transparent !important;
    }}
    div[data-testid="stBottom"] [data-testid="stButton"] {{
        background: transparent !important;
    }}
    div[data-testid="stBottom"] [data-testid="stButton"] > button {{
        background: transparent !important;
        border: none !important; border-radius: 0 !important;
        box-shadow: none !important;
        color: transparent !important;
        height: 68px !important; width: 100% !important;
        padding: 0 !important; margin: 0 !important;
        cursor: pointer !important;
        opacity: 0 !important;
    }}
    div[data-testid="stBottom"] [data-testid="stButton"] > button:hover,
    div[data-testid="stBottom"] [data-testid="stButton"] > button:focus,
    div[data-testid="stBottom"] [data-testid="stButton"] > button:active {{
        background: transparent !important;
        border: none !important; box-shadow: none !important;
        opacity: 0 !important;
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

# ─── Supabase ─────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

# ─── セッション ───────────────────────────────────────────────────
def init_session():
    defaults = {
        "user": None, "tab": "home", "selected_id": None,
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

SEARCH_SVG = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'
BELL_SVG   = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'
FILTER_SVG = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#5C7A98" stroke-width="2" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="12" y1="18" x2="20" y2="18"/></svg>'

def screen_header(title, icons_html=""):
    st.markdown(
        f'<div class="screen-header"><span class="screen-title">{title}</span>'
        f'<div class="h-icons">{icons_html}</div></div>',
        unsafe_allow_html=True,
    )

# ─── ホーム ──────────────────────────────────────────────────────
def page_home():
    screen_header("Home", f'<div class="h-icon">{BELL_SVG}</div>')

    res = supabase.table("heritage").select(
        "id,name_en,name_ja,category,states_name_en,date_inscribed,region_en,danger"
    ).limit(1200).execute()
    all_h = res.data or []

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

    total_cnt = supabase.table("heritage").select("id", count="exact").execute().count or 0
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

    query = supabase.table("heritage").select(
        "id,name_en,name_ja,category,states_name_en,region_en,date_inscribed,danger,criteria_txt"
    ).order("date_inscribed")
    if region_sel != "すべて":
        query = query.eq("region_en", region_sel)
    if cat_sel != "すべて":
        query = query.eq("category", cat_sel)
    if kw:
        query = query.or_(f"name_ja.ilike.%{kw}%,name_en.ilike.%{kw}%,states_name_en.ilike.%{kw}%")
    rows = query.limit(200).execute().data

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
    h   = supabase.table("heritage").select("*").eq("id", hid).single().execute().data

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
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px">📐 {h["area_hectares"]} ha</div>'
        if h.get("area_hectares") else ""
    )
    crit_part = (
        f'<div style="font-size:12px;color:{C_SUB}">🏷️ {h["criteria_txt"]}</div>'
        if h.get("criteria_txt") else ""
    )
    st.markdown(
        f'<div style="background:white;border-radius:18px;padding:14px 16px;margin-bottom:12px;box-shadow:0 2px 10px rgba(0,50,130,0.07)">'
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px">🌐 {h.get("states_name_en","")} · {r_label}</div>'
        f'<div style="font-size:12px;color:{C_SUB};margin-bottom:4px">📅 {h.get("date_inscribed","")}年 UNESCO登録</div>'
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
        import pandas as pd
        st.map(pd.DataFrame([{"lat": float(h["latitude"]), "lon": float(h["longitude"])}]), zoom=4)

    st.divider()
    if st.session_state.user:
        uid   = st.session_state.user.id
        fav   = supabase.table("favorites").select("id").eq("heritage_id", hid).eq("user_id", uid).execute()
        is_fav = len(fav.data) > 0
        if st.button("❤️ お気に入り解除" if is_fav else "🤍 お気に入りに追加", use_container_width=True):
            if is_fav:
                supabase.table("favorites").delete().eq("heritage_id", hid).eq("user_id", uid).execute()
            else:
                supabase.table("favorites").insert({"heritage_id": hid, "user_id": uid}).execute()
            st.rerun()
    else:
        st.info("お気に入り登録はログイン後に利用できます")

    st.markdown(f'<div class="sec-row"><span class="sec-title">💬 コメント</span></div>', unsafe_allow_html=True)
    comments = supabase.table("comments").select("*").eq("heritage_id", hid).order("created_at").execute().data
    if comments:
        for c in comments:
            with st.chat_message("user"):
                st.markdown(f"**{c.get('user_email','匿名')}** {c.get('created_at','')[:10]}")
                st.write(c["body"])
    else:
        st.caption("まだコメントはありません")

    if st.session_state.user:
        with st.form("comment_form", clear_on_submit=True):
            body = st.text_area("コメントを書く", placeholder="この世界遺産について…")
            if st.form_submit_button("投稿") and body.strip():
                supabase.table("comments").insert({
                    "heritage_id": hid,
                    "user_id":     st.session_state.user.id,
                    "user_email":  st.session_state.user.email,
                    "body":        body.strip(),
                }).execute()
                st.rerun()
    else:
        st.info("コメント投稿はログイン後に利用できます")

# ─── クイズ ──────────────────────────────────────────────────────
def page_quiz():
    screen_header("Quiz", f'<div class="h-icon">{BELL_SVG}</div>')

    def new_question():
        res  = supabase.table("heritage").select(
            "id,name_en,name_ja,states_name_en,category,region_en,date_inscribed"
        ).limit(500).execute()
        pool = [h for h in res.data if h.get("name_ja") and h.get("states_name_en")]
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

# ─── プロフィール ────────────────────────────────────────────────
def page_profile():
    screen_header("Profile", f'<div class="h-icon">{BELL_SVG}</div>')

    if st.session_state.user:
        email      = st.session_state.user.email
        score      = st.session_state.quiz_score
        level      = max(1, score // 5 + 1)
        level_name = ["Beginner", "Explorer", "Traveler", "Expert", "Master"][min(level - 1, 4)]
        st.markdown(
            f'<div style="background:linear-gradient(135deg,{C_ACTIVE},{C_DARK});border-radius:20px;padding:24px;'
            f'margin-bottom:14px;text-align:center;color:white;box-shadow:0 4px 20px rgba(0,58,154,0.28)">'
            f'<div style="font-size:48px;margin-bottom:8px">👤</div>'
            f'<div style="font-size:15px;font-weight:700;margin-bottom:4px">{email}</div>'
            f'<div style="font-size:11px;opacity:0.75">{level_name} · Lv.{level} · {score} XP</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("ログアウト", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        st.markdown('<div class="sec-row"><span class="sec-title">❤️ お気に入り</span></div>', unsafe_allow_html=True)
        favs = supabase.table("favorites").select("heritage_id").eq("user_id", st.session_state.user.id).execute().data
        if favs:
            ids   = [f["heritage_id"] for f in favs]
            hlist = supabase.table("heritage").select("id,name_en,name_ja,category,states_name_en").in_("id", ids).execute().data
            for h in hlist:
                cat  = h.get("category", "Cultural")
                grad = CAT_GRAD.get(cat, f"linear-gradient(135deg,{C_ACTIVE},{C_DARK})")
                em   = CAT_ICON.get(cat, "🌍")
                st.markdown(
                    f'<div class="hcard">'
                    f'<div class="hthumb" style="background:{grad}">{em}</div>'
                    f'<div><div class="hcard-title">{disp(h)}</div>'
                    f'<div class="hcard-loc">📍 {h.get("states_name_en","")}</div></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("詳細", key=f"fav_{h['id']}"):
                    st.session_state.selected_id = h["id"]
                    st.session_state.detail_from = "profile"
                    st.session_state.tab = "detail"
                    st.rerun()
        else:
            st.caption("お気に入りはまだありません")
    else:
        st.markdown(
            f'<div style="background:{C_ICON_BG};border-radius:20px;padding:24px;text-align:center;margin-bottom:16px">'
            f'<div style="font-size:48px">🌍</div>'
            f'<div style="font-size:15px;font-weight:700;color:{C_TEXT};margin-top:8px">ログインして記録を保存</div>'
            f'<div style="font-size:12px;color:{C_SUB};margin-top:4px">お気に入り・コメント機能が使えます</div></div>',
            unsafe_allow_html=True,
        )
        tab_in, tab_up = st.tabs(["ログイン", "新規登録"])
        with tab_in:
            email_in = st.text_input("メールアドレス", key="li_email")
            pw_in    = st.text_input("パスワード", type="password", key="li_pw")
            if st.button("ログイン", use_container_width=True, type="primary", key="login_btn"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_in, "password": pw_in})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error(f"ログイン失敗: {e}")
        with tab_up:
            email_up = st.text_input("メールアドレス", key="su_email")
            pw_up    = st.text_input("パスワード（6文字以上）", type="password", key="su_pw")
            if st.button("新規登録", use_container_width=True, type="primary", key="signup_btn"):
                try:
                    supabase.auth.sign_up({"email": email_up, "password": pw_up})
                    st.info("確認メールを送りました。メールのリンクをクリックしてください。")
                except Exception as e:
                    st.error(f"登録失敗: {e}")

# ─── ボトムナビ（HTML nav + 透明ボタンオーバーレイ） ────────────────
def bottom_nav():
    current = st.session_state.tab
    is_list = current in ("list", "detail")

    def nav_svg(tab_key, active):
        color = C_ACTIVE if active else C_INACTIVE
        if tab_key == "home":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="{color}">'
                    f'<path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>')
        elif tab_key == "list":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="{color}">'
                    f'<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13'
                    f'c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5'
                    f' 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>')
        elif tab_key == "quiz":
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"'
                    f' stroke="{color}" stroke-width="2" stroke-linecap="round">'
                    f'<circle cx="12" cy="12" r="10"/>'
                    f'<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>'
                    f'<line x1="12" y1="17" x2="12.01" y2="17"/></svg>')
        else:
            return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none"'
                    f' stroke="{color}" stroke-width="1.8">'
                    f'<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
                    f'<circle cx="12" cy="7" r="4"/></svg>')

    tabs = [("home", "Home"), ("list", "Sites"), ("quiz", "Quiz"), ("profile", "Profile")]
    nav_items = ""
    for tab_key, label in tabs:
        active = (current == tab_key) or (tab_key == "list" and is_list)
        cls = "n-item on" if active else "n-item"
        nav_items += f'<div class="{cls}">{nav_svg(tab_key, active)}<span>{label}</span></div>'

    with st.bottom:
        st.markdown(f'<div class="bnav">{nav_items}</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for col, (tab_key, label) in zip(cols, tabs):
            if col.button("　", key=f"nav_{tab_key}", help=label, use_container_width=True):
                st.session_state.tab = tab_key
                st.session_state.show_search = False
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
elif tab == "profile":
    page_profile()

bottom_nav()
