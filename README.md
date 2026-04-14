<div align="center">

# 🏟️ 足球场地预约看板 | Football Pitch Booking Board

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/pnnooy/football_booking_web/blob/main/LICENSE)
[![Vue 3](https://img.shields.io/badge/Vue-3.5.25-brightgreen.svg)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3.1-purple.svg)](https://vitejs.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-2.98.0-blue.svg)](https://supabase.io/)

**[English](docs/README-en.md) | [中文](#)**

</div>

---

## 目录

- [项目介绍](#项目介绍)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目配置](#项目配置)
- [数据库结构](#数据库结构)
- [部署说明](#部署说明)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [许可证](#许可证)
- [开发者信息](#开发者信息)

---

## 项目介绍

足球场地预约看板是一个简洁美观的足球场地预约情况实时查看系统，帮助用户快速了解场地预约状态。集成实时天气查询、想踢人数登记、预约分享等功能，为足球爱好者提供便捷的信息服务。

### 核心亮点

- 📱 响应式设计，完美适配移动端
- 🌙 支持浅色/深色/跟随系统三种主题
- ⚡ 实时数据同步，快速响应
- 🎨 精美的UI设计，流畅的交互体验

---

## 功能特性

### 用户功能

| 功能 | 描述 |
|------|------|
| 📅 **日期选择** | 查看未来8天的场地预约情况 |
| 🌤️ **天气预报** | 集成和风天气API，显示7日预报和逐小时天气 |
| ⚽ **想踢登记** | 点击时段登记踢球意向，方便组织者统计 |
| 📸 **分享功能** | 导出当前预约情况为图片，支持保存和分享 |
| 🎨 **主题切换** | 支持浅色/深色/跟随系统三种主题 |
| 📝 **反馈建议** | 提交问题反馈和功能建议 |

### 管理员功能

| 功能 | 描述 |
|------|------|
| 🔐 **管理员登录** | 邮箱密码登录，访问管理功能 |
| ✏️ **时段管理** | 修改时段状态（可预约/已预约）、添加备注 |
| 👥 **想踢管理** | 编辑想踢人数 |
| 📋 **反馈管理** | 查看和处理用户反馈与建议 |

### 系统特性

| 功能 | 描述 |
|------|------|
| 🔄 **实时同步** | Supabase实时数据同步 |
| 🐛 **自动爬虫** | GitHub Actions自动同步场地状态 |
| ⏱️ **天气缓存** | 天气数据每10分钟自动更新 |
| 📱 **微信优化** | 针对微信浏览器优化图片分享 |

---

## 技术栈

### 前端技术

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 7
- **UI**: 原生 CSS3 + Flexbox/Grid
- **截图**: html2canvas 1.4.1

### 后端服务

- **BaaS**: Supabase (PostgreSQL + Auth + Realtime)
- **天气API**: 和风天气 (QWeather)
- **部署**: Vercel

### 爬虫技术

- **语言**: Python 3
- **浏览器自动化**: Playwright
- **HTTP请求**: requests
- **定时任务**: GitHub Actions

---

## 快速开始

### 前置要求

- Node.js 18+
- npm 或 pnpm
- Python 3.8+ (如需运行爬虫)

### 安装依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm
pnpm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173 查看应用。

### 生产构建

```bash
npm run build
```

### 预览构建

```bash
npm run preview
```

---

## 项目配置

### 环境变量

在项目根目录创建 `.env` 文件：

```env
# Supabase 配置
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Supabase 配置

1. 创建 Supabase 项目
2. 在 SQL Editor 中执行 `database/setup.sql`
3. 启用 Realtime 功能
4. 获取 URL 和 Anon Key

### 天气 API

项目已内置和风天气 API，默认获取上海闵行区天气。如需修改：

- 在 `src/App.vue` 中修改 `QWEATHER_LOCATION`
- 参考 [和风天气开发文档](https://dev.qweather.com/)

---

## 数据库结构

### bookings 表

预约记录表，用于存储管理员设置的时段状态和备注。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| venue | TEXT | 场地标识 ('cage', 'pool') |
| date | TEXT | 日期 (YYYY-MM-DD) |
| time_slot | INTEGER | 时段 (14-21) |
| remark | TEXT | 备注 |
| status | TEXT | 状态 ('available', 'booked') |
| updated_at | TIMESTAMP | 更新时间 |

### time_slots 表

爬虫同步的场地实际状态表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| venue_id | TEXT | 场地ID |
| date | TEXT | 日期 |
| field_name | TEXT | 场地名称 |
| time | TEXT | 时间 |
| price | TEXT | 价格 |
| remaining | INTEGER | 剩余数量 |
| status | TEXT | 状态 |
| created_at | TIMESTAMP | 创建时间 |

### feedback 表

用户反馈表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| type | TEXT | 类型 ('feedback', 'suggestion') |
| content | TEXT | 内容 |
| status | TEXT | 状态 ('pending', 'resolved') |
| created_at | TIMESTAMP | 创建时间 |

### want_to_play 表

想踢人数登记表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| venue | TEXT | 场地 |
| date | TEXT | 日期 |
| time_slot | INTEGER | 时段 |
| user_id | TEXT | 用户ID |
| created_at | TIMESTAMP | 创建时间 |

---

## 部署说明

### Vercel 部署

项目已配置 Vercel 自动部署：

1. Fork 本仓库
2. 在 Vercel 中导入项目
3. 配置环境变量
4. 推送代码到 main 分支，自动部署


### GitHub Actions 爬虫

项目包含自动爬虫工作流，定期同步场地状态：

- 工作流文件: `.github/workflows/sjtu-crawler.yml`
- 爬虫代码: `scripts/sjtu_crawler_auto.py`

配置 Secrets：
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SJTU_USERNAME`
- `SJTU_PASSWORD`

---

## 使用指南

### 基本使用

1. **查看预约**：选择日期即可查看该日期所有时段的预约情况
2. **想踢登记**：点击任意时段，在弹出的窗口中点击"想踢+1"即可登记意向；再次点击可取消登记
3. **日期天气**：每个日期按钮上方显示当天天气概况
4. **时段天气**：每个时段块内显示两天内时段的具体天气
5. **自动更新**：天气数据每10分钟自动更新，也可在设置中手动清除缓存强制刷新
6. **主题切换**：支持浅色模式、深色模式和跟随系统三种主题
7. **分享功能**：点击场地情况页面右上角分享按钮，可导出当前预约情况为图片保存或分享
8. **反馈建议**：在设置-反馈与帮助提交问题反馈或产品建议

### 常见问题

**Q: 想踢功能有什么用？会帮我预约吗？**

A: 想踢功能仅用于表达意向，方便组织者了解需求，不会自动预约场地，踢球请在群聊内接龙。

**Q: 我提交的反馈与建议会被看到吗？**

A: 是的，管理员可以在后台看到所有反馈和建议，我们会认真阅读并考虑。

**Q: 为什么最后一天的数据在下午2点前显示"不可选"？**

A: 数据通常在每天下午2点左右更新，请在2点后再查看最新数据。

**Q: 为什么全部时段都显示可预约？**

A: 您的网络环境异常，请切换WLAN/移动数据或更换浏览器重试。

---

## 项目结构

```
football_booking_web/
├── .github/
│   └── workflows/
│       └── sjtu-crawler.yml    # GitHub Actions 爬虫工作流
├── .vscode/                     # VS Code 配置
├── public/
│   ├── bg/                       # 背景图片
│   └── icons/                    # 图标资源
├── src/
│   ├── assets/                   # 静态资源
│   ├── App.vue                   # 主应用组件
│   ├── main.js                   # 入口文件
│   ├── style.css                 # 全局样式
│   └── supabase.js               # Supabase 配置
├── scripts/                      # 脚本目录
│   ├── sjtu_crawler_auto.py      # 爬虫脚本
│   └── requirements-crawler.txt  # 爬虫依赖
├── database/                     # 数据库脚本
│   ├── setup.sql                 # 数据库初始化脚本
│   ├── migration.sql             # 数据库迁移脚本
│   ├── fix.sql                   # 数据库修复脚本
│   └── time_slots.sql            # time_slots 表创建脚本
├── docs/                         # 文档目录
│   └── README-en.md              # 项目说明（英文）
├── README.md                     # 项目说明（中文）
├── index.html                    # HTML 入口
├── package.json                  # 依赖配置
├── vite.config.js                # Vite 配置
├── vercel.json                   # Vercel 配置
└── .env.example                  # 环境变量示例
```

---

## 许可证

[MIT License](LICENSE)

---

## 开发者信息

### 作者

- **pony**
- 📧 Email: hanyufei24@sjtu.edu.cn
- 🔗 GitHub: [pnnooy](https://github.com/pnnooy)

### 项目链接

- 🏠 GitHub 仓库: [github.com/pnnooy/football_booking_web](https://github.com/pnnooy/football_booking_web)