<template>
  <div class="app" :style="{ backgroundImage: `url(/bg/${currentBgImage})` }">
    <!-- 加载界面 -->
    <div v-if="isLoading" class="loading-screen">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载场地预约数据...</p>
    </div>

    <!-- 主内容 -->
    <div v-else class="main-content-wrapper">
    <header class="header">
      <h1>场地预约情况</h1>
      <p class="current-time">当前时间：{{ currentTime }}</p>
    </header>

    <main class="main-content">
      <!-- 场地切换标签 -->
      <div class="venue-tabs">
        <button
          v-for="venue in venues"
          :key="venue.id"
          :class="['tab', { active: currentVenue === venue.id }]"
          @click="currentVenue = venue.id"
        >
          {{ venue.name }}
          <span :class="['venue-status', hasBooking(venue.id) ? 'has-booking' : 'no-booking']">
            {{ hasBooking(venue.id) ? '有预约' : '无预约' }}
          </span>
        </button>
      </div>

      <!-- 日期导航 -->
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
            <!-- 天气显示 - 文字描述 -->
            <span v-if="getWeatherForDate(date.fullDate)" class="weather-info">
              <span class="weather-desc" :data-weather="getWeatherForDate(date.fullDate).desc">
                {{ getWeatherForDate(date.fullDate).desc }}
              </span>
              <span class="weather-temp">
                {{ getWeatherForDate(date.fullDate).minTemp }}°~{{ getWeatherForDate(date.fullDate).maxTemp }}°
              </span>
            </span>
          </button>
        </div>
      </div>

      <!-- 时间网格 -->
      <div class="time-grid">
        <div
          v-for="hour in timeSlots"
          :key="hour"
          class="time-slot-wrapper"
        >
          <!-- 备注显示 -->
          <div v-if="getRemark(hour)" class="remark-display">
            {{ getRemark(hour) }}
          </div>

          <!-- 时段块 -->
          <div
            :class="['time-slot', getSlotClass(hour)]"
            @click="handleSlotClick(hour)"
            @touchstart="startPress(hour)"
            @touchend="cancelPress"
            @touchcancel="cancelPress"
          >
            <span class="time-label">{{ hour }}:00 - {{ hour + 1 }}:00</span>
            <span class="time-status">{{ getSlotStatus(hour) }}</span>
          </div>
        </div>
      </div>
    </main>
    </div>

    <!-- 密码确认弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="showPasswordModal = false">
      <div class="modal" @click.stop>
        <h3>请输入管理员密码</h3>
        <input
          v-model="passwordInput"
          type="password"
          class="password-input"
          placeholder="请输入密码..."
          @keyup.enter="verifyPassword"
          autofocus
        />
        <div class="modal-buttons">
          <button class="btn-cancel" @click="showPasswordModal = false">取消</button>
          <button class="btn-confirm" @click="verifyPassword">确认</button>
        </div>
      </div>
    </div>

    <!-- 确认弹窗 -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="showConfirmModal = false">
      <div class="modal" @click.stop>
        <h3>提示</h3>
        <p class="modal-message">{{ confirmMessage }}</p>
        <div class="modal-buttons">
          <button class="btn-cancel" @click="showConfirmModal = false">取消</button>
          <button class="btn-confirm" @click="confirmToggle">确定</button>
        </div>
      </div>
    </div>

    <!-- 备注输入弹窗 -->
    <div v-if="showRemarkModal" class="modal-overlay" @click="showRemarkModal = false">
      <div class="modal" @click.stop>
        <h3>添加备注</h3>
        <p class="modal-time">{{ remarkTime }}</p>
        <textarea
          v-model="remarkText"
          placeholder="请输入备注信息..."
          rows="3"
        ></textarea>
        <div class="modal-buttons">
          <button class="btn-cancel" @click="showRemarkModal = false">取消</button>
          <button class="btn-confirm" @click="saveRemark">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { supabase } from './supabase'

