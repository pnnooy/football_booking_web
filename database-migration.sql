-- 迁移脚本：添加 status 字段
-- 如果你的数据库已经存在，运行此脚本添加 status 字段

-- 添加 status 字段（如果不存在）
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'available' CHECK (status IN ('available', 'booked'));

-- 将已有记录的 status 设置为 'booked'（因为旧数据有记录就算已预约）
UPDATE bookings SET status = 'booked' WHERE status IS NULL OR status = '';

-- 确保 status 字段有默认值
ALTER TABLE bookings ALTER COLUMN status SET DEFAULT 'available';

-- 修复：确保remark字段有默认值
ALTER TABLE bookings ALTER COLUMN remark SET DEFAULT '';
