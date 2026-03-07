-- =====================================================
-- 足球场地预约系统 - 完整数据库创建脚本
-- 请在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- 此脚本可重复执行，不会出错
-- =====================================================

-- 1. 删除旧表（如果存在）并重新创建
DROP TABLE IF EXISTS bookings CASCADE;

-- 创建预约表
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue TEXT NOT NULL CHECK (venue IN ('cage', 'pool')),
    date TEXT NOT NULL,
    time_slot INTEGER NOT NULL CHECK (time_slot >= 14 AND time_slot <= 21),
    remark TEXT DEFAULT '',
    status TEXT DEFAULT 'available' CHECK (status IN ('available', 'booked')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(venue, date, time_slot)
);

-- 2. 启用实时功能
ALTER PUBLICATION supabase_realtime ADD TABLE bookings;

-- 3. 启用行级安全
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- 4. 创建访问策略（允许所有用户操作）
CREATE POLICY "Allow public read access" ON bookings
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access" ON bookings
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public delete access" ON bookings
    FOR DELETE USING (true);

CREATE POLICY "Allow public update access" ON bookings
    FOR UPDATE USING (true);

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_bookings_venue_date ON bookings(venue, date);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);

-- 完成！
SELECT '数据库创建成功！' AS message;