// 场地列表
const venues = [
  { id: 'cage', name: '笼式足球场', venue_id: '2b528fa8-3ce8-4a7a-8f8b-83cc537901ed' },
  { id: 'pool', name: '致远游泳馆球场', venue_id: 'a41b3261-6fce-4073-b799-1e91ed19a7f3' }
]

// 时间段（14:00 - 22:00，每小时一个时段）
const timeSlots = [14, 15, 16, 17, 18, 19, 20, 21]

// 当前选中的场地和日期
const currentVenue = ref('cage')
const selectedDate = ref('')
const bookings = ref([])
const currentTime = ref('')

// 页面加载状态
const isLoading = ref(true)

// 背景图片
const bgImages = ['bg1.jpg', 'bg2.jpg', 'bg3.jpg', 'bg4.jpg', 'bg5.jpg', 'bg6.jpg', 'bg7.jpg']
// 主页面可用的背景图片（排除bg1.jpg）
const mainPageBgImages = ['bg2.jpg', 'bg3.jpg', 'bg4.jpg', 'bg5.jpg', 'bg6.jpg', 'bg7.jpg']
const currentBgImage = ref('')

// 场地实际状态数据（从time_slots表获取）
const venueSlots = ref([])

// 当前选中场地的venue_id
const currentVenueId = computed(() => {
  const venue = venues.find(v => v.id === currentVenue.value)
  return venue ? venue.venue_id : ''
})

// 天气数据
const weatherData = ref({})
const weatherLoading = ref(false)

// 备注相关
const showRemarkModal = ref(false)
const remarkTime = ref('')
const remarkText = ref('')
const currentHour = ref(null)

// 密码确认弹窗相关
const showPasswordModal = ref(false)
const passwordInput = ref('')
const pendingAction = ref(null) // 待执行的操作：{ type: 'book'|'cancel', hour: number }

// 确认弹窗相关
const showConfirmModal = ref(false)
const confirmMessage = ref('')
const confirmHour = ref(null)

let timeInterval = null

// Open-Meteo 天气代码到文字描述的映射
const weatherCodeMap = {
  0: '晴天',
  1: '晴间多云',
  2: '多云',
  3: '阴',
  45: '雾',
  48: '雾凇',
  51: '小毛毛雨',
  53: '中毛毛雨',
  55: '大毛毛雨',
  56: '冻毛毛雨',
  57: '强冻毛毛雨',
  61: '小雨',
  63: '中雨',
  65: '大雨',
  66: '小冻雨',
  67: '大冻雨',
  71: '小雪',
  73: '中雪',
  75: '大雪',
  77: '雪粒',
  80: '小阵雨',
  81: '中阵雨',
  82: '大阵雨',
  85: '小阵雪',
  86: '大阵雪',
  95: '雷暴',
  96: '雷暴+小冰雹',
  99: '雷暴+大冰雹'
}

// 获取默认城市天气数据 - 使用Open-Meteo API（快速且无需API密钥）
async function fetchWeatherData() {
  // 先检查本地缓存
  const cachedData = localStorage.getItem('weatherCache')
  const cacheTime = localStorage.getItem('weatherCacheTime')
  const now = Date.now()

  // 如果缓存存在且未超过3小时，直接使用缓存
  if (cachedData && cacheTime && (now - parseInt(cacheTime)) < 3 * 60 * 60 * 1000) {
    weatherData.value = JSON.parse(cachedData)
    console.log('Using cached weather data')
    return
  }

  weatherLoading.value = true
  try {
    // 使用Open-Meteo API - 上海交通大学闵行校区坐标 (lat: 31.025393, lon: 121.436348)
    // 请求14天的天气数据
    const response = await fetch(
      'https://api.open-meteo.com/v1/forecast?latitude=31.025393&longitude=121.436348&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Asia/Shanghai&forecast_days=14'
    )

    if (!response.ok) throw new Error('Weather API failed')

    const data = await response.json()
    const weatherMap = {}

    // 处理14天的天气数据
    if (data.daily && data.daily.time) {
      data.daily.time.forEach((dateStr, index) => {
        const weatherCode = data.daily.weather_code[index]
        weatherMap[dateStr] = {
          minTemp: Math.round(data.daily.temperature_2m_min[index]),
          maxTemp: Math.round(data.daily.temperature_2m_max[index]),
          code: weatherCode,
          desc: weatherCodeMap[weatherCode] || '未知'
        }
      })
    }

    weatherData.value = weatherMap

    // 保存到本地缓存
    localStorage.setItem('weatherCache', JSON.stringify(weatherMap))
    localStorage.setItem('weatherCacheTime', now.toString())

    console.log('Weather data loaded from API:', weatherMap)
  } catch (error) {
    console.error('Failed to fetch weather:', error)
  } finally {
    weatherLoading.value = false
  }
}

