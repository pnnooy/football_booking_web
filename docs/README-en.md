<div align="center">

# 🏟️ Football Pitch Booking Board | 足球场地预约看板

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/pnnooy/football_booking_web/blob/main/LICENSE)
[![Vue 3](https://img.shields.io/badge/Vue-3.5.25-brightgreen.svg)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3.1-purple.svg)](https://vitejs.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-2.98.0-blue.svg)](https://supabase.io/)

**[English](#) | [中文](README.md)**

</div>

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Database Structure](#database-structure)
- [Deployment](#deployment)
- [User Guide](#user-guide)
- [Project Structure](#project-structure)
- [License](#license)
- [Developer Info](#developer-info)

---

## Introduction

Football Pitch Booking Board is a clean and beautiful real-time football pitch availability viewing system. It helps users quickly understand pitch booking status, with integrated real-time weather queries, "want to play" registration, booking sharing, and more, providing convenient information services for football enthusiasts.

### Key Highlights

- 📱 Responsive design, perfectly adapted for mobile devices
- 🌙 Supports light/dark/system three themes
- ⚡ Real-time data synchronization, fast response
- 🎨 Beautiful UI design, smooth interactive experience

---

## Features

### User Features

| Feature | Description |
|---------|-------------|
| 📅 **Date Selection** | View pitch availability for the next 8 days |
| 🌤️ **Weather Forecast** | Integrated QWeather API, showing 7-day forecast and hourly weather |
| ⚽ **Want to Play** | Click time slot to register playing intention, easy for organizers to count |
| 📸 **Share Function** | Export current booking status as image, support saving and sharing |
| 🎨 **Theme Switching** | Supports light/dark/system three themes |
| 📝 **Feedback & Suggestions** | Submit problem feedback and feature suggestions |

### Admin Features

| Feature | Description |
|---------|-------------|
| 🔐 **Admin Login** | Email and password login to access management features |
| ✏️ **Time Slot Management** | Modify slot status (available/booked), add remarks |
| 👥 **Want to Play Management** | Edit want to play count |
| 📋 **Feedback Management** | View and process user feedback and suggestions |

### System Features

| Feature | Description |
|---------|-------------|
| 🔄 **Real-time Sync** | Supabase real-time data synchronization |
| 🐛 **Auto Crawler** | GitHub Actions automatically sync pitch status |
| ⏱️ **Weather Cache** | Weather data updates automatically every 10 minutes |
| 📱 **WeChat Optimization** | Optimized image sharing for WeChat browser |

---

## Tech Stack

### Frontend Technologies

- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite 7
- **UI**: Native CSS3 + Flexbox/Grid
- **Screenshot**: html2canvas 1.4.1

### Backend Services

- **BaaS**: Supabase (PostgreSQL + Auth + Realtime)
- **Weather API**: QWeather
- **Deployment**: Vercel

### Crawler Technologies

- **Language**: Python 3
- **Browser Automation**: Playwright
- **HTTP Requests**: requests
- **Scheduled Tasks**: GitHub Actions

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm or pnpm
- Python 3.8+ (if running crawler)

### Install Dependencies

```bash
# Using npm
npm install

# Or using pnpm
pnpm install
```

### Development Mode

```bash
npm run dev
```

Visit http://localhost:5173 to view the application.

### Production Build

```bash
npm run build
```

### Preview Build

```bash
npm run preview
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Supabase Setup

1. Create a Supabase project
2. Execute `database/setup.sql` in SQL Editor
3. Enable Realtime feature
4. Get URL and Anon Key

### Weather API

The project has built-in QWeather API, defaulting to Shanghai Minhang District weather. To modify:

- Modify `QWEATHER_LOCATION` in `src/App.vue`
- Refer to [QWeather Development Docs](https://dev.qweather.com/en/)

---

## Database Structure

### bookings Table

Booking records table, used to store admin-set slot status and remarks.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| venue | TEXT | Venue identifier ('cage', 'pool') |
| date | TEXT | Date (YYYY-MM-DD) |
| time_slot | INTEGER | Time slot (14-21) |
| remark | TEXT | Remark |
| status | TEXT | Status ('available', 'booked') |
| updated_at | TIMESTAMP | Update time |

### time_slots Table

Actual pitch status table synced by crawler.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| venue_id | TEXT | Venue ID |
| date | TEXT | Date |
| field_name | TEXT | Field name |
| time | TEXT | Time |
| price | TEXT | Price |
| remaining | INTEGER | Remaining count |
| status | TEXT | Status |
| created_at | TIMESTAMP | Creation time |

### feedback Table

User feedback table.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| type | TEXT | Type ('feedback', 'suggestion') |
| content | TEXT | Content |
| status | TEXT | Status ('pending', 'resolved') |
| created_at | TIMESTAMP | Creation time |

### want_to_play Table

Want to play registration table.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| venue | TEXT | Venue |
| date | TEXT | Date |
| time_slot | INTEGER | Time slot |
| user_id | TEXT | User ID |
| created_at | TIMESTAMP | Creation time |

---

## Deployment

### Vercel Deployment

The project is configured with Vercel automatic deployment:

1. Fork this repository
2. Import project in Vercel
3. Configure environment variables
4. Push code to main branch, auto-deploy



### GitHub Actions Crawler

The project includes an automatic crawler workflow that regularly syncs pitch status:

- Workflow file: `.github/workflows/sjtu-crawler.yml`
- Crawler code: `scripts/sjtu_crawler_auto.py`

Configure Secrets:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SJTU_USERNAME`
- `SJTU_PASSWORD`

---

## User Guide

### Basic Usage

1. **View Bookings**: Select a date to view booking status for all time slots on that date
2. **Want to Play**: Click any time slot, click "Want to Play +1" in the popup to register your intention; click again to cancel
3. **Date Weather**: Weather overview is displayed above each date button
4. **Time Slot Weather**: Specific weather for time slots within two days is displayed in each time slot block
5. **Auto Update**: Weather data updates automatically every 10 minutes, you can also manually clear cache in settings to force refresh
6. **Theme Switching**: Supports light mode, dark mode, and system-following themes
7. **Share Function**: Click the share button in the top-right corner of the pitch status page to export current booking status as an image for saving or sharing
8. **Feedback & Suggestions**: Submit problem feedback or product suggestions in Settings - Feedback & Help

### FAQ

**Q: What is the "Want to Play" function for? Will it book for me?**

A: The "Want to Play" function is only for expressing your intention, making it convenient for organizers to understand everyone's needs. It will not automatically book the pitch. Please join the group chat to sign up for playing.

**Q: Will the feedback and suggestions I submit be seen?**

A: Yes, admins can see all feedback and suggestions in the backend. We will read and consider them carefully.

**Q: Why does the last day's data show "Not Available" before 2 PM?**

A: Data is usually updated around 2 PM every day. Please check after 2 PM for the latest data.

**Q: Why do all time slots show as available?**

A: Your network environment is abnormal. Please switch WLAN/mobile data or try a different browser.

---

## Project Structure

```
football_booking_web/
├── .github/
│   └── workflows/
│       └── sjtu-crawler.yml    # GitHub Actions crawler workflow
├── public/
│   ├── bg/                       # Background images
│   └── icons/                    # Icon resources
├── src/
│   ├── assets/                   # Static assets
│   ├── App.vue                   # Main app component
│   ├── main.js                   # Entry file
│   ├── style.css                 # Global styles
│   └── supabase.js               # Supabase config
├── scripts/                      # Scripts directory
│   ├── sjtu_crawler_auto.py      # Crawler script
│   └── requirements-crawler.txt  # Crawler dependencies
├── database/                     # Database scripts
│   ├── setup.sql                 # Database initialization script
│   ├── migration.sql             # Database migration script
│   ├── fix.sql                   # Database fix script
│   └── time_slots.sql            # time_slots table creation script
├── docs/                         # Documentation directory
│   ├── README.md                 # Project documentation (Chinese)
│   └── README-en.md              # Project documentation (English)
├── index.html                    # HTML entry
├── package.json                  # Dependency config
├── vite.config.js                # Vite config
├── vercel.json                   # Vercel config
└── .env.example                  # Environment variables example
```

---

## License

[MIT License](LICENSE)

---

## Developer Info

### Author

- **pony**
- 📧 Email: hanyufei24@sjtu.edu.cn
- 🔗 GitHub: [pnnooy](https://github.com/pnnooy)

### Project Links

- 🏠 GitHub Repository: [github.com/pnnooy/football_booking_web](https://github.com/pnnooy/football_booking_web)
