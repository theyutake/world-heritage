# 世界遺産アプリ ステータス

最終更新: 2026-05-22

---

## デプロイ情報

| 項目 | 値 |
|---|---|
| 公開URL | https://world-heritage-6xg7.onrender.com |
| プラットフォーム | Render（無料プラン・スリープあり） |
| リポジトリ | https://github.com/theyutake/world-heritage |
| DB/Auth | Supabase（`lqgzjdhbmktwkkeiqirb`） |
| Pythonバージョン | 3.11（runtime.txt で固定） |
| Streamlit | 1.45.0 |
| supabase-py | 2.30.0 |

---

## 実装済み機能

- **Homeタブ**: 今日の遺産カード・クイズ進捗・DB統計・地域一覧
- **Sitesタブ**: 一覧（地域/種別フィルター・キーワード検索）・遺産カード（年登録・criteria表示）
- **詳細ページ**: 遺産情報・地図・お気に入り・コメント投稿
- **Quizタブ**: ランダム4択（国名当て）・スコア管理
- **Profileタブ**: ログイン/新規登録・お気に入り一覧・ログアウト
- **UIテーマ**: design.html ベースのライトテーマ（#0096D6 × #003DA5）
- **キャッシュ**: `@st.cache_data(ttl=300)` で主要クエリをキャッシュ済み

---

## 未解決の問題

### ❌ フッターナビのクリック不可（最優先）

**状況**: SVGアイコンは `position:fixed` で表示されているが、クリックが反応しない。

**原因の経緯**:
1. `st.bottom` が Render 環境（Python 3.14）で使えなかった
2. Python 3.11 に固定 → まだ未確認
3. `st.bottom` がない場合のフォールバックを `st.container()` にしたが、透明ボタンが `.bnav` と重ならず機能しない

**次回試すこと**:
- Python 3.11 + streamlit 1.45.0 の組み合わせで `st.bottom` が使えるか確認
- もし `st.bottom` が使えない場合は、フッターボタンを `position:fixed` CSS で `.bnav` に重ねる方式を検討

**関係するコード**:
- `bottom_nav()` 関数（app.py 末尾付近）
- `.bnav` CSS（`inject_css()` 内）

---

### △ フッターボタンが黒く見える（ローカル）

ローカルでは `st.bottom` は動くが、透明ボタンが完全に透明にならず黒く見える。  
`opacity: 0` + `background: transparent` を各ラッパー層に適用済みだが、まだ残っている可能性。

---

## 環境変数（Render）

Render ダッシュボード → Environment に設定済み:
- `SUPABASE_URL`
- `SUPABASE_KEY`

ローカルは `.streamlit/secrets.toml`（gitignore 除外済み）で管理。

---

## ファイル構成

```
world-heritage/
├── app.py              # メインアプリ（951行）
├── requirements.txt    # streamlit==1.45.0, supabase==2.30.0
├── runtime.txt         # python-3.11.0
├── supabase_schema.sql # テーブル定義・RLS・GRANT
├── design.html         # UIモックアップ（参考資料）
└── .streamlit/
    └── secrets.toml    # ローカル用（gitignore）
```

---

## Phase 2 残タスク

- [ ] フッターナビのクリック修正（上記）
- [ ] Supabase管理画面でテストユーザー作成・ログイン動作確認
- [ ] Renderスリープ対策（有料プラン or UptimeRobot で定期ping）

Phase 2 完成定義：「公開URLで全機能が動作すること」