// 获取某一天的天气数据
function getWeatherForDate(dateStr) {
  return weatherData.value[dateStr] || null
}

// 计算未来8天的日期列表
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

    dates.push({
      month,
      day,
      week,
      fullDate
    })
  }

  return dates
})

// 初始化 selectedDate 为今天
onMounted(() => {
  // 随机选择主页面背景图片（排除bg1.jpg）
  const randomIndex = Math.floor(Math.random() * mainPageBgImages.length)
  currentBgImage.value = mainPageBgImages[randomIndex]

  const today = new Date()
  const month = today.getMonth() + 1
  const day = today.getDate()
  selectedDate.value = `${today.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`

  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)

  // 先显示页面，天气数据在后台异步加载
  // 这样不会阻塞用户看到预约信息
  Promise.all([
    fetchBookings(),
    fetchVenueSlots(),
    subscribeToBookings()
  ]).then(() => {
    isLoading.value = false
  })

  // 天气数据在后台加载，不阻塞页面显示
  fetchWeatherData()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

function updateCurrentTime() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${year}-${month}-${date} ${hours}:${minutes}:${seconds}`
}

// 获取某个场地和日期的预约记录
function getBookingsForVenueAndDate(venue, date) {
  return bookings.value.filter(
    b => b.venue === venue && b.date === date
  )
}

// 检查某个时段是否已预约 (通过status字段判断)
function isBooked(hour) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
  const booking = venueBookings.find(b => b.time_slot === hour)
  // 如果有status字段，检查status是否为booked
  if (booking && booking.status !== undefined) {
    return booking.status === 'booked'
  }
  // 兼容旧数据：没有status字段时，有记录且remark不为空算已预约
  if (booking && booking.remark) {
    return true
  }
  // 再兼容旧数据：没有任何记录就算未预约
  return false
}

// 检查某个时段是否已过期（时段结束后才标记为过期，如14-15点的在15:00后才过期）
function isExpired(hour) {
  const now = new Date()
  const [year, month, day] = selectedDate.value.split('-').map(Number)
  // 使用hour+1，即该时段结束时的时间点才标记为过期
  const slotEndDate = new Date(year, month - 1, day, hour + 1)

  return now > slotEndDate
}

// 获取时段的状态类名
function getSlotClass(hour) {
  if (isExpired(hour)) {
    return 'expired'
  }
  // 如果用户已预约，显示用户预约状态（绿色）
  if (isBooked(hour)) {
    return 'booked'
  }
  // 致远游泳馆球场：所有未过期时段都显示为不可选（灰色）
  if (currentVenue.value === 'pool') {
    return 'unavailable'
  }
  // 用户未预约时，根据场地实际状态显示颜色
  const venueStatus = getVenueSlotStatus(selectedDate.value, hour)
  // 已满、不可选显示灰色
  if (venueStatus === '已满' || venueStatus === '不可选' || venueStatus === '未开放') {
    return 'unavailable'
  }
  // 可预约显示蓝色
  return 'available'
}

// 获取时段的显示状态
function getSlotStatus(hour) {
  if (isExpired(hour)) {
    return '已过期'
  }
  // 如果用户已预约，显示用户预约状态
  if (isBooked(hour)) {
    return '已预约'
  }
  // 致远游泳馆球场：所有未过期时段都显示为不可选
  if (currentVenue.value === 'pool') {
    return '不可选'
  }
  // 用户未预约时，显示场地实际状态
  const venueStatus = getVenueSlotStatus(selectedDate.value, hour)
  if (venueStatus) {
    return venueStatus
  }
  // 如果没有场地状态数据，显示可预约
  return '可预约'
}

// 获取备注 - 优先显示用户备注，否则显示自动备注
function getRemark(hour) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
  const booking = venueBookings.find(b => b.time_slot === hour)

  // 如果有用户备注，显示用户备注
  if (booking?.remark) {
    return booking.remark
  }

  // 否则显示自动备注
  return getAutoRemark(selectedDate.value, hour)
}

// 检查某个日期是否有任何预约（针对当前选中的场地）- 使用status字段判断
function hasDateBooking(date) {
  const venueBookings = getBookingsForVenueAndDate(currentVenue.value, date)
  // 检查是否有status为booked的记录
  return venueBookings.some(b => b.status === 'booked')
}

// 检查某个场地在所有显示的日期中是否有未过期的预约 - 使用status字段判断
function hasBooking(venueId) {
  const now = new Date()
  for (const dateItem of dateList.value) {
    const venueBookings = bookings.value.filter(b => b.venue === venueId && b.date === dateItem.fullDate)
    for (const booking of venueBookings) {
      // 检查status是否为booked
      if (booking.status === 'booked') {
        const slotDate = new Date(booking.date + ' ' + booking.time_slot + ':00:00')
        if (slotDate >= now) {
          return true
        }
      }
    }
  }
  return false
}

// 处理时段点击
function handleSlotClick(hour) {
  if (isExpired(hour)) {
    alert('已过时的时段无法操作')
    return
  }

  // 如果用户已预约，需要密码才能取消
  if (isBooked(hour)) {
    pendingAction.value = { type: 'cancel', hour: hour }
    showPasswordModal.value = true
    passwordInput.value = ''
    return
  }

  // 用户未预约时，任何状态都可以改为已预约（需要密码）
  // 不再检查场地实际状态，所有时段都可以预约
  pendingAction.value = { type: 'book', hour: hour }
  showPasswordModal.value = true
  passwordInput.value = ''
}

// 确认切换预约状态
function confirmToggle() {
  if (confirmHour.value !== null) {
    toggleBooking(confirmHour.value)
  }
  showConfirmModal.value = false
  confirmHour.value = null
}

// 验证密码
function verifyPassword() {
  if (passwordInput.value === 'qwerty') {
    // 密码正确，关闭密码弹窗，执行待执行的操作
    showPasswordModal.value = false
    passwordInput.value = ''

    if (pendingAction.value) {
      if (pendingAction.value.type === 'book') {
        // 执行预约操作
        confirmMessage.value = '确认预约该时段'
        confirmHour.value = pendingAction.value.hour
        showConfirmModal.value = true
      } else if (pendingAction.value.type === 'cancel') {
        // 执行取消预约操作
        confirmMessage.value = '取消该时段的预约'
        confirmHour.value = pendingAction.value.hour
        showConfirmModal.value = true
      }
      pendingAction.value = null
    }
  } else {
    // 密码错误
    alert('密码错误，请重试')
    passwordInput.value = ''
  }
}

// 长按处理
let pressTimer = null

function startPress(hour) {
  if (isExpired(hour)) return

  pressTimer = setTimeout(() => {
    currentHour.value = hour
    remarkTime.value = `${selectedDate.value} ${hour}:00-${hour+1}:00`

    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const booking = venueBookings.find(b => b.time_slot === hour)

    // 优先显示用户备注，如果没有则显示自动备注
    remarkText.value = booking?.remark || getAutoRemark(selectedDate.value, hour)

    showRemarkModal.value = true
  }, 500)
}

function cancelPress() {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
}

// 切换预约状态 - 使用status字段，备注独立于预约状态
async function toggleBooking(hour) {
  try {
    const isCurrentlyBooked = isBooked(hour)
    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const existingBooking = venueBookings.find(b => b.time_slot === hour)

    if (isCurrentlyBooked) {
      // 取消预约：将status设为available
      if (existingBooking && existingBooking.id) {
        // 如果有status字段，只更新status
        if (existingBooking.status !== undefined) {
          const { error } = await supabase
            .from('bookings')
            .update({ status: 'available' })
            .eq('id', existingBooking.id)

          if (error) throw error
        } else {
          // 兼容旧数据：删除记录
          const { error } = await supabase
            .from('bookings')
            .delete()
            .eq('id', existingBooking.id)

          if (error) throw error
        }
      }
    } else {
      // 预约：将status设为booked
      if (existingBooking && existingBooking.id) {
        // 如果已有记录，只更新status
        const { error } = await supabase
          .from('bookings')
          .update({ status: 'booked' })
          .eq('id', existingBooking.id)

        if (error) throw error
      } else {
        // 创建新记录，直接设为booked
        const { error } = await supabase
          .from('bookings')
          .insert({
            venue: currentVenue.value,
            date: selectedDate.value,
            time_slot: hour,
            status: 'booked'
          })

        if (error) throw error
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败，请重试')
  }
}

// 保存备注 - 备注和预约状态独立，不改变预约状态
async function saveRemark() {
  if (!currentHour.value) return

  try {
    const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
    const existingBooking = venueBookings.find(b => b.time_slot === currentHour.value)

    if (existingBooking && existingBooking.id) {
      // 如果已有记录，只更新备注
      const { error: updateError } = await supabase
        .from('bookings')
        .update({ remark: remarkText.value || '' })
        .eq('id', existingBooking.id)

      if (updateError) throw updateError
    } else {
      // 如果没有任何记录，创建一个仅有备注的记录，status默认为available
      const { error: insertError } = await supabase
        .from('bookings')
        .insert({
          venue: currentVenue.value,
          date: selectedDate.value,
          time_slot: currentHour.value,
          remark: remarkText.value || '',
          status: 'available'
        })

      if (insertError) throw insertError
    }

    showRemarkModal.value = false
    remarkText.value = ''
    currentHour.value = null
  } catch (error) {
    console.error('保存备注失败:', error)
    alert('保存备注失败，请确保已在数据库中添加 status 和 remark 字段')
  }
}

// 检查是否为周四19-21时段 (只包含19和20，即19:00-21:00)
function isThursday19to21(dateStr, hour) {
  const [year, month, day] = dateStr.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  const dayOfWeek = date.getDay() // 0=周日, 4=周四
  return dayOfWeek === 4 && hour >= 19 && hour <= 20
}

// 获取自动备注 - 只对笼式足球场显示周四备注
function getAutoRemark(dateStr, hour) {
  // 只对笼式足球场(cage)显示周四健步足球备注
  if (currentVenue.value === 'cage' && isThursday19to21(dateStr, hour)) {
    return '健步足球社团时间'
  }
  return ''
}

// 从数据库获取预约记录 - 优化：只获取最近8天的数据
async function fetchBookings() {
  try {
    // 获取今天和未来8天的日期范围
    const today = new Date()
    const endDate = new Date(today)
    endDate.setDate(today.getDate() + 8)

    const startDateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    const endDateStr = `${endDate.getFullYear()}-${String(endDate.getMonth() + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`

    const { data, error } = await supabase
      .from('bookings')
      .select('id, venue, date, time_slot, remark, status')
      .gte('date', startDateStr)
      .lte('date', endDateStr)
      .order('date', { ascending: true })
      .order('time_slot', { ascending: true })

    if (error) throw error

    bookings.value = data || []
  } catch (error) {
    console.error('获取预约记录失败:', error)
    bookings.value = []
  }
}

// 从time_slots表获取场地实际可预约状态
async function fetchVenueSlots() {
  try {
    const today = new Date()
    const endDate = new Date(today)
    endDate.setDate(today.getDate() + 8)

    const startDateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    const endDateStr = `${endDate.getFullYear()}-${String(endDate.getMonth() + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`

    const { data, error } = await supabase
      .from('time_slots')
      .select('id, venue_id, date, field_name, time, price, remaining, status')
      .gte('date', startDateStr)
      .lte('date', endDateStr)
      .order('date', { ascending: true })
      .order('time', { ascending: true })

    if (error) throw error

    venueSlots.value = data || []
    console.log('场地状态数据加载完成:', venueSlots.value.length, '条记录')
  } catch (error) {
    console.error('获取场地状态失败:', error)
    venueSlots.value = []
  }
}

// 获取某一天某时段的场地实际状态
function getVenueSlotStatus(date, hour) {
  const timeStr = `${String(hour).padStart(2, '0')}:00`
  const slot = venueSlots.value.find(
    s => s.date === date && s.time === timeStr && s.venue_id === currentVenueId.value
  )
  return slot ? slot.status : null
}

// 订阅实时更新 - 返回Promise
function subscribeToBookings() {
  // 订阅 bookings 表变化
  supabase
    .channel('bookings')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'bookings'
    }, (payload) => {
      console.log('收到 bookings 实时更新:', payload)

      if (payload.eventType === 'INSERT') {
        const exists = bookings.value.some(b => b.id === payload.new.id)
        if (!exists) {
          bookings.value.push(payload.new)
        }
      } else if (payload.eventType === 'DELETE') {
        bookings.value = bookings.value.filter(
          b => b.id !== payload.old.id
        )
      } else if (payload.eventType === 'UPDATE') {
        const index = bookings.value.findIndex(b => b.id === payload.new.id)
        if (index !== -1) {
          bookings.value[index] = payload.new
        }
      }
    })
    .subscribe()

  // 订阅 time_slots 表变化（场地状态实时更新）
  supabase
    .channel('time_slots')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'time_slots'
    }, (payload) => {
      console.log('收到 time_slots 实时更新:', payload)

      // 重新获取所有场地数据
      fetchVenueSlots()
    })
    .subscribe()
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 去除按钮默认的focus和active样式（保留按钮自定义的样式） */
button {
  outline: none !important;
  -webkit-tap-highlight-color: transparent !important;
  box-shadow: none !important;
}

button:focus {
  outline: none !important;
  box-shadow: none !important;
}

button:active {
  background-color: transparent !important;
  box-shadow: none !important;
  outline: none !important;
}

.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主内容容器 - 半透明背景 */
.main-content-wrapper {
  background: rgba(0, 0, 0, 0.3);
  min-height: 100vh;
}

/* 加载界面样式 */
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
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
}

.header {
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.current-time {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'Monaco', 'Courier New', monospace;
}

.main-content {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.venue-tabs {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.tab {
  padding: 15px 20px;
  font-size: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  outline: none !important;
  box-shadow: none !important;
}

.tab:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tab:focus {
  outline: none !important;
  box-shadow: none !important;
}

.tab.active {
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  border-color: transparent;
  color: #fff;
  font-weight: bold;
  outline: none !important;
  box-shadow: none !important;
}

.venue-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
}

.venue-status.has-booking {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
}

.venue-status.no-booking {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: #fff;
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
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
  min-height: 90px;
  outline: none !important;
  box-shadow: none !important;
}

.date-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.date-btn:focus {
  outline: none !important;
  box-shadow: none !important;
}

.date-btn.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  outline: none !important;
  box-shadow: none !important;
}

.date-day {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
}

.date-week {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.date-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  margin-top: 4px;
}

.date-status.has-booking {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
}

.date-status.no-booking {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: #fff;
}

/* 天气显示样式 - 文字描述 */
.weather-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.weather-desc {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 4px;
  border-radius: 4px;
  white-space: nowrap;
}

/* 好天气 - 晴天 */
.weather-desc[data-weather="晴天"],
.weather-desc[data-weather="晴间多云"] {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

/* 一般天气 - 多云 */
.weather-desc[data-weather="多云"],
.weather-desc[data-weather="阴"] {
  background: rgba(148, 163, 184, 0.2);
  color: #94a3b8;
}

/* 坏天气 - 雨天类 */
.weather-desc[data-weather="小毛毛雨"],
.weather-desc[data-weather="中毛毛雨"],
.weather-desc[data-weather="大毛毛雨"],
.weather-desc[data-weather="小雨"],
.weather-desc[data-weather="中雨"],
.weather-desc[data-weather="大雨"],
.weather-desc[data-weather="小阵雨"],
.weather-desc[data-weather="中阵雨"],
.weather-desc[data-weather="大阵雨"] {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

/* 恶劣天气 - 雷暴/冰雹 */
.weather-desc[data-weather="雷暴"],
.weather-desc[data-weather="雷暴+小冰雹"],
.weather-desc[data-weather="雷暴+大冰雹"] {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

/* 雪天 */
.weather-desc[data-weather="小雪"],
.weather-desc[data-weather="中雪"],
.weather-desc[data-weather="大雪"],
.weather-desc[data-weather="小阵雪"],
.weather-desc[data-weather="大阵雪"],
.weather-desc[data-weather="雪粒"] {
  background: rgba(165, 243, 252, 0.2);
  color: #a5f3fc;
}

/* 雾天 */
.weather-desc[data-weather="雾"],
.weather-desc[data-weather="雾凇"] {
  background: rgba(203, 213, 225, 0.2);
  color: #cbd5e1;
}

/* 冻雨 */
.weather-desc[data-weather="冻毛毛雨"],
.weather-desc[data-weather="强冻毛毛雨"],
.weather-desc[data-weather="小冻雨"],
.weather-desc[data-weather="大冻雨"] {
  background: rgba(34, 211, 238, 0.2);
  color: #22d3ee;
}

/* 未知天气 */
.weather-desc[data-weather="未知"] {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}

.weather-temp {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.time-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.time-slot-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.remark-display {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin-left: 4px;
}

.time-slot {
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 2px solid transparent;
  outline: none !important;
  box-shadow: none !important;
}

.time-slot:hover:not(.expired) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.time-label {
  font-size: 15px;
  font-weight: 500;
}

.time-status {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
}

.time-slot.available {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.time-slot.available:hover {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
}

.time-slot.unavailable {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.time-slot.unavailable:hover {
  background: linear-gradient(135deg, #9ca3af, #6b7280);
}

.time-slot.unbooked {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.time-slot.unbooked:hover {
  background: linear-gradient(135deg, #9ca3af, #6b7280);
}

.time-slot.booked {
  background: linear-gradient(135deg, #10b981, #059669);
}

.time-slot.booked:hover {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.time-slot.expired {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  cursor: not-allowed;
  opacity: 0.6;
}

.legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  margin-bottom: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 6px;
}

.legend-color.available {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.legend-color.unavailable {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.legend-color.unbooked {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.legend-color.booked {
  background: linear-gradient(135deg, #10b981, #059669);
}

.legend-color.expired {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.footer {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

/* 弹窗样式 */
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
}

.modal {
  background: #1a1a2e;
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
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 16px;
}

.modal-message {
  font-size: 16px;
  color: #fff;
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
  border-color: #00d4ff;
}

/* 密码输入框样式 */
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
  border-color: #00d4ff;
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
  transition: all 0.3s ease;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-confirm {
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  color: #fff;
}

.btn-confirm:hover {
  opacity: 0.9;
}
</style>
