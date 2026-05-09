-- ========================================
-- 世界遺産アプリ Supabase テーブル設計
-- Supabase SQL Editor で実行する
-- ========================================

-- 世界遺産テーブル（UNESCO公式フォーマット準拠）
CREATE TABLE heritage (
  id              SERIAL PRIMARY KEY,
  unique_number   INTEGER UNIQUE NOT NULL,  -- WHC固有ID
  id_no           INTEGER,                  -- UNESCO ID
  name_en         TEXT NOT NULL,
  name_fr         TEXT,
  name_ja         TEXT,
  description_en  TEXT,                     -- HTMLタグ除去済み説明文
  date_inscribed  INTEGER,                  -- 登録年
  danger          BOOLEAN DEFAULT FALSE,    -- 危機遺産フラグ
  longitude       NUMERIC,
  latitude        NUMERIC,
  area_hectares   NUMERIC,
  criteria_txt    TEXT,                     -- (i)(ii)(iii)形式の選定基準
  category        TEXT,                     -- Cultural / Natural / Mixed
  category_short  TEXT,                     -- C / N / M
  states_name_en  TEXT,                     -- 国名（英語）
  region_en       TEXT,                     -- 地域（Asia and the Pacific 等）
  iso_code        TEXT,                     -- ISO国コード
  transboundary   BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMP DEFAULT NOW()
);

-- コメントテーブル
CREATE TABLE comments (
  id           SERIAL PRIMARY KEY,
  heritage_id  INTEGER REFERENCES heritage(id) ON DELETE CASCADE,
  user_id      UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  user_email   TEXT,
  body         TEXT NOT NULL,
  created_at   TIMESTAMP DEFAULT NOW()
);

-- お気に入りテーブル
CREATE TABLE favorites (
  id          SERIAL PRIMARY KEY,
  heritage_id INTEGER REFERENCES heritage(id) ON DELETE CASCADE,
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at  TIMESTAMP DEFAULT NOW(),
  UNIQUE(heritage_id, user_id)
);

-- ========================================
-- Row Level Security (RLS) 設定
-- ========================================

ALTER TABLE heritage ENABLE ROW LEVEL SECURITY;
CREATE POLICY "heritage_read_all" ON heritage FOR SELECT USING (true);

ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "comments_read_all"   ON comments FOR SELECT USING (true);
CREATE POLICY "comments_insert_own" ON comments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "comments_delete_own" ON comments FOR DELETE USING (auth.uid() = user_id);

ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
CREATE POLICY "favorites_read_own"   ON favorites FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "favorites_insert_own" ON favorites FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "favorites_delete_own" ON favorites FOR DELETE USING (auth.uid() = user_id);
