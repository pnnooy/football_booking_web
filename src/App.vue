<template>
  <div class="app" :style="appStyle">
    <!-- 加载界面 -->
    <div v-if="isLoading" class="loading-screen" :style="loadingBgStyle">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载场地预约数据...</p>
    </div>

    <!-- 主内容 -->
    <div v-else class="main-content-wrapper">
    <button class="settings-btn" @click="showSettings = true">⚙</button>
    <button class="share-btn" @click="shareSchedule">📤</button>
    
    <header class="header">
      <h1>场地预约情况</h1>
    </header>

    <main class="main-content">
      <!-- 场地名称显示 -->
      <div class="venue-title">
        <h2>{{ venues[0].name }}</h2>
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
            <!-- 天气显示 - 和风天气 -->
            <span v-if="getWeatherForDate(date.fullDate)" class="weather-info">
              <i :class="['qi-' + getWeatherForDate(date.fullDate).iconCode, 'weather-icon']"></i>
              <span class="weather-desc">
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
            <div class="time-slot-left">
              <span class="time-label">{{ hour }}:00 - {{ hour + 1 }}:00</span>
              <!-- 天气显示 -->
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

    <!-- 设置弹窗 -->
    <div v-if="showSettings" class="settings-modal" @click="showSettings = false">
      <div class="settings-content" @click.stop>
        <h2 class="settings-title">设置</h2>
        
        <div class="settings-option" @click="showBgSettings = true">
          <div class="settings-option-title">更换背景</div>
          <div class="settings-option-desc">选择纯色背景或图片背景</div>
        </div>
        
        <div class="settings-option" @click="alert('反馈与帮助功能开发中...')">
          <div class="settings-option-title">反馈与帮助</div>
          <div class="settings-option-desc">提交反馈或获取帮助</div>
        </div>
        
        <div class="settings-option" @click="showProjectInfo = true">
          <div class="settings-option-title">项目信息</div>
          <div class="settings-option-desc">查看项目详情</div>
        </div>
        
        <div class="settings-option" @click="clearCache">
          <div class="settings-option-title">清除缓存</div>
          <div class="settings-option-desc">清除本地缓存数据</div>
        </div>
        
        <div class="settings-option" @click="refreshPage">
          <div class="settings-option-title">刷新页面</div>
          <div class="settings-option-desc">重新加载页面数据</div>
        </div>
        
        <button class="settings-close" @click="showSettings = false">关闭</button>
      </div>
    </div>

    <!-- 背景设置弹窗 -->
    <div v-if="showBgSettings" class="settings-modal" @click="showBgSettings = false">
      <div class="settings-content" @click.stop>
        <h2 class="settings-title">更换背景</h2>
        
        <div class="section-label">纯色背景</div>
        <div class="bg-options">
          <div 
            v-for="(color, index) in solidBgColors" 
            :key="index"
            class="bg-option"
            :class="{ active: currentBgType === 'solid' && currentSolidBg === color.color }"
            :style="{ background: color.color }"
            :title="color.name"
            @click="selectSolidBg(color.color)"
          ></div>
        </div>
        
        <div class="section-label">图片背景</div>
        <div class="bg-options">
          <div 
            v-for="(img, index) in bgImages" 
            :key="index"
            class="bg-option bg-option-image"
            :class="{ active: currentBgType === 'image' && currentBgImage === img }"
            :style="{ backgroundImage: `url(/bg/${img})` }"
            @click="selectImageBg(img)"
          ></div>
        </div>
        
        <button class="settings-close" @click="showBgSettings = false">返回</button>
      </div>
    </div>

    <!-- 项目信息弹窗 -->
    <div v-if="showProjectInfo" class="settings-modal" @click="showProjectInfo = false">
      <div class="settings-content" @click.stop>
        <h2 class="settings-title">项目信息</h2>
        
        <div class="project-info-item">
          <div class="project-info-label">项目名称</div>
          <div class="project-info-value">足球场地预约看板</div>
        </div>
        
        <div class="project-info-item">
          <div class="project-info-label">版本</div>
          <div class="project-info-value">2.0.0</div>
        </div>
        
        <div class="project-info-item">
          <div class="project-info-label">作者</div>
          <div class="project-info-value">PlayToday Team</div>
        </div>
        
        <div class="project-info-item">
          <div class="project-info-label">仓库</div>
          <div class="project-info-value project-info-link">
            <a href="https://github.com/playtoday/football-booking" target="_blank" rel="noopener noreferrer">
              GitHub Repository
            </a>
          </div>
        </div>
        
        <button class="settings-close" @click="showProjectInfo = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { supabase } from './supabase'

