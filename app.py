import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="世界遺産アプリ",
    page_icon="🌍",
    layout="wide",
)

# ─── Supabase接続 ───────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )

supabase = get_supabase()

# ─── セッション初期化 ────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "list"
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None

# ─── ヘルパー ────────────────────────────────────────────────
def get_display_name(row: dict) -> str:
    return row.get("name_ja") or row.get("name_en", "")

REGION_LABELS = {
    "Africa":                          "アフリカ",
    "Arab States":                     "アラブ諸国",
    "Asia and the Pacific":            "アジア・太平洋",
    "Europe and North America":        "ヨーロッパ・北米",
    "Latin America and the Caribbean": "中南米・カリブ海",
}
CATEGORY_LABELS = {
    "Cultural": "文化遺産",
    "Natural":  "自然遺産",
    "Mixed":    "複合遺産",
}

def region_ja(r: str) -> str:
    return REGION_LABELS.get(r, r)

def category_ja(c: str) -> str:
    return CATEGORY_LABELS.get(c, c)

# ─── 認証UI ──────────────────────────────────────────────────
def auth_sidebar():
    with st.sidebar:
        st.markdown("### 🔑 アカウント")
        if st.session_state.user:
            email = st.session_state.user.email
            st.success(f"✅ {email}")
            if st.button("ログアウト", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.rerun()
        else:
            tab_in, tab_up = st.tabs(["ログイン", "新規登録"])
            with tab_in:
                email = st.text_input("メールアドレス", key="li_email")
                pw    = st.text_input("パスワード", type="password", key="li_pw")
                if st.button("ログイン", use_container_width=True):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        st.error(f"ログイン失敗: {e}")
            with tab_up:
                email = st.text_input("メールアドレス", key="su_email")
                pw    = st.text_input("パスワード（6文字以上）", type="password", key="su_pw")
                if st.button("登録", use_container_width=True):
                    try:
                        res = supabase.auth.sign_up({"email": email, "password": pw})
                        st.info("確認メールを送りました。メールのリンクをクリックしてください。")
                    except Exception as e:
                        st.error(f"登録失敗: {e}")

# ─── 一覧ページ ──────────────────────────────────────────────
def page_list():
    st.title("🌍 世界遺産データベース")
    st.caption(f"UNESCO登録 全 1,223 件")

    # フィルター
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        keyword = st.text_input("🔍 キーワード検索（日本語・英語・国名）", placeholder="例：日本、Italy、forest")
    with col2:
        region_opts = ["すべて"] + list(REGION_LABELS.keys())
        region_sel  = st.selectbox("地域", region_opts, format_func=lambda x: "すべて" if x == "すべて" else region_ja(x))
    with col3:
        cat_opts = ["すべて"] + list(CATEGORY_LABELS.keys())
        cat_sel  = st.selectbox("種別", cat_opts, format_func=lambda x: "すべて" if x == "すべて" else category_ja(x))

    # クエリ構築
    query = supabase.table("heritage").select(
        "id, unique_number, name_en, name_ja, category, category_short, "
        "states_name_en, region_en, date_inscribed, danger"
    ).order("date_inscribed")

    if region_sel != "すべて":
        query = query.eq("region_en", region_sel)
    if cat_sel != "すべて":
        query = query.eq("category", cat_sel)
    if keyword:
        kw = keyword.strip()
        query = query.or_(
            f"name_ja.ilike.%{kw}%,"
            f"name_en.ilike.%{kw}%,"
            f"states_name_en.ilike.%{kw}%"
        )

    query = query.limit(200)
    res   = query.execute()
    rows  = res.data

    st.markdown(f"**{len(rows)} 件**{'（上限200件）' if len(rows) == 200 else ''}")

    # テーブル表示
    for row in rows:
        name    = get_display_name(row)
        cat_lbl = category_ja(row.get("category", ""))
        country = row.get("states_name_en", "")
        year    = row.get("date_inscribed", "")
        danger  = "⚠️ " if row.get("danger") else ""

        with st.container():
            c1, c2 = st.columns([5, 1])
            with c1:
                badge = {"Cultural": "🏛️", "Natural": "🌿", "Mixed": "✨"}.get(row.get("category",""), "🌍")
                st.markdown(f"{badge} **{danger}{name}**  \n"
                            f"<small>{cat_lbl} ｜ {country} ｜ {year}年登録</small>",
                            unsafe_allow_html=True)
            with c2:
                if st.button("詳細", key=f"btn_{row['id']}"):
                    st.session_state.selected_id = row["id"]
                    st.session_state.page = "detail"
                    st.rerun()
        st.divider()

# ─── 詳細ページ ──────────────────────────────────────────────
def page_detail():
    hid = st.session_state.selected_id
    res = supabase.table("heritage").select("*").eq("id", hid).single().execute()
    h   = res.data

    if st.button("← 一覧に戻る"):
        st.session_state.page = "list"
        st.rerun()

    name = get_display_name(h)
    st.title(name)
    if h.get("name_en") and h.get("name_ja"):
        st.caption(h["name_en"])

    col1, col2 = st.columns([3, 2])
    with col1:
        badges = []
        cat = h.get("category", "")
        if cat:
            badges.append(f"{'🏛️' if cat=='Cultural' else '🌿' if cat=='Natural' else '✨'} {category_ja(cat)}")
        if h.get("danger"):
            badges.append("⚠️ 危機遺産")
        st.markdown("　".join(badges))

        if h.get("description_en"):
            st.markdown("#### 概要")
            st.write(h["description_en"])

        if h.get("criteria_txt"):
            st.markdown(f"**選定基準：** {h['criteria_txt']}")

    with col2:
        st.markdown("#### 基本情報")
        info = {
            "国": h.get("states_name_en", ""),
            "地域": region_ja(h.get("region_en", "")),
            "登録年": f"{h.get('date_inscribed', '')}年",
            "面積": f"{h.get('area_hectares', '')} ha" if h.get("area_hectares") else "—",
        }
        for k, v in info.items():
            st.markdown(f"**{k}：** {v}")

        if h.get("latitude") and h.get("longitude"):
            st.markdown("#### 地図")
            import pandas as pd
            df = pd.DataFrame([{"lat": h["latitude"], "lon": h["longitude"]}])
            st.map(df)

    # お気に入りボタン
    st.divider()
    if st.session_state.user:
        uid = st.session_state.user.id
        fav = supabase.table("favorites").select("id").eq("heritage_id", hid).eq("user_id", uid).execute()
        is_fav = len(fav.data) > 0
        if is_fav:
            if st.button("❤️ お気に入り解除"):
                supabase.table("favorites").delete().eq("heritage_id", hid).eq("user_id", uid).execute()
                st.rerun()
        else:
            if st.button("🤍 お気に入りに追加"):
                supabase.table("favorites").insert({"heritage_id": hid, "user_id": uid}).execute()
                st.rerun()
    else:
        st.info("お気に入り登録はログイン後に利用できます")

    # コメント
    st.markdown("### 💬 コメント")
    comments_res = supabase.table("comments").select("*").eq("heritage_id", hid).order("created_at").execute()
    comments = comments_res.data

    if comments:
        for c in comments:
            with st.chat_message("user"):
                st.markdown(f"**{c.get('user_email','匿名')}**　{c.get('created_at','')[:10]}")
                st.write(c["body"])
    else:
        st.caption("まだコメントはありません")

    if st.session_state.user:
        with st.form("comment_form", clear_on_submit=True):
            body = st.text_area("コメントを書く", placeholder="この世界遺産について...")
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

# ─── ルーティング ────────────────────────────────────────────
auth_sidebar()

if st.session_state.page == "list":
    page_list()
elif st.session_state.page == "detail":
    page_detail()
