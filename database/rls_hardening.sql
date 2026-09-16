-- =====================================================
-- RLS 收紧迁移脚本: 移除匿名用户的写权限
-- 请在 Supabase Dashboard 的 SQL Editor 中执行
--
-- 背景: bookings / time_slots 原策略允许任何人用公开的
-- anon key 增删改全部数据, 存在数据被任意篡改/清空的风险
-- 爬虫使用 service_role 密钥 (绕过RLS), 此变更不影响爬虫
-- =====================================================

-- 1. bookings: 删除公开写策略, 改为仅登录管理员可写
DROP POLICY IF EXISTS "Allow public insert access" ON bookings;
DROP POLICY IF EXISTS "Allow public update access" ON bookings;
DROP POLICY IF EXISTS "Allow public delete access" ON bookings;

DROP POLICY IF EXISTS "Allow admin write access" ON bookings;
CREATE POLICY "Allow admin write access" ON bookings
    FOR ALL TO authenticated
    USING (true) WITH CHECK (true);

-- 2. time_slots: 删除全部公开写策略 (爬虫用service_role, 不受影响)
DROP POLICY IF EXISTS "Allow public insert access" ON time_slots;
DROP POLICY IF EXISTS "Allow public update access" ON time_slots;
DROP POLICY IF EXISTS "Allow public delete access" ON time_slots;

-- 3. 自查: 列出所有表的全开写策略
--    feedback / want_to_play 等手动建的表不在本仓库,
--    请核对输出确认写权限是否符合预期
SELECT schemaname, tablename, policyname, cmd, roles
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, cmd;