// 场地列表
const venues = [
  { id: 'cage', name: '笼式足球场', venue_id: '2b528fa8-3ce8-4a7a-8f8b-83cc537901ed' }
]

// 时间段（14:00 - 22:00，每小时一个时段）
const timeSlots = [14, 15, 16, 17, 18, 19, 20, 21]

// 当前选中的场地和日期
const currentVenue = ref('cage')
const selectedDate = ref('')
const bookings = ref([])

// 页面加载状态
const isLoading = ref(true)

// 背景图片
const bgImages = ['bg1.jpg', 'bg2.jpg', 'bg3.jpg', 'bg4.jpg', 'bg5.jpg', 'bg6.jpg', 'bg7.jpg']
const currentBgImage = ref('')

// 纯色背景选项
const solidBgColors = [
  { color: '#0a0a0a', name: '极深黑' },
  { color: '#0d0d0d', name: '深邃黑' },
  { color: '#111111', name: '墨黑' },
  { color: '#141414', name: '暗黑' },
  { color: '#171717', name: '深黑' },
  { color: '#1a1a1a', name: '纯黑' },
  { color: '#1d1d1d', name: '炭黑' },
  { color: '#202020', name: '灰黑' },
  { color: '#1a1d23', name: '深空灰' },
  { color: '#1d1d1f', name: '苹果灰' },
  { color: '#1e1e1e', name: '代码灰' },
  { color: '#212121', name: '哑光灰' },
  { color: '#242424', name: '磨砂灰' },
  { color: '#252525', name: '石墨灰' },
  { color: '#282828', name: '石板灰' },
  { color: '#2d2d2d', name: '金属灰' },
  { color: '#1a1a2e', name: '深靛蓝' },
  { color: '#16213e', name: '深海蓝' },
  { color: '#1a2332', name: '午夜蓝' },
  { color: '#1d1d2e', name: '暗紫蓝' },
  { color: '#1e2030', name: '深紫灰' },
  { color: '#152238', name: '藏青蓝' },
  { color: '#1c1c28', name: '深紫' },
  { color: '#232d3f', name: '靛蓝灰' },
  { color: '#2d1b69', name: '深紫' },
  { color: '#1e3a5f', name: '皇家蓝' },
  { color: '#2a1f3d', name: '暗紫红' },
  { color: '#1f3040', name: '深蓝' },
  { color: '#1d352c', name: '深绿' },
  { color: '#3d291d', name: '深棕' },
  { color: '#4a1942', name: '酒红' },
  { color: '#1a4a5e', name: '孔雀蓝' },
  { color: '#3d2a4f', name: '紫罗兰' },
  { color: '#1f4d40', name: '森林绿' },
  { color: '#4a3520', name: '琥珀棕' },
  { color: '#2d4a5e', name: '钢蓝' },
  { color: '#5e2d4a', name: '洋红' },
  { color: '#4a5e2d', name: '橄榄绿' }
]

// 设置相关
const showSettings = ref(false)
const showBgSettings = ref(false)
const showProjectInfo = ref(false)

// 背景类型和当前选择
const currentBgType = ref('solid') // 'solid' 或 'image'
const currentSolidBg = ref('#232d3f') // 默认靛蓝灰
const loadingBgImage = ref('') // 加载页随机背景

