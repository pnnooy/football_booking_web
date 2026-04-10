<template>
  <div class="app" :class="currentTheme">
    <!-- 加载界面 -->
    <div v-if="isLoading" class="loading-screen" :style="loadingBgStyle">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载场地预约数据...</p>
    </div>

    <!-- 主内容 -->
    <div v-else class="main-container">
      <div class="page-content">
        <!-- 场地情况页面 -->
        <div id="venue-page" class="venue-page" :class="{ active: currentPage === 'venue' }">
          <header class="page-header">
            <div class="page-header-content">
              <h1>{{ venues[0].name }}</h1>
              <button class="share-btn-fixed" @click="shareSchedule">📤</button>
            </div>
          </header>

          <main class="main-content">

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

        <!-- 设置页面 -->
        <div id="settings-page" class="settings-page" :class="{ active: currentPage === 'settings' }">
          <header class="settings-header">
            <h2>设置</h2>
          </header>

          <div class="settings-body">
            <!-- 第一组：主题配色 -->
            <div class="settings-section">
              <div class="section-title">主题配色</div>
              <div class="theme-grid">
                <div class="theme-item" :class="{ active: currentTheme === 'theme-light' }" @click="selectTheme('theme-light')" style="background: #2b6cb0;">
                  <div class="theme-check" v-if="currentTheme === 'theme-light'">✓</div>
                  <span class="theme-name">浅灰蓝-低调版</span>
                </div>
                <div class="theme-item" :class="{ active: currentTheme === 'theme-dark' }" @click="selectTheme('theme-dark')" style="background: #3b82f6;">
                  <div class="theme-check" v-if="currentTheme === 'theme-dark'">✓</div>
                  <span class="theme-name">深蓝灰-柔和版</span>
                </div>
              </div>
            </div>

            <!-- 第二组：外观设置 -->
            <div class="settings-section">
              <div class="section-title">外观设置</div>
              <div class="section-content">
                <div class="settings-item">
                  <div class="settings-text">
                    <div class="settings-item-title">更换背景</div>
                    <div class="settings-item-desc">选择主题配色</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <!-- 第三组：反馈与帮助 -->
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

            <!-- 第四组：缓存管理 -->
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

            <!-- 第五组：项目信息 -->
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

            <!-- 第六组：安全与隐私 -->
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
        <button class="tab-item" :class="{ active: currentPage === 'venue' }" @click="switchPage('venue')">
          <span class="tab-icon">⚽</span>
          <span class="tab-label">场地情况</span>
        </button>
        <button class="tab-item" :class="{ active: currentPage === 'settings' }" @click="switchPage('settings')">
          <span class="tab-icon">⚙️</span>
          <span class="tab-label">设置</span>
        </button>
      </nav>
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

    <!-- 问题反馈弹窗 -->
    <div v-if="showFeedbackModal" class="modal-overlay" @click="showFeedbackModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>问题反馈</h3>
          <button class="modal-close" @click="showFeedbackModal = false">✕</button>
        </div>
        <div class="modal-body">
          <textarea class="modal-textarea" placeholder="请描述您遇到的问题..."></textarea>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showFeedbackModal = false">取消</button>
          <button class="modal-btn modal-btn-primary" @click="submitFeedback">提交</button>
        </div>
      </div>
    </div>

    <!-- 功能建议弹窗 -->
    <div v-if="showSuggestionModal" class="modal-overlay" @click="showSuggestionModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>功能建议</h3>
          <button class="modal-close" @click="showSuggestionModal = false">✕</button>
        </div>
        <div class="modal-body">
          <textarea class="modal-textarea" placeholder="请描述您的建议..."></textarea>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showSuggestionModal = false">取消</button>
          <button class="modal-btn modal-btn-primary" @click="submitSuggestion">提交</button>
        </div>
      </div>
    </div>

    <!-- 项目信息弹窗 -->
    <div v-if="showProjectInfo" class="modal-overlay" @click="showProjectInfo = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>项目信息</h3>
          <button class="modal-close" @click="showProjectInfo = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-card">
            <div class="info-item">
              <span class="info-label">项目介绍</span>
              <span class="info-value">足球场地预约看板，实时查看场地预约情况，支持天气查询和预约管理</span>
            </div>
            <div class="info-item">
              <span class="info-label">版本信息</span>
              <span class="info-value version-badge">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新日志</span>
              <span class="info-value">v1.0.0 - 初始版本发布</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-primary" @click="showProjectInfo = false">确定</button>
        </div>
      </div>
    </div>

    <!-- 开发者信息弹窗 -->
    <div v-if="showDeveloperInfo" class="modal-overlay" @click="showDeveloperInfo = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>开发者信息</h3>
          <button class="modal-close" @click="showDeveloperInfo = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-card">
            <div class="info-item">
              <span class="info-label">作者信息</span>
              <span class="info-value">pnnooy</span>
            </div>
            <div class="info-item">
              <span class="info-label">GitHub仓库</span>
              <a href="https://github.com/pnnooy/football_booking_web" target="_blank" class="info-link">
                github.com/pnnooy/football_booking_web
              </a>
            </div>
            <div class="info-item">
              <span class="info-label">开源协议</span>
              <span class="info-value">MIT License</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-primary" @click="showDeveloperInfo = false">确定</button>
        </div>
      </div>
    </div>

    <!-- 责任声明弹窗 -->
    <div v-if="showLiabilityModal" class="modal-overlay" @click="showLiabilityModal = false">
      <div class="modal-content modal-content-large" @click.stop>
        <div class="modal-header">
          <h3>责任声明</h3>
          <button class="modal-close" @click="showLiabilityModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-card">
            <div class="info-section">
              <div class="info-section-title">使用条款</div>
              <div class="info-section-content">
                1. 本项目仅供学习和交流使用<br>
                2. 请合理安排预约时间，避免场地浪费<br>
                3. 预约成功后请按时到场
              </div>
            </div>
            <div class="info-section" style="margin-top: 12px;">
              <div class="info-section-title">免责声明</div>
              <div class="info-section-content">
                1. 场地实际状态以现场为准<br>
                2. 天气数据仅供参考<br>
                3. 因使用本项目造成的任何损失，开发者不承担责任
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-primary" @click="showLiabilityModal = false">确定</button>
        </div>
      </div>
    </div>

    <!-- 使用帮助弹窗 -->
    <div v-if="showHelpModal" class="modal-overlay" @click="showHelpModal = false">
      <div class="modal-content modal-content-large" @click.stop>
        <div class="modal-header">
          <h3>使用帮助</h3>
          <button class="modal-close" @click="showHelpModal = false">✕</button>
        </div>
        <div class="modal-body help-content">
          <div class="help-section">
            <h4>基本使用</h4>
            <p>1. <strong>查看预约</strong>：选择日期后，下方会显示该日期的所有时间段预约情况</p>
            <p>2. <strong>预约场地</strong>：点击"可预约"的时间段，输入管理员密码即可完成预约</p>
            <p>3. <strong>取消预约</strong>：点击"已预约"的时间段，输入密码即可取消</p>
          </div>
          <div class="help-section">
            <h4>天气功能</h4>
            <p>1. 每个日期上方会显示当天的天气概况</p>
            <p>2. 每个时间段会显示该时段的天气和降水概率</p>
            <p>3. 天气数据每小时自动更新</p>
          </div>
          <div class="help-section">
            <h4>设置功能</h4>
            <p>1. <strong>主题配色</strong>：支持浅灰蓝-低调版和深蓝灰-柔和版两种主题</p>
            <p>2. <strong>分享功能</strong>：可将预约情况导出为图片分享</p>
            <p>3. <strong>清除缓存</strong>：清除天气缓存或所有本地数据</p>
          </div>
          <div class="help-section">
            <h4>常见问题</h4>
            <p><strong>Q: 为什么显示"暂无数据"？</strong></p>
            <p>A: 数据每天下午2点左右更新，请稍后再试。</p>
            <p><strong>Q: 天气数据准确吗？</strong></p>
            <p>A: 天气数据来自和风天气API，仅供参考。</p>
            <p><strong>Q: 如何修改管理员密码？</strong></p>
            <p>A: 目前需要联系开发者修改。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { supabase } from './supabase'

