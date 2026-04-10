# Football Pitch Booking Board | 足球场地预约看板

[English Version](README-en.md) | [中文版](README.md)

A clean and beautiful football pitch booking system to help you quickly view and book football pitches.

## Features

- 📅 **Date Selection** - View pitch availability for the next 8 days
- ⚽ **Cage Football** - Focus on cage football pitch booking
- 🌤️ **Weather Forecast** - Integrated QWeather API, showing 7-day forecast and hourly weather
- 🔒 **Password Protection** - Booking and cancellation require admin password
- ✍️ **Remark Function** - Long press time slot to add remarks
- 🔄 **Real-time Sync** - Supabase real-time data synchronization
- 🐛 **Crawler Sync** - GitHub Actions automatically crawls pitch status

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

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
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
User booking records table

### time_slots Table
Actual pitch status table synced by crawler

Please check the SQL files in the project root directory for detailed database scripts.

## GitHub Actions Crawler

The project includes an automatic crawler workflow that regularly syncs pitch status to Supabase.

Crawler configuration located at: `.github/workflows/`

Crawler code located at: `sjtu_crawler_auto.py`

## Deployment

The project is configured with Vercel automatic deployment. Pushing to main branch will trigger deployment automatically.

## License

MIT License

## Project Links

- GitHub Repository: https://github.com/pnnooy/football_booking_web
