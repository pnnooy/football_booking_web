-- =====================================================
-- RLS 第二步: 修正"名为仅认证、实则对public全开"的策略
-- 请在 Supabase Dashboard 的 SQL Editor 中执行
--
-- 判据: pg_policies 里这些策略 roles={public}, 若
-- qual/with_check 也没有 auth.role() 校验, 则匿名可写
-- (爬虫走 service_role 绕过RLS, 本脚本不影响爬虫)
-- =====================================================

-- 0. 先执行这个核查查询, 确认问题属实 (可选)
SELECT tablename, policyname, cmd, roles, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('feedback', 'time_slots')
ORDER BY tablename, cmd;

-- 1. time_slots: 删除全操作策略 (爬虫走service_role, 不受RLS约束)
DROP POLICY IF EXISTS "仅认证用户可操作 time_slots" ON time_slots;

-- 1.1 顺带清理与 "Allow public read access" 重复的读策略 (二选一保留)
DROP POLICY IF EXISTS "允许公开查询 time_slots" ON time_slots;

-- 2. feedback: 查看/更新/删除仅限登录管理员
--    (用户提交反馈的 INSERT 保持公开; 前端只在管理员登录后拉取列表)
DROP POLICY IF EXISTS "仅认证用户可查看反馈" ON feedback;
CREATE POLICY "仅认证用户可查看反馈" ON feedback
    FOR SELECT TO authenticated
    USING (true);

DROP POLICY IF EXISTS "仅认证用户可更新反馈" ON feedback;
CREATE POLICY "仅认证用户可更新反馈" ON feedback
    FOR UPDATE TO authenticated
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "仅认证用户可删除反馈" ON feedback;
CREATE POLICY "仅认证用户可删除反馈" ON feedback
    FOR DELETE TO authenticated
    USING (true);

-- 3. want_to_play: 保持现状 (前端"想踢"用匿名upsert计数, 公开增改是设计需要)
