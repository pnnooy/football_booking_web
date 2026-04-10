# 足球场地预约看板 | Football Pitch Booking Board

<details open>
<summary>中文</summary>

## 项目介绍

一个简洁美观的足球场地预约情况看板系统，帮助你快速查看足球场地预约情况。

## 功能特性

- 📅 **日期选择** - 支持查看未来8天的场地预约情况
- ⚽ **笼式足球场** - 专注于笼式足球场预约查看
- 🌤️ **天气预报** - 集成和风天气API，显示7日预报和逐小时天气
- 🔒 **密码保护** - 预约和取消操作需要管理员密码（管理员功能）
- ✍️ **备注功能** - 长按时段可添加备注信息（管理员功能）
- 🔄 **实时同步** - Supabase实时数据同步
- 🐛 **自动同步** - GitHub Actions自动同步场地状态
- 🎨 **主题切换** - 支持浅色/深色/跟随系统三种主题

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
预约记录表

### time_slots表
爬虫同步的场地实际状态表

详细的数据库脚本请查看项目根目录下的SQL文件。

## 部署

项目已配置Vercel自动部署，推送到main分支会自动触发部署。

## 许可证

MIT License

## 项目链接

- GitHub仓库: https://github.com/pnnooy/football_booking_web

</details>

<details>
<summary>English</summary>

## Project Introduction

A clean and beautiful football pitch booking board system to help you quickly view football pitch availability.

## Features

- 📅 **Date Selection** - View pitch availability for the next 8 days
- ⚽ **Cage Football** - Focus on cage football pitch viewing
- 🌤️ **Weather Forecast** - Integrated QWeather API, showing 7-day forecast and hourly weather
- 🔒 **Password Protection** - Booking and cancellation require admin password (admin feature)
- ✍️ **Remark Function** - Long press time slot to add remarks (admin feature)
- 🔄 **Real-time Sync** - Supabase real-time data synchronization
- 🐛 **Crawler Sync** - GitHub Actions automatically crawls pitch status
- 🎨 **Theme Switching** - Supports light/dark/system three themes

## Tech Stack

- **Frontend Framework**: Vue 3 + Vite
- **Backend Service**: Supabase
- **Weather Service**: QWeather API
- **Deployment Platform**: Vercel
- **Crawler**: Python + Playwright

## Quick Start

### Install Dependencies

```bash
npm install
```

### Development Mode

```bash
npm run dev
```

## Project Configuration

### Supabase Configuration

Need to configure the following environment variables:

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Weather API Configuration

Using QWeather API, already configured:
- API Key: Built-in
- API Host: Custom domain

## Database Structure

### bookings Table
Booking records table

### time_slots Table
Actual pitch status table synced by crawler

Please check the SQL files in the project root directory for detailed database scripts.

## Deployment

The project is configured with Vercel automatic deployment. Pushing to main branch will trigger deployment automatically.

## License

MIT License

## Project Links

- GitHub Repository: https://github.com/pnnooy/football_booking_web

</details>
