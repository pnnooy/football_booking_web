-- 足球场地预约系统 - 修复脚本
-- 如果你的 bookings 表已存在但缺少字段，执行此脚本

-- 1. 添加 remark 字段（如果不存在）
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS remark TEXT DEFAULT '';

-- 2. 添加 status 字段（如果不存在）
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'available';

-- 3. 添加 CHECK 约束（忽略如果已存在）
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_status_check;
ALTER TABLE bookings ADD CONSTRAINT bookings_status_check CHECK (status IN ('available', 'booked'));

-- 4. 将已有记录的 status 设置为 'booked'（因为旧数据有记录就算已预约）
UPDATE bookings SET status = 'booked' WHERE status IS NULL OR status = '';

-- 5. 确保字段有默认值
ALTER TABLE bookings ALTER COLUMN remark SET DEFAULT '';
ALTER TABLE bookings ALTER COLUMN status SET DEFAULT 'available';

-- 6. 启用实时功能（检查是否已存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
        AND tablename = 'bookings'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE bookings;
    END IF;
END $$;

-- 7. 启用行级安全（如果未启用）
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- 8. 创建访问策略（先删除旧的）
DROP POLICY IF EXISTS "Allow public read access" ON bookings;
DROP POLICY IF EXISTS "Allow public insert access" ON bookings;
DROP POLICY IF EXISTS "Allow public delete access" ON bookings;
DROP POLICY IF EXISTS "Allow public update access" ON bookings;

-- 允许所有用户读取
CREATE POLICY "Allow public read access" ON bookings FOR SELECT USING (true);

-- 允许所有用户插入
CREATE POLICY "Allow public insert access" ON bookings FOR INSERT WITH CHECK (true);

-- 允许所有用户删除
CREATE POLICY "Allow public delete access" ON bookings FOR DELETE USING (true);

-- 允许所有用户更新
CREATE POLICY "Allow public update access" ON bookings FOR UPDATE USING (true);

-- 9. 创建索引
CREATE INDEX IF NOT EXISTS idx_bookings_venue_date ON bookings(venue, date);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
