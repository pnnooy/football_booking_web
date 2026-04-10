<template>
  <div class="app" :class="currentTheme">
    <!-- 加载界面 -->
    <div v-if="isLoading" class="loading-screen">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载场地预约数据...</p>
    </div>

    <!-- 主内容 -->
    <div v-else class="main-container">
      <!-- 页面内容区域 -->
      <div class="page-content">
        <!-- 场地情况页面 -->
        <div v-if="currentPage === 'venue'" class="venue-page">
          <header class="page-header">
            <h1>场地预约情况</h1>
            <button class="share-btn-fixed" @click="shareSchedule">
              <img src="/icons/share.svg" alt="分享" class="icon-img">
            </button>
          </header>

          <main class="main-content">
            <div class="venue-title">
              <h2>{{ venues[0].name }}</h2>
            </div>

            <div class="date-nav">
              <div class="dates-scroll">
                <button
                  v-for="(date, index) in dateList"
                  :key="index"
                  :class="['date-btn', { active: selectedDate === date.fullDate }]"
                  @click="selectedDate = date.fullDate"
                >
                  <span class="date-day">{{ date.day }}</span>
                  <span class="date-week">{{ date.week }}</span>
                  <span :class="['date-status', hasDateBooking(date.fullDate) ? 'has-booking' : 'no-booking']">
                    {{ hasDateBooking(date.fullDate) ? '有' : '无' }}
                  </span>
                  <span v-if="getWeatherForDate(date.fullDate)" class="weather-info">
                    <i :class="['qi-' + getWeatherForDate(date.fullDate).iconCode, 'weather-icon']"></i>
                    <span class="weather-desc">{{ getWeatherForDate(date.fullDate).desc }}</span>
                    <span class="weather-temp">{{ getWeatherForDate(date.fullDate).minTemp }}°~{{ getWeatherForDate(date.fullDate).maxTemp }}°</span>
                  </span>
                </button>
              </div>
            </div>

            <div class="time-grid">
              <div
                v-for="hour in timeSlots"
                :key="hour"
                class="time-slot-wrapper"
              >
                <div v-if="getRemark(hour)" class="remark-display">
                  {{ getRemark(hour) }}
                </div>

                <div
                  :class="['time-slot', getSlotClass(hour)]"
                  @click="handleSlotClick(hour)"
                  @touchstart="startPress(hour)"
                  @touchend="cancelPress"
                  @touchcancel="cancelPress"
                >
                  <div class="time-slot-left">
                    <span class="time-label">{{ hour }}:00 - {{ hour + 1 }}:00</span>
                    <div v-if="getHourlyWeather(selectedDate, hour)" class="time-slot-weather">
                      <i :class="['qi-' + getHourlyWeather(selectedDate, hour).iconCode, 'slot-weather-icon']"></i>
                      <span class="slot-weather-temp">{{ getHourlyWeather(selectedDate, hour).temp }}°</span>
                      <span v-if="getHourlyWeather(selectedDate, hour).pop > 15" class="slot-weather-pop">
                        💧{{ getHourlyWeather(selectedDate, hour).pop }}%
                      </span>
                    </div>
                  </div>
                  <span class="time-status">{{ getSlotStatus(hour) }}</span>
                </div>
              </div>
            </div>
          </main>
        </div>

        <!-- 设置页面 -->
        <div v-if="currentPage === 'settings'" class="settings-page">
          <header class="settings-header">
            <h2>设置</h2>
          </header>

          <div class="settings-body">
            <div class="settings-section">
              <div class="section-title">主题配色</div>
              <div class="theme-grid">
                <div
                  v-for="theme in themes"
                  :key="theme.id"
                  :class="['theme-item', { active: currentThemeId === theme.id }]"
                  :style="{ background: theme.primary }"
                  @click="selectTheme(theme.id)"
                >
                  <div v-if="currentThemeId === theme.id" class="theme-check">✓</div>
                </div>
              </div>
            </div>

            <div class="settings-section">
              <div class="section-title">外观设置</div>
              <div class="section-content">
                <div class="settings-item" @click="showBgSettings = true">
                  <div class="settings-text">
                    <div class="settings-item-title">更换背景</div>
                    <div class="settings-item-desc">选择图片背景或纯色背景</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <div class="settings-section">
              <div class="section-title">反馈与帮助</div>
              <div class="section-content">
                <div class="settings-item" @click="showFeedbackModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">问题反馈</div>
                    <div class="settings-item-desc">报告Bug或遇到的问题</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>

                <div class="settings-item" @click="showSuggestionModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">功能建议</div>
                    <div class="settings-item-desc">提出新功能或改进建议</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>

                <div class="settings-item" @click="showHelpModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">使用帮助</div>
                    <div class="settings-item-desc">查看使用说明和常见问题</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <div class="settings-section">
              <div class="section-title">缓存管理</div>
              <div class="section-content">
                <div class="settings-item" @click="clearWeatherCache">
                  <div class="settings-text">
                    <div class="settings-item-title">清除天气缓存</div>
                    <div class="settings-item-desc">清除已缓存的天气数据</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>

                <div class="settings-item" @click="clearAllCache">
                  <div class="settings-text">
                    <div class="settings-item-title">清除所有本地数据</div>
                    <div class="settings-item-desc">清除所有缓存和本地存储</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <div class="settings-section">
              <div class="section-title">项目信息</div>
              <div class="section-content">
                <div class="settings-item" @click="showProjectInfo = true">
                  <div class="settings-text">
                    <div class="settings-item-title">项目信息</div>
                    <div class="settings-item-desc">版本、更新日志等</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>

                <div class="settings-item" @click="showDeveloperInfo = true">
                  <div class="settings-text">
                    <div class="settings-item-title">开发者信息</div>
                    <div class="settings-item-desc">作者、仓库、协议等</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <div class="settings-section">
              <div class="section-title">安全与隐私</div>
              <div class="section-content">
                <div class="settings-item" @click="clearBrowsingHistory">
                  <div class="settings-text">
                    <div class="settings-item-title">清除浏览记录</div>
                    <div class="settings-item-desc">清除本地浏览历史</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>

                <div class="settings-item" @click="showLiabilityModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">责任声明</div>
                    <div class="settings-item-desc">使用条款、免责声明等</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底栏导航 -->
      <nav class="tab-bar">
        <button
          :class="['tab-item', { active: currentPage === 'venue' }]"
          @click="currentPage = 'venue'"
        >
          <span class="tab-icon">⚽</span>
          <span class="tab-label">场地情况</span>
        </button>
        <button
          :class="['tab-item', { active: currentPage === 'settings' }]"
          @click="currentPage = 'settings'"
        >
          <span class="tab-icon">⚙️</span>
          <span class="tab-label">设置</span>
        </button>
      </nav>
    </div>

    <!-- 弹窗组件省略，保持原有代码... -->
    <div v-if="showBgSettings" class="modal-overlay" @click="showBgSettings = false">
      <div class="modal-content modal-content-large" @click.stop>
        <div class="modal-header">
          <h3>更换背景</h3>
          <button class="modal-close" @click="showBgSettings = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="section-label">图片背景</div>
          <div class="bg-preview-grid">
            <div 
              v-for="(img, index) in bgImages" 
              :key="index"
              class="bg-preview-item"
              :class="{ active: currentBgType === 'image' && currentBgImage === img }"
              :style="{ backgroundImage: `url(/bg/${img})` }"
              @click="selectImageBg(img)"
            ></div>
          </div>
          
          <div class="section-label" style="margin-top: 20px;">纯色背景</div>
          <div class="color-preview-grid">
            <div 
              v-for="(color, index) in solidBgColors" 
              :key="index"
              class="color-preview-item"
              :class="{ active: currentBgType === 'solid' && currentSolidBg === color.color }"
              :style="{ background: color.color }"
              :title="color.name"
              @click="selectSolidBg(color.color)"
            ></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-primary" @click="showBgSettings = false">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { supabase } from './supabase'

