-- =====================================================
-- 足球场地预约系统 - time_slots 表创建脚本
-- 请在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- =====================================================

-- 1. 删除旧表（如果存在）并重新创建
DROP TABLE IF EXISTS time_slots CASCADE;

-- 创建 time_slots 表
CREATE TABLE time_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id UUID NOT NULL,
    date TEXT NOT NULL,
    field_name TEXT NOT NULL,
    time TEXT NOT NULL,
    price TEXT,
    remaining INTEGER,
    status TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(venue_id, date, time, field_name)
);

-- 2. 启用实时功能
ALTER PUBLICATION supabase_realtime ADD TABLE time_slots;

-- 3. 启用行级安全
ALTER TABLE time_slots ENABLE ROW LEVEL SECURITY;

-- 4. 创建访问策略（允许所有用户操作）
CREATE POLICY "Allow public read access" ON time_slots
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access" ON time_slots
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public delete access" ON time_slots
    FOR DELETE USING (true);

CREATE POLICY "Allow public update access" ON time_slots
    FOR UPDATE USING (true);

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_time_slots_venue_date ON time_slots(venue_id, date);
CREATE INDEX IF NOT EXISTS idx_time_slots_date ON time_slots(date);

-- 完成！
SELECT 'time_slots 表创建成功！' AS message;