// 计算应用样式
const appStyle = computed(() => {
  if (currentBgType.value === 'image') {
    return {
      backgroundImage: `url(/bg/${currentBgImage.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }
  } else {
    return {
      background: currentSolidBg.value
    }
  }
})

// 加载页背景样式
const loadingBgStyle = computed(() => {
  return {
    backgroundImage: `url(/bg/${loadingBgImage.value})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat'
  }
})

// 分享预约情况
function shareSchedule() {
  alert('分享导出功能开发中，请稍后再试！')
}

// 选择纯色背景
function selectSolidBg(color) {
  currentSolidBg.value = color
  currentBgType.value = 'solid'
  localStorage.setItem('bgType', 'solid')
  localStorage.setItem('solidBg', color)
}

// 选择图片背景
function selectImageBg(img) {
  currentBgImage.value = img
  currentBgType.value = 'image'
  localStorage.setItem('bgType', 'image')
  localStorage.setItem('imageBg', img)
}

// 清除缓存
function clearCache() {
  localStorage.removeItem('weatherCache')
  localStorage.removeItem('hourlyWeatherCache')
  localStorage.removeItem('weatherCacheTime')
  alert('缓存已清除！')
  fetchWeatherData()
}

// 刷新页面
function refreshPage() {
  location.reload()
}

// 场地实际状态数据（从time_slots表获取）
const venueSlots = ref([])

// 当前选中场地的venue_id
const currentVenueId = computed(() => {
  const venue = venues.find(v => v.id === currentVenue.value)
  return venue ? venue.venue_id : ''
})

// 天气数据
const weatherData = ref({})
const hourlyWeatherData = ref([])
const weatherLoading = ref(false)

// 和风天气配置
const QWEATHER_API_KEY = '88a8f299cef84b979fd0f9ff434b57c3'
const QWEATHER_API_HOST = 'nt63yxcqx8.re.qweatherapi.com'
const QWEATHER_LOCATION = '101021200' // 上海闵行区

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



// 获取默认城市天气数据 - 使用和风天气API
async function fetchWeatherData() {
  // 先检查本地缓存
  const cachedData = localStorage.getItem('weatherCache')
  const cachedHourlyData = localStorage.getItem('hourlyWeatherCache')
  const cacheTime = localStorage.getItem('weatherCacheTime')
  const now = Date.now()

  // 如果缓存存在且未超过10分钟，直接使用缓存
  if (cachedData && cachedHourlyData && cacheTime && (now - parseInt(cacheTime)) < 10 * 60 * 1000) {
    weatherData.value = JSON.parse(cachedData)
    hourlyWeatherData.value = JSON.parse(cachedHourlyData)
    console.log('Using cached weather data')
    return
  }

  weatherLoading.value = true
  try {
    // 并行请求10日预报和72小时逐小时预报
    const [dailyResponse, hourlyResponse] = await Promise.all([
      fetch(`https://${QWEATHER_API_HOST}/v7/weather/10d?location=${QWEATHER_LOCATION}&key=${QWEATHER_API_KEY}`),
      fetch(`https://${QWEATHER_API_HOST}/v7/weather/72h?location=${QWEATHER_LOCATION}&key=${QWEATHER_API_KEY}`)
    ])

    if (!dailyResponse.ok || !hourlyResponse.ok) throw new Error('Weather API failed')

    const dailyData = await dailyResponse.json()
    const hourlyData = await hourlyResponse.json()
    const weatherMap = {}

    // 处理7日预报数据
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

    // 处理逐小时预报数据（今天和明天两天）
    if (hourlyData.hourly) {
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      const dayAfterTomorrow = new Date(tomorrow)
      dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1)
      
      hourlyWeatherData.value = hourlyData.hourly
        .filter(hour => {
          const hourDate = new Date(hour.fxTime)
          return hourDate >= now && hourDate < dayAfterTomorrow
        })
        .map(hour => ({
          time: hour.fxTime,
          temp: parseInt(hour.temp),
          iconCode: hour.icon,
          desc: hour.text,
          pop: hour.pop ? parseInt(hour.pop) : 0
        }))
    }

    weatherData.value = weatherMap

    // 保存到本地缓存
    localStorage.setItem('weatherCache', JSON.stringify(weatherMap))
    localStorage.setItem('hourlyWeatherCache', JSON.stringify(hourlyWeatherData.value))
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

// 获取指定日期和小时的逐小时天气
function getHourlyWeather(dateStr, hour) {
  if (!hourlyWeatherData.value || hourlyWeatherData.value.length === 0) {
    return null
  }
  
  const targetDateTime = `${dateStr} ${String(hour).padStart(2, '0')}:00`
  
  for (const hourData of hourlyWeatherData.value) {
    const hourDateTime = hourData.time.replace('T', ' ').substring(0, 16)
    if (hourDateTime.startsWith(targetDateTime)) {
      return hourData
    }
  }
  
  return null
}

// 初始化 selectedDate 为今天
onMounted(() => {
  // 设置加载页随机背景
  const randomIndex = Math.floor(Math.random() * bgImages.length)
  loadingBgImage.value = bgImages[randomIndex]
  
  // 从localStorage读取背景设置
  const savedBgType = localStorage.getItem('bgType')
  const savedSolidBg = localStorage.getItem('solidBg')
  const savedImageBg = localStorage.getItem('imageBg')
  
  if (savedBgType) {
    currentBgType.value = savedBgType
  }
  if (savedSolidBg) {
    currentSolidBg.value = savedSolidBg
  }
  if (savedImageBg) {
    currentBgImage.value = savedImageBg
  } else {
    currentBgImage.value = bgImages[0]
  }

  const today = new Date()
  const month = today.getMonth() + 1
  const day = today.getDate()
  selectedDate.value = `${today.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`

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
  // 清理代码（如果需要）
})

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
  // 检查是否是最后一天
  const lastDate = dateList.value[dateList.value.length - 1]?.fullDate
  const now = new Date()
  const currentHour = now.getHours()
  
  // 如果是最后一天，且当前时间在下午2点前，返回"不可选"
  if (date === lastDate && currentHour < 14) {
    return '不可选'
  }
  
  const timeStr = `${String(hour).padStart(2, '0')}:00`
  // 筛选匹配的记录
  const matchingSlots = venueSlots.value.filter(
    s => s.date === date && s.time === timeStr && s.venue_id === currentVenueId.value
  )
  
  if (matchingSlots.length === 0) {
    return null
  }
  
  // 如果有多个匹配记录，按updated_at降序排序，取最新的一条
  if (matchingSlots.length > 1) {
    console.warn(`发现 ${matchingSlots.length} 条重复记录: ${date} ${timeStr}`)
    matchingSlots.sort((a, b) => {
      const dateA = a.updated_at ? new Date(a.updated_at) : new Date(0)
      const dateB = b.updated_at ? new Date(b.updated_at) : new Date(0)
      return dateB - dateA
    })
  }
  
  return matchingSlots[0].status
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
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 设置按钮 */
.settings-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
  transition: all 0.3s;
  z-index: 100;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(45deg);
}

/* 分享按钮 */
.share-btn {
  position: fixed;
  top: 74px;
  right: 20px;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
  transition: all 0.3s;
  z-index: 100;
}

.share-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

/* 主内容容器 */
.main-content-wrapper {
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
  border-top-color: rgba(255, 255, 255, 0.6);
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
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 28px;
  color: #fff;
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
  font-size: 22px;
  color: #fff;
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
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
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

/* 天气显示样式 - 和风天气 */
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
  color: #fff !important;
}

.weather-desc {
  font-size: 10px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}

.weather-temp {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* 时段框内天气样式 */
.time-slot-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.time-slot-weather {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.slot-weather-icon {
  font-size: 20px;
  line-height: 1;
}

.slot-weather-temp {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.slot-weather-pop {
  font-size: 11px;
  color: #93c5fd;
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
  background: #3b82f6;
}

.time-slot.available:hover {
  background: #60a5fa;
}

.time-slot.unavailable {
  background: #52525b;
}

.time-slot.unavailable:hover {
  background: #62626b;
}

.time-slot.unbooked {
  background: #52525b;
}

.time-slot.unbooked:hover {
  background: #62626b;
}

.time-slot.booked {
  background: #10b981;
}

.time-slot.booked:hover {
  background: #34d399;
}

.time-slot.expired {
  background: #6b7280;
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
  background: #3b82f6;
  color: #fff;
}

.btn-confirm:hover {
  opacity: 0.9;
}

/* 设置弹窗样式 */
.settings-modal {
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 200;
  align-items: center;
  justify-content: center;
}

.settings-content {
  background: #252525;
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  max-height: 85vh;
  overflow-y: auto;
}

.settings-content::-webkit-scrollbar {
  width: 4px;
}

.settings-content::-webkit-scrollbar-track {
  background: transparent;
}

.settings-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.settings-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
  text-align: center;
}

.settings-option {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.settings-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.settings-option-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.settings-option-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.settings-close {
  display: block;
  width: 100%;
  padding: 14px;
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.settings-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 16px 0 10px;
}

.section-label:first-of-type {
  margin-top: 0;
}

.bg-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.bg-option {
  aspect-ratio: 1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.bg-option:hover {
  transform: scale(1.05);
}

.bg-option.active {
  border-color: #fff;
}

.bg-option-image {
  background-size: cover;
  background-position: center;
}

.project-info-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.project-info-item:last-of-type {
  border-bottom: none;
}

.project-info-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.project-info-value {
  font-size: 15px;
  font-weight: 500;
}

.project-info-link a {
  color: #60a5fa;
  text-decoration: none;
}

.project-info-link a:hover {
  text-decoration: underline;
}
</style>