const currentPage = ref('venue')

const themes = [
  { id: 'theme-ocean', name: '海洋蓝', primary: '#0f172a', text: '#e2e8f0', accent: '#3b82f6' },
  { id: 'theme-forest', name: '森林绿', primary: '#064e3b', text: '#ecfdf5', accent: '#10b981' },
  { id: 'theme-sunset', name: '日落橙', primary: '#1c1917', text: '#fef3c7', accent: '#f97316' },
  { id: 'theme-lavender', name: '薰衣草紫', primary: '#1e1b4b', text: '#ede9fe', accent: '#8b5cf6' }
]
const currentThemeId = ref('theme-ocean')
const currentTheme = computed(() => currentThemeId.value)

function selectTheme(themeId) {
  currentThemeId.value = themeId
  localStorage.setItem('themeId', themeId)
}

async function loadHtml2Canvas() {
  return new Promise((resolve, reject) => {
    if (window.html2canvas) {
      resolve(window.html2canvas)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js'
    script.onload = () => resolve(window.html2canvas)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const venues = [
  { id: 'cage', name: '笼式足球场', venue_id: '2b528fa8-3ce8-4a7a-8f8b-83cc537901ed' }
]

const timeSlots = [14, 15, 16, 17, 18, 19, 20, 21]
const currentVenue = ref('cage')
const selectedDate = ref('')
const bookings = ref([])
const isLoading = ref(true)
const bgImages = ['bg1.jpg', 'bg2.jpg', 'bg3.jpg', 'bg4.jpg', 'bg5.jpg', 'bg6.jpg', 'bg7.jpg']
const currentBgImage = ref('')
const solidBgColors = [
  { color: '#0a0a0a', name: '极深黑' },
  { color: '#0d0d0d', name: '深邃黑' },
  { color: '#111111', name: '墨黑' },
  { color: '#141414', name: '暗黑' },
  { color: '#171717', name: '深黑' },
  { color: '#1a1a1a', name: '纯黑' },
  { color: '#1d1d1d', name: '炭黑' },
  { color: '#202020', name: '灰黑' }
]
const showBgSettings = ref(false)
const showProjectInfo = ref(false)
const showDeveloperInfo = ref(false)
const showLiabilityModal = ref(false)
const showFeedbackModal = ref(false)
const showSuggestionModal = ref(false)
const showHelpModal = ref(false)
const showPasswordModal = ref(false)
const showConfirmModal = ref(false)
const showRemarkModal = ref(false)
const currentBgType = ref('solid')
const currentSolidBg = ref('#232d3f')
const venueSlots = ref([])
const weatherData = ref({})
const hourlyWeatherData = ref([])
const weatherLoading = ref(false)
const QWEATHER_API_KEY = '88a8f299cef84b979fd0f9ff434b57c3'
const QWEATHER_API_HOST = 'nt63yxcqx8.re.qweatherapi.com'
const QWEATHER_LOCATION = '101021200'
const passwordInput = ref('')
const pendingAction = ref(null)
const confirmMessage = ref('')
const confirmHour = ref(null)
const remarkTime = ref('')
const remarkText = ref('')
const currentHour = ref(null)
const pressTimer = ref(null)

const currentVenueId = computed(() => {
  const venue = venues.find(v => v.id === currentVenue.value)
  return venue ? venue.venue_id : ''
})

const dateList = computed(() => {
  const dates = []
  const today = new Date()
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  for (let i = 0; i < 8; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const week = weekDays[date.getDay()]
    const fullDate = `${date.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    dates.push({ month, day, week, fullDate })
  }
  return dates
})

async function shareSchedule() {
  try {
    const h2c = await loadHtml2Canvas()
    const shareBtn = document.querySelector('.share-btn-fixed')
    if (shareBtn) shareBtn.style.display = 'none'
    await nextTick()
    const element = document.querySelector('.venue-page')
    if (!element) { alert('无法获取页面内容'); return }
    const canvas = await h2c(element, {
      scale: 2, useCORS: true, backgroundColor: '#0f172a',
      allowTaint: true, logging: false, letterRendering: true
    })
    if (shareBtn) shareBtn.style.display = 'flex'
    const link = document.createElement('a')
    const dateStr = new Date().toISOString().split('T')[0]
    link.download = `足球场地预约_${dateStr}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
    const shareBtn = document.querySelector('.share-btn-fixed')
    if (shareBtn) shareBtn.style.display = 'flex'
  }
}

function selectSolidBg(color) {
  currentSolidBg.value = color
  currentBgType.value = 'solid'
  localStorage.setItem('bgType', 'solid')
  localStorage.setItem('solidBg', color)
}

function selectImageBg(img) {
  currentBgImage.value = img
  currentBgType.value = 'image'
  localStorage.setItem('bgType', 'image')
  localStorage.setItem('imageBg', img)
}

function clearWeatherCache() {
  localStorage.removeItem('weatherCache')
  localStorage.removeItem('hourlyWeatherCache')
  localStorage.removeItem('weatherCacheTime')
  alert('天气缓存已清除！')
  fetchWeatherData()
}

function clearAllCache() {
  if (confirm('确定要清除所有本地数据吗？此操作不可恢复。')) {
    localStorage.clear()
    alert('所有本地数据已清除！')
    location.reload()
  }
}

function clearBrowsingHistory() {
  if (confirm('确定要清除浏览记录吗？')) {
    localStorage.removeItem('bookingHistory')
    alert('浏览记录已清除！')
  }
}

function submitFeedback() {
  alert('感谢您的反馈！我们会尽快处理。')
  showFeedbackModal.value = false
}

function submitSuggestion() {
  alert('感谢您的建议！我们会认真考虑。')
  showSuggestionModal.value = false
}

async function fetchWeatherData() {
  const cachedData = localStorage.getItem('weatherCache')
  const cachedHourlyData = localStorage.getItem('hourlyWeatherCache')
  const cacheTime = localStorage.getItem('weatherCacheTime')
  const now = Date.now()
  if (cachedData && cachedHourlyData && cacheTime && (now - parseInt(cacheTime)) < 10 * 60 * 1000) {
    weatherData.value = JSON.parse(cachedData)
    hourlyWeatherData.value = JSON.parse(cachedHourlyData)
    return
  }
  weatherLoading.value = true
  try {
    const [dailyResponse, hourlyResponse] = await Promise.all([
      fetch(`https://${QWEATHER_API_HOST}/v7/weather/10d?location=${QWEATHER_LOCATION}&key=${QWEATHER_API_KEY}`),
      fetch(`https://${QWEATHER_API_HOST}/v7/weather/72h?location=${QWEATHER_LOCATION}&key=${QWEATHER_API_KEY}`)
    ])
    if (!dailyResponse.ok || !hourlyResponse.ok) throw new Error('Weather API failed')
    const dailyData = await dailyResponse.json()
    const hourlyData = await hourlyResponse.json()
    const weatherMap = {}
    if (dailyData.daily) {
      dailyData.daily.forEach((day) => {
        weatherMap[day.fxDate] = {
          minTemp: parseInt(day.tempMin),
          maxTemp: parseInt(day.tempMax),
          iconCode: day.iconDay,
          desc: day.textDay
        }
      })
    }
    weatherData.value = weatherMap
    localStorage.setItem('weatherCache', JSON.stringify(weatherMap))
    localStorage.setItem('hourlyWeatherCache', JSON.stringify([]))
    localStorage.setItem('weatherCacheTime', now.toString())
  } catch (error) {
    console.error('Failed to fetch weather:', error)
  } finally {
    weatherLoading.value = false
  }
}

function getWeatherForDate(dateStr) {
  return weatherData.value[dateStr] || null
}

function getHourlyWeather(dateStr, hour) {
  return null
}

onMounted(() => {
  const savedThemeId = localStorage.getItem('themeId')
  if (savedThemeId) currentThemeId.value = savedThemeId
  const savedBgType = localStorage.getItem('bgType')
  const savedSolidBg = localStorage.getItem('solidBg')
  if (savedBgType) currentBgType.value = savedBgType
  if (savedSolidBg) currentSolidBg.value = savedSolidBg
  const today = new Date()
  const month = today.getMonth() + 1
  const day = today.getDate()
  selectedDate.value = `${today.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  Promise.all([fetchBookings(), fetchVenueSlots(), subscribeToBookings()]).then(() => {
    isLoading.value = false
  })
  fetchWeatherData()
})

function getBookingsForVenueAndDate(venue, date) {
  return bookings.value.filter(b => b.venue === venue && b.date === date)
}

function isBooked(hour) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
  const booking = venueBookings.find(b => b.time_slot === hour)
  if (booking && booking.status !== undefined) return booking.status === 'booked'
  if (booking && booking.remark) return true
  return false
}

function isExpired(hour) {
  const now = new Date()
  const [year, month, day] = selectedDate.value.split('-').map(Number)
  const slotEndDate = new Date(year, month - 1, day, hour + 1)
  return now > slotEndDate
}

function getSlotClass(hour) {
  if (isExpired(hour)) return 'expired'
  if (isBooked(hour)) return 'booked'
  const venueStatus = getVenueSlotStatus(selectedDate.value, hour)
  if (venueStatus === '已满' || venueStatus === '不可选' || venueStatus === '未开放') return 'unavailable'
  return 'available'
}

function getSlotStatus(hour) {
  if (isExpired(hour)) return '已过期'
  if (isBooked(hour)) return '已预约'
  const venueStatus = getVenueSlotStatus(selectedDate.value, hour)
  if (venueStatus) return venueStatus
  return '可预约'
}

function getRemark(hour) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
  const booking = venueBookings.find(b => b.time_slot === hour)
  if (booking?.remark) return booking.remark
  return getAutoRemark(selectedDate.value, hour)
}

function hasDateBooking(date) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, date)
  return venueBookings.some(b => b.status === 'booked')
}

function handleSlotClick(hour) {
  if (isExpired(hour)) { alert('已过时的时段无法操作'); return }
  if (isBooked(hour)) {
    pendingAction.value = { type: 'cancel', hour: hour }
    showPasswordModal.value = true
    passwordInput.value = ''
    return
  }
  pendingAction.value = { type: 'book', hour: hour }
  showPasswordModal.value = true
  passwordInput.value = ''
}

function confirmToggle() {
  if (confirmHour.value !== null) toggleBooking(confirmHour.value)
  showConfirmModal.value = false
  confirmHour.value = null
}

function verifyPassword() {
  if (passwordInput.value === 'qwerty') {
    showPasswordModal.value = false
    passwordInput.value = ''
    if (pendingAction.value) {
      if (pendingAction.value.type === 'book') {
        confirmMessage.value = '确认预约该时段'
        confirmHour.value = pendingAction.value.hour
        showConfirmModal.value = true
      } else if (pendingAction.value.type === 'cancel') {
        confirmMessage.value = '取消该时段的预约'
        confirmHour.value = pendingAction.value.hour
        showConfirmModal.value = true
      }
      pendingAction.value = null
    }
  } else {
    alert('密码错误，请重试')
    passwordInput.value = ''
  }
}

function startPress(hour) {
  if (isExpired(hour)) return
  pressTimer = setTimeout(() => {
    currentHour.value = hour
    remarkTime.value = `${selectedDate.value} ${hour}:00-${hour+1}:00`
    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const booking = venueBookings.find(b => b.time_slot === hour)
    remarkText.value = booking?.remark || getAutoRemark(selectedDate.value, hour)
    showRemarkModal.value = true
  }, 500)
}

function cancelPress() {
  if (pressTimer) { clearTimeout(pressTimer); pressTimer = null }
}

async function toggleBooking(hour) {
  try {
    const isCurrentlyBooked = isBooked(hour)
    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const existingBooking = venueBookings.find(b => b.time_slot === hour)
    if (isCurrentlyBooked) {
      if (existingBooking && existingBooking.id) {
        if (existingBooking.status !== undefined) {
          const { error } = await supabase.from('bookings').update({ status: 'available' }).eq('id', existingBooking.id)
          if (error) throw error
        } else {
          const { error } = await supabase.from('bookings').delete().eq('id', existingBooking.id)
          if (error) throw error
        }
      }
    } else {
      if (existingBooking && existingBooking.id) {
        const { error } = await supabase.from('bookings').update({ status: 'booked' }).eq('id', existingBooking.id)
        if (error) throw error
      } else {
        const { error } = await supabase.from('bookings').insert({ venue: currentVenue.value, date: selectedDate.value, time_slot: hour, status: 'booked' })
        if (error) throw error
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败，请重试')
  }
}

async function saveRemark() {
  if (!currentHour.value) return
  try {
    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const existingBooking = venueBookings.find(b => b.time_slot === currentHour.value)
    if (existingBooking && existingBooking.id) {
      const { error: updateError } = await supabase.from('bookings').update({ remark: remarkText.value || '' }).eq('id', existingBooking.id)
      if (updateError) throw updateError
    } else {
      const { error: insertError } = await supabase.from('bookings').insert({ venue: currentVenue.value, date: selectedDate.value, time_slot: currentHour.value, remark: remarkText.value || '', status: 'available' })
      if (insertError) throw insertError
    }
    showRemarkModal.value = false
    remarkText.value = ''
    currentHour.value = null
  } catch (error) {
    console.error('保存备注失败:', error)
    alert('保存备注失败')
  }
}

function isThursday19to21(dateStr, hour) {
  const [year, month, day] = dateStr.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  const dayOfWeek = date.getDay()
  return dayOfWeek === 4 && hour >= 19 && hour <= 20
}

function getAutoRemark(dateStr, hour) {
  if (currentVenue.value === 'cage' && isThursday19to21(dateStr, hour)) {
    return '健步足球社团时间'
  }
  return ''
}

async function fetchBookings() {
  try {
    const today = new Date()
    const endDate = new Date(today)
    endDate.setDate(today.getDate() + 8)
    const startDateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    const endDateStr = `${endDate.getFullYear()}-${String(endDate.getMonth() + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`
    const { data, error } = await supabase.from('bookings').select('id, venue, date, time_slot, remark, status').gte('date', startDateStr).lte('date', endDateStr).order('date', { ascending: true }).order('time_slot', { ascending: true })
    if (error) throw error
    bookings.value = data || []
  } catch (error) {
    console.error('获取预约记录失败:', error)
    bookings.value = []
  }
}

async function fetchVenueSlots() {
  try {
    venueSlots.value = []
  } catch (error) {
    console.error('获取场地状态失败:', error)
    venueSlots.value = []
  }
}

function getVenueSlotStatus(date, hour) {
  return null
}

function subscribeToBookings() {
  supabase.channel('bookings').on('postgres_changes', { event: '*', schema: 'public', table: 'bookings' }, (payload) => {
    console.log('收到 bookings 实时更新:', payload)
    fetchBookings()
  }).subscribe()
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

button {
  -webkit-tap-highlight-color: transparent !important;
  outline: none !important;
  box-shadow: none !important;
}

.theme-ocean {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #334155;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}

.theme-forest {
  --bg-primary: #064e3b;
  --bg-secondary: #065f46;
  --bg-card: #047857;
  --text-primary: #ecfdf5;
  --text-secondary: #a7f3d0;
  --accent: #10b981;
  --accent-hover: #059669;
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #f87171;
}

.theme-sunset {
  --bg-primary: #1c1917;
  --bg-secondary: #292524;
  --bg-card: #44403c;
  --text-primary: #fef3c7;
  --text-secondary: #fcd34d;
  --accent: #f97316;
  --accent-hover: #ea580c;
  --success: #a3e635;
  --warning: #fbbf24;
  --danger: #fb7185;
}

.theme-lavender {
  --bg-primary: #1e1b4b;
  --bg-secondary: #312e81;
  --bg-card: #4338ca;
  --text-primary: #ede9fe;
  --text-secondary: #c4b5fd;
  --accent: #8b5cf6;
  --accent-hover: #7c3aed;
  --success: #a78bfa;
  --warning: #fbbf24;
  --danger: #f87171;
}

.app {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  transition: background 0.3s ease;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: var(--text-secondary);
}

.main-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-bottom: 70px;
}

.page-content {
  flex: 1;
  overflow-y: auto;
}

.page-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.settings-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.settings-header h2 {
  font-size: 22px;
  font-weight: 600;
}

.share-btn-fixed {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.share-btn-fixed:hover {
  background: var(--accent);
}

.icon-img {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: invert(1);
}

.venue-page {
  min-height: 100%;
}

.main-content {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.venue-title {
  text-align: center;
  margin-bottom: 20px;
}

.venue-title h2 {
  font-size: 20px;
  font-weight: 500;
}

.date-nav {
  margin-bottom: 20px;
  overflow-x: auto;
}

.dates-scroll {
  display: flex;
  gap: 10px;
  padding: 5px;
}

.date-btn {
  flex-shrink: 0;
  padding: 8px 10px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 75px;
  min-height: 100px;
}

.date-btn:hover {
  background: var(--bg-card);
}

.date-btn.active {
  background: var(--accent);
  border-color: transparent;
}

.date-day {
  font-size: 20px;
  font-weight: bold;
}

.date-week {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 4px;
}

.date-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 6px;
  font-weight: 600;
}

.date-status.has-booking {
  background: var(--success);
  color: #fff;
}

.date-status.no-booking {
  background: var(--bg-card);
  color: var(--text-secondary);
}

.weather-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.weather-icon {
  font-size: 24px;
  line-height: 1;
}

.weather-desc {
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

.weather-temp {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 500;
}

.time-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
}

.time-slot-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.remark-display {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 8px 14px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-left: 4px;
}

.time-slot {
  padding: 18px 20px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 2px solid transparent;
}

.time-slot:hover:not(.expired) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.time-slot-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.time-label {
  font-size: 16px;
  font-weight: 600;
}

.time-slot-weather {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.slot-weather-icon {
  font-size: 22px;
  line-height: 1;
}

.slot-weather-temp {
  font-size: 14px;
  font-weight: 600;
}

.slot-weather-pop {
  font-size: 12px;
  color: #93c5fd;
  font-weight: 500;
}

.time-status {
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  font-weight: 600;
}

.time-slot.available {
  background: var(--accent);
}

.time-slot.available:hover {
  background: var(--accent-hover);
}

.time-slot.unavailable {
  background: var(--bg-card);
  opacity: 0.7;
}

.time-slot.booked {
  background: var(--success);
}

.time-slot.expired {
  background: var(--bg-secondary);
  cursor: not-allowed;
  opacity: 0.5;
}

.settings-page {
  min-height: 100%;
}

.settings-body {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.settings-section {
  margin-bottom: 28px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 12px;
  padding-left: 4px;
}

.section-content {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 4px;
  overflow: hidden;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 12px;
}

.theme-item {
  aspect-ratio: 1;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid transparent;
}

.theme-item:hover {
  transform: scale(1.05);
}

.theme-item.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.theme-check {
  font-size: 24px;
  color: #fff;
  font-weight: bold;
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px;
  background: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  width: 100%;
  -webkit-tap-highlight-color: transparent;
}

.settings-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.settings-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.settings-item-title {
  font-size: 16px;
  font-weight: 500;
  line-height: 1.4;
}

.settings-item-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.settings-arrow {
  font-size: 20px;
  color: var(--text-secondary);
  margin-left: 8px;
  font-weight: 300;
  flex-shrink: 0;
}

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  z-index: 100;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s;
  -webkit-tap-highlight-color: transparent;
}

.tab-icon {
  font-size: 24px;
  margin-bottom: 4px;
  opacity: 0.5;
  transition: all 0.3s;
}

.tab-label {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.5;
  transition: all 0.3s;
}

.tab-item.active .tab-icon,
.tab-item.active .tab-label {
  opacity: 1;
  color: var(--accent);
}

.bg-preview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 8px;
}

.bg-preview-item {
  aspect-ratio: 9/16;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  background-size: cover;
  background-position: center;
}

.bg-preview-item:hover {
  transform: scale(1.02);
}

.bg-preview-item.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.color-preview-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  padding: 8px;
}

.color-preview-item {
  aspect-ratio: 1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.color-preview-item:hover {
  transform: scale(1.1);
}

.color-preview-item.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-content-large {
  max-width: 480px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  font-size: 17px;
  font-weight: 600;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  -webkit-tap-highlight-color: transparent;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  -webkit-tap-highlight-color: transparent;
}

.modal-btn-secondary {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.8);
}

.modal-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-btn-primary {
  background: var(--accent);
  color: #fff;
}

.modal-btn-primary:hover {
  background: var(--accent-hover);
}

.modal {
  background: var(--bg-secondary);
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal h3 {
  margin-bottom: 8px;
  font-size: 18px;
}

.modal-time {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.modal-message {
  font-size: 16px;
  margin-bottom: 20px;
  text-align: center;
}

.modal textarea {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.modal textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.password-input {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 16px;
  margin-top: 12px;
}

.password-input:focus {
  outline: none;
  border-color: var(--accent);
}

.modal-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.modal-buttons button {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  -webkit-tap-highlight-color: transparent;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-confirm {
  background: var(--accent);
  color: #fff;
}

.btn-confirm:hover {
  opacity: 0.9;
}

.info-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  margin: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 14px;
  line-height: 1.5;
}

.info-link {
  font-size: 14px;
  color: var(--accent);
  text-decoration: none;
  word-break: break-all;
}

.info-link:hover {
  text-decoration: underline;
}

.version-badge {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.info-section {
  margin-bottom: 16px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.info-section-content {
  font-size: 13px;
  line-height: 1.6;
}

.help-content {
  padding: 16px;
}

.help-section {
  margin-bottom: 24px;
}

.help-section:last-child {
  margin-bottom: 0;
}

.help-section h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 10px;
}

.help-section p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 8px;
}

.help-section p:last-child {
  margin-bottom: 0;
}

.help-section strong {
  color: #fff;
  font-weight: 500;
}
</style>