// 动态加载html2canvas（仅CDN方式）
async function loadHtml2Canvas() {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载
    if (window.html2canvas) {
      resolve(window.html2canvas)
      return
    }
    
    // 从CDN加载
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js'
    script.onload = () => {
      resolve(window.html2canvas)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

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

// 背景图片（仅用于加载页面）
const bgImages = ['bg1.jpg', 'bg2.jpg', 'bg3.jpg', 'bg4.jpg', 'bg5.jpg', 'bg6.jpg', 'bg7.jpg']
const loadingBgImage = ref('')

// 当前页面和主题
const currentPage = ref('venue')
const currentTheme = ref('theme-light')

// 设置相关
const showProjectInfo = ref(false)
const showDeveloperInfo = ref(false)
const showLiabilityModal = ref(false)
const showFeedbackModal = ref(false)
const showSuggestionModal = ref(false)
const showHelpModal = ref(false)

// 加载页背景样式
const loadingBgStyle = computed(() => {
  return {
    backgroundImage: `url(/bg/${loadingBgImage.value})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat'
  }
})

// 切换页面
function switchPage(page) {
  currentPage.value = page
}

// 选择主题
function selectTheme(theme) {
  currentTheme.value = theme
  localStorage.setItem('theme', theme)
}

// 分享预约情况
async function shareSchedule() {
  try {
    // 动态加载html2canvas
    const h2c = await loadHtml2Canvas()
    
    // 先隐藏底栏和分享按钮，防止截图时包含
    const tabBar = document.querySelector('.tab-bar')
    const shareBtn = document.querySelector('.share-btn-fixed')
    if (tabBar) tabBar.style.display = 'none'
    if (shareBtn) shareBtn.style.display = 'none'

    // 等待DOM更新
    await nextTick()

    // 获取主内容区域
    const element = document.querySelector('.venue-page.active')
    if (!element) {
      alert('无法获取页面内容')
      return
    }

    // 使用html2canvas截图
    const canvas = await h2c(element, {
      scale: 2,
      useCORS: true,
      backgroundColor: currentTheme.value === 'theme-light' ? '#f7fafc' : '#0f172a',
      allowTaint: true,
      logging: false,
      letterRendering: true
    })

    // 恢复显示
    if (tabBar) tabBar.style.display = 'flex'
    if (shareBtn) shareBtn.style.display = 'flex'

    // 创建下载链接
    const link = document.createElement('a')
    const dateStr = new Date().toISOString().split('T')[0]
    link.download = `足球场地预约_${dateStr}.png`
    link.href = canvas.toDataURL('image/png')

    // 检测是否在微信浏览器中
    const isWeChat = /MicroMessenger/i.test(navigator.userAgent)
    
    if (isWeChat) {
      // 在微信中，显示预览图让用户长按保存
      const previewImg = document.createElement('img')
      previewImg.src = canvas.toDataURL('image/png')
      previewImg.style.maxWidth = '90%'
      previewImg.style.maxHeight = '80vh'
      previewImg.style.borderRadius = '12px'
      
      const previewDiv = document.createElement('div')
      previewDiv.style.position = 'fixed'
      previewDiv.style.top = '0'
      previewDiv.style.left = '0'
      previewDiv.style.right = '0'
      previewDiv.style.bottom = '0'
      previewDiv.style.background = 'rgba(0,0,0,0.9)'
      previewDiv.style.display = 'flex'
      previewDiv.style.flexDirection = 'column'
      previewDiv.style.alignItems = 'center'
      previewDiv.style.justifyContent = 'center'
      previewDiv.style.zIndex = '9999'
      
      const hintText = document.createElement('div')
      hintText.style.color = '#fff'
      hintText.style.fontSize = '16px'
      hintText.style.marginTop = '20px'
      hintText.style.textAlign = 'center'
      hintText.innerHTML = '长按图片保存到相册\n或分享给好友'
      
      const closeBtn = document.createElement('button')
      closeBtn.innerText = '关闭'
      closeBtn.style.marginTop = '20px'
      closeBtn.style.padding = '10px 30px'
      closeBtn.style.background = 'rgba(255,255,255,0.2)'
      closeBtn.style.border = 'none'
      closeBtn.style.borderRadius = '20px'
      closeBtn.style.color = '#fff'
      closeBtn.style.fontSize = '14px'
      closeBtn.style.cursor = 'pointer'
      
      closeBtn.addEventListener('click', () => {
        document.body.removeChild(previewDiv)
      })
      
      previewDiv.appendChild(previewImg)
      previewDiv.appendChild(hintText)
      previewDiv.appendChild(closeBtn)
      document.body.appendChild(previewDiv)
    } else {
      // 非微信浏览器，正常下载
      link.click()
      
      // 尝试使用Web Share API（如果支持）
      if (navigator.share) {
        try {
          // 将canvas转为blob
          canvas.toBlob(async (blob) => {
            if (blob) {
              const file = new File([blob], `足球场地预约_${dateStr}.png`, { type: 'image/png' })
              try {
                await navigator.share({
                  title: '足球场地预约情况',
                  text: `查看${dateStr}的足球场地预约情况`,
                  files: [file]
                })
              } catch (err) {
                console.log('分享被取消或不支持分享文件')
              }
            }
          })
        } catch (err) {
          console.log('Web Share API不可用', err)
        }
      }
    }

  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
    
    // 确保恢复显示
    const tabBar = document.querySelector('.tab-bar')
    const shareBtn = document.querySelector('.share-btn-fixed')
    if (tabBar) tabBar.style.display = 'flex'
    if (shareBtn) shareBtn.style.display = 'flex'
  }
}

// 清除天气缓存
function clearWeatherCache() {
  localStorage.removeItem('weatherCache')
  localStorage.removeItem('hourlyWeatherCache')
  localStorage.removeItem('weatherCacheTime')
  alert('天气缓存已清除！')
  fetchWeatherData()
}

// 清除所有本地数据
function clearAllCache() {
  if (confirm('确定要清除所有本地数据吗？此操作不可恢复。')) {
    localStorage.clear()
    alert('所有本地数据已清除！')
    location.reload()
  }
}

// 清除浏览记录
function clearBrowsingHistory() {
  if (confirm('确定要清除浏览记录吗？')) {
    localStorage.removeItem('bookingHistory')
    alert('浏览记录已清除！')
  }
}

// 提交反馈
function submitFeedback() {
  alert('感谢您的反馈！我们会尽快处理。')
  showFeedbackModal.value = false
}

// 提交建议
function submitSuggestion() {
  alert('感谢您的建议！我们会认真考虑。')
  showSuggestionModal.value = false
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
  
  // 从localStorage读取主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    currentTheme.value = savedTheme
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
  -webkit-tap-highlight-color: transparent;
}

/* ============ 白色系（浅灰蓝-低调版） ============ */
.theme-light {
  --bg-primary: #f7fafc;
  --bg-secondary: #ffffff;
  --bg-card: #edf2f7;
  --bg-hover: #e2e8f0;
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --accent: #2b6cb0;
  --accent-hover: #2c5282;
  --accent-light: #e6f0fa;
  --success: #276749;
  --success-light: #e8f5e9;
  --warning: #b45309;
  --danger: #b91c1c;
  --border: #e2e8f0;
  --border-light: #edf2f7;
}

/* ============ 黑色系（深蓝灰-柔和版） ============ */
.theme-dark {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #334155;
  --bg-hover: #475569;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --accent-light: #1e3a5f;
  --success: #059669;
  --success-light: #064e3b;
  --warning: #d97706;
  --danger: #dc2626;
  --border: #475569;
  --border-light: #334155;
}

.app {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  height: 100vh;
}

/* 去除所有按钮的点击高亮效果 */
button {
  -webkit-tap-highlight-color: transparent !important;
  outline: none !important;
  box-shadow: none !important;
}

button:focus {
  outline: none !important;
  box-shadow: none !important;
}

button:active {
  box-shadow: none !important;
  outline: none !important;
}

/* ============ 页面容器 ============ */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 70px;
  position: relative;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* ============ 加载界面样式 ============ */
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

/* ============ 页面头部 ============ */
.page-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  position: relative;
  background: var(--bg-primary);
  z-index: 10;
}

.page-header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 600;
}

.settings-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  background: var(--bg-primary);
}

.settings-header h2 {
  font-size: 20px;
  font-weight: 600;
}

/* ============ 分享按钮 ============ */
.share-btn-fixed {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  background: var(--bg-card);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

/* ============ 场地页面 ============ */
.venue-page,
.settings-page {
  display: none;
  min-height: 100%;
}

.venue-page.active,
.settings-page.active {
  display: block;
}

.main-content {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.venue-title {
  text-align: center;
  margin-bottom: 24px;
}

.venue-title h2 {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* ============ 日期导航 ============ */
.date-nav {
  margin-bottom: 24px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.dates-scroll {
  display: flex;
  gap: 10px;
  padding: 5px 0;
}

.date-btn {
  flex-shrink: 0;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 14px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 78px;
  min-height: 100px;
}

.date-btn.active {
  background: var(--bg-secondary);
  border-color: var(--accent);
}

.date-btn.active .date-day {
  color: var(--text-primary);
}

.date-btn.active .date-week {
  color: var(--text-secondary);
}

.date-btn.active .date-status {
  background: var(--bg-card);
  color: var(--text-secondary);
}

.date-btn.active .date-status.has-booking {
  background: var(--success);
  color: #fff;
}

.date-day {
  font-size: 22px;
  font-weight: bold;
}

.date-week {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 4px;
}

.date-btn.active .date-week {
  color: rgba(255, 255, 255, 0.85);
}

.date-status {
  font-size: 10px;
  padding: 2px 10px;
  border-radius: 12px;
  margin-top: 8px;
  font-weight: 600;
  background: var(--bg-card);
  color: var(--text-secondary);
}

.date-status.has-booking {
  background: var(--success);
  color: #fff;
}

.date-btn.active .date-status.no-booking {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

/* ============ 天气显示样式 - 和风天气 ============ */
.weather-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border-light);
}

.weather-icon {
  font-size: 24px;
  line-height: 1;
}

.theme-dark .weather-icon {
  color: #fff !important;
}

.weather-desc {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

.weather-temp {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* ============ 时段框内天气样式 ============ */
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
}

.slot-weather-pop {
  font-size: 11px;
  color: #93c5fd;
  font-weight: 500;
}

/* ============ 时间网格 ============ */
.time-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
}

.time-slot-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.remark-display {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 6px 12px;
  background: var(--bg-card);
  border-radius: 6px;
  margin-left: 4px;
}

.time-slot {
  padding: 18px 20px;
  border-radius: 14px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 2px solid transparent;
}

.time-label {
  font-size: 16px;
  font-weight: 600;
}

.time-status {
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.06);
  font-weight: 600;
}

/* ============ 时间槽配色 - 柔和版 ============ */
.time-slot.available {
  background: var(--accent-light);
  color: var(--accent);
  border: 2px solid var(--accent);
}

.time-slot.available .time-status {
  background: var(--accent);
  color: #fff;
}

.time-slot.unavailable {
  background: var(--bg-card);
  opacity: 0.6;
}

.time-slot.booked {
  background: var(--success-light);
  color: var(--success);
  border: 2px solid var(--success);
}

.time-slot.booked .time-status {
  background: var(--success);
  color: #fff;
}

.time-slot.expired {
  background: var(--bg-secondary);
  cursor: not-allowed;
  opacity: 0.5;
}

/* ============ 设置页面 ============ */
.settings-body {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.settings-section {
  margin-bottom: 32px;
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
  border: 1px solid var(--border);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  padding: 14px;
}

.theme-item {
  aspect-ratio: 1.5;
  border-radius: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid transparent;
  position: relative;
}

.theme-item.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.theme-check {
  font-size: 28px;
  color: #fff;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.theme-name {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  background: rgba(0,0,0,0.7);
  color: #fff;
  padding: 4px 12px;
  border-radius: 10px;
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
  text-align: left;
  width: 100%;
}

.settings-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  font-size: 22px;
  color: var(--text-secondary);
  margin-left: 8px;
  font-weight: 300;
  flex-shrink: 0;
}

/* ============ 底栏导航 ============ */
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
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
}

.tab-icon {
  font-size: 26px;
  margin-bottom: 4px;
  opacity: 0.5;
}

.tab-label {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.5;
}

.tab-item.active .tab-icon,
.tab-item.active .tab-label {
  opacity: 1;
  color: var(--accent);
}

/* ============ 弹窗样式 ============ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 100%;
}

.modal h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.modal-message {
  font-size: 16px;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.password-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 16px;
  margin-bottom: 20px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-time {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.modal textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 16px;
  margin-bottom: 20px;
  background: var(--bg-primary);
  color: var(--text-primary);
  resize: vertical;
  font-family: inherit;
}

.modal-buttons {
  display: flex;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel {
  background: var(--bg-card);
  color: var(--text-primary);
}

.btn-confirm {
  background: var(--accent);
  color: #fff;
}

/* ============ 新弹窗样式 ============ */
.modal-content {
  background: var(--bg-secondary);
  border-radius: 16px;
  max-width: 400px;
  width: 100%;
  overflow: hidden;
}

.modal-content-large {
  max-width: 500px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 20px;
}

.modal-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 16px;
  background: var(--bg-primary);
  color: var(--text-primary);
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}

.modal-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.modal-btn-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
}

.modal-btn-primary {
  background: var(--accent);
  color: #fff;
}

/* ============ 信息卡片样式 ============ */
.info-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 16px;
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
  background: var(--accent-light);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
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

/* ============ 帮助内容样式 ============ */
.help-content {
  padding: 0;
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
  color: var(--text-primary);
  font-weight: 500;
}
</style>