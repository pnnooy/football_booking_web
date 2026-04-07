# 足球场地预约看板

一个简洁美观的足球场地预约情况看板系统，帮助你快速查看和预约足球场地。

## 功能特性

- 📅 **日期选择** - 支持查看未来8天的场地预约情况
- ⚽ **笼式足球场** - 专注于笼式足球场预约
- 🌤️ **天气预报** - 集成和风天气API，显示7日预报和逐小时天气
- 🔒 **密码保护** - 预约和取消操作需要管理员密码
- ✍️ **备注功能** - 长按时段可添加备注信息
- 🔄 **实时同步** - Supabase实时数据同步
- 🐛 **爬虫同步** - GitHub Actions自动爬取场地状态

## 技术栈

- **前端框架**: Vue 3 + Vite
- **后端服务**: Supabase
- **天气服务**: 和风天气API
- **部署平台**: Vercel
- **爬虫**: Python + Playwright

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目配置

### Supabase配置

需要配置以下环境变量：

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 天气API配置

使用和风天气API，已配置：
- API Key: 内置
- API Host: 自定义域名

## 数据库结构

### bookings表
用户预约记录表

### time_slots表
爬虫同步的场地实际状态表

详细的数据库脚本请查看项目根目录下的SQL文件。

## GitHub Actions爬虫

项目包含自动爬虫工作流，定期同步场地状态到Supabase。

爬虫配置位于：`.github/workflows/`

爬虫代码位于：`sjtu_crawler_auto.py`

## 部署

项目已配置Vercel自动部署，推送到main分支会自动触发部署。

## 许可证

MIT License

## 项目链接

- GitHub仓库: https://github.com/pnnooy/football_booking_web
