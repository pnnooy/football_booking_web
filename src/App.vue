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
              <button class="share-btn-fixed" @click="shareSchedule">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link icon-share">
                  <path d="M15 3h6v6"></path>
                  <path d="M10 14 21 3"></path>
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                </svg>
              </button>
            </div>
          </header>

          <main class="main-content">

            <!-- 预约预览条 -->
            <div class="booking-preview-bar">
              <div class="preview-bar-container">
                <div
                  v-for="(date, index) in dateList"
                  :key="index"
                  :class="['preview-bar-item', hasDateBooking(date.fullDate) ? 'has-booking' : '']"
                >
                  <span class="preview-bar-day">{{ getWeekDayChar(date.week) }}</span>
                </div>
              </div>
            </div>

            <!-- 日期导航 -->
            <div class="date-nav">
              <div class="dates-scroll">
                <button
                  v-for="(date, index) in dateList"
                  :key="index"
                  :class="['date-btn', { active: selectedDate === date.fullDate }]"
                  @click="selectDate(date.fullDate)"
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
                  :class="['time-slot', getSlotClass(hour), { 'time-slot-locked': !isAdminLoggedIn }]"
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
                  <div class="time-slot-right">
                    <!-- 想踢数量显示 -->
                    <div v-if="currentWantToPlay[hour] > 0" class="want-to-play-badge">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" class="want-to-play-icon">
                        <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                          <path d="M11 4a1 1 0 1 0 2 0a1 1 0 0 0-2 0M3 17l5 1l.75-1.5M14 21v-4l-4-3l1-6"/>
                          <path d="M6 12V9l5-1l3 3l3 1"/>
                          <path fill="currentColor" d="M19.5 20a.5.5 0 1 0 0-1a.5.5 0 0 0 0 1"/>
                        </g>
                      </svg>
                      想踢×{{ currentWantToPlay[hour] }}
                    </div>
                    <span class="time-status">{{ getSlotStatus(hour) }}</span>
                  </div>
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
            <!-- 第一组：主题 -->
            <div class="settings-section">
              <div class="section-title">主题</div>
              <div class="theme-selector">
                <div class="theme-option" :class="{ active: themeMode === 'light' }" @click="setThemeMode('light')">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="theme-icon">
                    <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                      <circle cx="12" cy="12" r="5"></circle>
                      <path d="M12 1v2m0 18v2M4.2 4.2l1.4 1.4m12.8 12.8l1.4 1.4M1 12h2m18 0h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"></path>
                    </g>
                  </svg>
                  <span class="theme-label">浅色</span>
                </div>
                <div class="theme-option" :class="{ active: themeMode === 'dark' }" @click="setThemeMode('dark')">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="theme-icon">
                    <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3h.393a7.5 7.5 0 0 0 7.92 12.446A9 9 0 1 1 12 2.992z"></path>
                  </svg>
                  <span class="theme-label">深色</span>
                </div>
                <div class="theme-option" :class="{ active: themeMode === 'system' }" @click="setThemeMode('system')">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" class="theme-icon">
                    <path fill="currentColor" d="M10.25 2A3.25 3.25 0 0 0 7 5.25v21.5A3.25 3.25 0 0 0 10.25 30h11.5A3.25 3.25 0 0 0 25 26.75V5.25A3.25 3.25 0 0 0 21.75 2zM9 5.25C9 4.56 9.56 4 10.25 4h11.5c.69 0 1.25.56 1.25 1.25v21.5c0 .69-.56 1.25-1.25 1.25h-11.5C9.56 28 9 27.44 9 26.75zM14 24a1 1 0 1 0 0 2h4a1 1 0 1 0 0-2z"></path>
                  </svg>
                  <span class="theme-label">跟随系统</span>
                </div>
              </div>
            </div>

            <!-- 第二组：帮助 -->
            <div class="settings-section">
              <div class="section-title">帮助</div>
              <div class="section-content">
                <div class="settings-item" @click="showHelpModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">使用帮助</div>
                    <div class="settings-item-desc">查看使用说明和常见问题</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
              </div>
            </div>

            <!-- 第三组：反馈与建议 -->
            <div class="settings-section">
              <div class="section-title">反馈与建议</div>
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

            <!-- 第七组：管理员功能 -->
            <div class="settings-section">
              <div class="section-title">管理员功能</div>
              <div class="section-content">
                <div v-if="!isAdminLoggedIn" class="settings-item" @click="showAdminLoginModal = true">
                  <div class="settings-text">
                    <div class="settings-item-title">管理员登录</div>
                    <div class="settings-item-desc">管理员入口</div>
                  </div>
                  <span class="settings-arrow">›</span>
                </div>
                <template v-else>
                  <div class="settings-item" :class="{ 'feedback-unresolved': hasUnresolvedFeedback }" @click="showFeedbackListModal = true; fetchFeedbackList()">
                    <div class="settings-text">
                      <div class="settings-item-title">反馈管理</div>
                      <div class="settings-item-desc">查看所有用户反馈</div>
                    </div>
                    <span v-if="hasUnresolvedFeedback" class="feedback-badge">新</span>
                    <span class="settings-arrow">›</span>
                  </div>
                  <div class="settings-item" @click="handleAdminLogout">
                    <div class="settings-text">
                      <div class="settings-item-title">退出登录</div>
                      <div class="settings-item-desc">当前已登录</div>
                    </div>
                    <span class="settings-arrow">›</span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底栏导航 -->
      <nav class="tab-bar">
        <button class="tab-item" :class="{ active: currentPage === 'venue' }" @click="switchPage('venue')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" class="tab-icon">
            <path fill="currentColor" d="M6.224 48.672h43.552c4.143 0 6.224-2.061 6.224-6.145V16.62c0-4.084-2.081-6.146-6.224-6.146H6.224C2.101 10.473 0 12.515 0 16.62v25.908c0 4.084 2.101 6.145 6.224 6.145m.06-3.191c-1.982 0-3.092-1.07-3.092-3.132v-2.874h5.57c2.933 0 4.658-1.725 4.658-4.659V24.31c0-2.934-1.725-4.658-4.658-4.658h-5.57v-2.875c0-2.042 1.11-3.112 3.092-3.112h20.06v6.68c-4.42.714-7.75 4.54-7.75 9.218s3.33 8.504 7.75 9.238v6.68Zm31.003-15.918c-.04-4.658-3.31-8.425-7.75-9.198v-6.7h20.179c1.962 0 3.092 1.07 3.092 3.112v2.874h-5.57c-2.934 0-4.658 1.725-4.658 4.659v10.506c0 2.934 1.724 4.658 4.658 4.658h5.57v2.875c0 2.061-1.13 3.132-3.092 3.132h-20.18V38.8c4.46-.754 7.81-4.56 7.751-9.238m10.01 6.72c-.971 0-1.526-.555-1.526-1.526V24.369c0-.971.555-1.526 1.526-1.526h5.511v13.44ZM8.703 22.843c.972 0 1.527.555 1.527 1.526v10.388c0 .97-.555 1.526-1.527 1.526h-5.51v-13.44Zm12.766 6.7a6.41 6.41 0 0 1 4.877-6.244v12.528c-2.775-.714-4.877-3.27-4.877-6.284m12.945 0c-.04 3.013-2.102 5.57-4.877 6.284V23.319c2.795.713 4.896 3.23 4.877 6.224"></path>
          </svg>
          <span class="tab-label">场地情况</span>
        </button>
        <button class="tab-item" :class="{ active: currentPage === 'settings' }" @click="switchPage('settings')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings-icon lucide-settings tab-icon">
            <path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
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
          <textarea v-model="feedbackContent" class="modal-textarea" placeholder="请描述您遇到的问题..."></textarea>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showFeedbackModal = false; feedbackContent = ''">取消</button>
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
          <textarea v-model="feedbackContent" class="modal-textarea" placeholder="请描述您的建议..."></textarea>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showSuggestionModal = false; feedbackContent = ''">取消</button>
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
              <span class="info-value">足球场地预约看板，实时查看场地预约情况，支持实时天气查询、想踢人数登记和分享功能</span>
            </div>
            <div class="info-item">
              <span class="info-label">版本信息</span>
              <span class="info-value version-badge">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新日志</span>
              <span class="info-value">
                v1.0.0 - 初始版本发布<br>
                - 支持场地预约状态查看<br>
                - 集成实时天气查询功能<br>
                - 支持想踢人数登记功能<br>
                - 支持预约图片导出分享
              </span>
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
              <span class="info-value">
                pony<br>
                hanyufei24@sjtu.edu.cn<br>
                <a href="https://github.com/pnnooy" target="_blank" class="info-link">
                  https://github.com/pnnooy
                </a>
              </span>
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
                1. 本项目仅供学习交流和个人非商业用途使用<br>
                2. 请合理安排时间，避免场地资源浪费<br>
                3. 想踢功能仅用于表达意向，不代表实际预约<br>
                4. 请勿提交恶意或虚假的反馈和建议<br>
                5. 该网页仅限本群使用，与其他个人/组织无关
              </div>
            </div>
            <div class="info-section" style="margin-top: 12px;">
              <div class="info-section-title">免责声明</div>
              <div class="info-section-content">
                1. 数据更新存在延迟，场地实际状态以实际情况为准，本系统数据仅供参考<br>
                2. 因使用本项目造成的任何直接或间接损失，开发者不承担责任<br>
                3. 系统可能会因维护、网络问题等原因功能异常<br>
                4. 用户提交的反馈和建议会被用于产品改进
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
            <p><strong>查看预约</strong>：选择日期即可查看该日期所有时段的预约情况</p>
            <p><strong>想踢登记</strong>：点击任意时段，在弹出的窗口中点击"想踢+1"即可登记您的意向；再次点击可取消登记</p>
            <p><strong>日期天气</strong>：每个日期按钮上方会显示当天的天气概况</p>
            <p><strong>时段天气</strong>：每个时段块内会显示两天内时段的具体天气</p>
            <p><strong>自动更新</strong>：天气数据每10分钟自动更新一次，您也可以在设置中手动清除天气缓存来强制刷新</p>
            <p><strong>主题切换</strong>：支持浅色模式、深色模式和跟随系统三种主题</p>
            <p><strong>分享功能</strong>：点击场地情况页面右上角的分享按钮，可将当前预约情况导出为图片保存或分享</p>
            <p><strong>反馈建议</strong>：可在设置-反馈与帮助提交您的问题反馈或产品建议</p>
          </div>
          <div class="help-section">
            <h4>常见问题</h4>
            <p><strong>Q: 想踢功能有什么用？会帮我预约吗？</strong></p>
            <p>A: 想踢功能仅用于表达您的意向，方便组织者了解大家的需求，不会自动预约场地，踢球请在群聊内接龙。</p>
            <p><strong>Q: 我提交的反馈与建议会被看到吗？</strong></p>
            <p>A: 是的，管理员可以在后台看到所有反馈和建议，我们会认真阅读并考虑。</p>
            <p><strong>Q: 为什么最后一天的数据在下午2点前显示"不可选"？</strong></p>
            <p>A: 数据通常在每天下午2点左右更新，请在2点后再查看最新数据。</p>
            <p><strong>Q: 为什么全部时段都显示可预约？</strong></p>
            <p>A: 您的网络环境异常，请切换WLAN/移动数据或更换浏览器重试。</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 管理员登录弹窗 -->
    <div v-if="showAdminLoginModal" class="modal-overlay" @click="showAdminLoginModal = false">
      <div class="modal" @click.stop>
        <h3>管理员登录</h3>
        <input
          v-model="adminEmail"
          type="email"
          class="password-input"
          placeholder="请输入邮箱..."
          @keyup.enter="adminPassword ? handleAdminLogin() : null"
          autofocus
        />
        <input
          v-model="adminPassword"
          type="password"
          class="password-input"
          placeholder="请输入密码..."
          style="margin-top: 10px;"
          @keyup.enter="handleAdminLogin"
        />
        <div class="modal-buttons">
          <button class="btn-cancel" @click="showAdminLoginModal = false">取消</button>
          <button class="btn-confirm" @click="handleAdminLogin">登录</button>
        </div>
      </div>
    </div>

    <!-- 反馈管理弹窗 -->
    <div v-if="showFeedbackListModal" class="modal-overlay" @click="showFeedbackListModal = false">
      <div class="modal-content modal-content-large" @click.stop>
        <div class="modal-header">
          <h3>反馈管理</h3>
          <button class="modal-close" @click="showFeedbackListModal = false">✕</button>
        </div>
        <div class="modal-body help-content" style="max-height: 60vh; overflow-y: auto;">
          <div v-if="feedbackList.length === 0" style="text-align: center; padding: 40px; color: var(--text-secondary);">
            暂无反馈
          </div>
          <div v-else class="help-section" v-for="item in feedbackList" :key="item.id" style="border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
              <span style="background: var(--accent-light); color: var(--accent); padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                {{ item.type === 'feedback' ? '问题反馈' : '功能建议' }}
              </span>
              <span v-if="item.status === 'resolved'" style="background: var(--success-light); color: var(--success); padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                已处理
              </span>
            </div>
            <p style="margin-bottom: 8px; white-space: pre-wrap; word-break: break-word;">{{ item.content }}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--text-secondary); font-size: 12px;">
                {{ new Date(item.created_at).toLocaleString('zh-CN') }}
              </span>
              <button v-if="item.status !== 'resolved'" style="background: var(--accent); color: white; border: none; padding: 6px 16px; border-radius: 16px; font-size: 12px; cursor: pointer;" @click="markFeedbackResolved(item.id)">
                标记已处理
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-primary" @click="showFeedbackListModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 时段信息弹窗 -->
    <div v-if="showSlotInfoModal" class="modal-overlay" @click="showSlotInfoModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>时段信息</h3>
          <button class="modal-close" @click="showSlotInfoModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-card">
            <div class="info-item">
              <span class="info-label">时段</span>
              <span class="info-value">{{ currentSlot }}:00 - {{ currentSlot + 1 }}:00</span>
            </div>
            <div v-if="slotInfoRemark" class="info-item">
              <span class="info-label">备注</span>
              <span class="info-value">{{ slotInfoRemark }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">想踢</span>
              <div v-if="isAdminLoggedIn" style="display: flex; align-items: center; gap: 12px;">
                <input type="number" v-model.number="wantToPlayEditCount" min="0" style="width: 80px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px;" />
                <span style="color: var(--text-secondary);">人</span>
              </div>
              <div v-else style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px; font-weight: 600; color: var(--accent);">
                  {{ getWantToPlayCount(currentVenue, selectedDate, currentSlot) }}
                </span>
                <span style="color: var(--text-secondary);">人想踢</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showSlotInfoModal = false">关闭</button>
          <button v-if="isAdminLoggedIn" class="modal-btn modal-btn-primary" @click="saveWantToPlayCount">保存</button>
          <template v-else>
            <template v-if="initialWantToPlayStatus">
              <button class="modal-btn modal-btn-danger" 
                      @click="decrementWantToPlay"
                      :disabled="wantToPlayButtonState !== 'idle'">
                <span v-if="wantToPlayButtonState === 'idle'">取消想踢</span>
                <span v-else-if="wantToPlayButtonState === 'loading'">提交中...</span>
                <span v-else-if="wantToPlayButtonState === 'success'">✓ 已取消</span>
              </button>
            </template>
            <template v-else>
              <button class="modal-btn modal-btn-primary" 
                      @click="incrementWantToPlay"
                      :disabled="wantToPlayButtonState !== 'idle'">
                <span v-if="wantToPlayButtonState === 'idle'">想踢+1</span>
                <span v-else-if="wantToPlayButtonState === 'loading'">提交中...</span>
                <span v-else-if="wantToPlayButtonState === 'success'">✓ 已记录</span>
              </button>
            </template>
          </template>
        </div>
      </div>
    </div>

    <!-- 管理员时段管理弹窗 -->
    <div v-if="showAdminSlotModal" class="modal-overlay" @click="showAdminSlotModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>时段管理</h3>
          <button class="modal-close" @click="showAdminSlotModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-card">
            <div class="info-item">
              <span class="info-label">时段</span>
              <span class="info-value">{{ currentSlot }}:00 - {{ currentSlot + 1 }}:00</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <div style="display: flex; gap: 10px;">
                <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                  <input type="radio" v-model="adminSlotStatus" value="available" />
                  <span>可预约</span>
                </label>
                <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                  <input type="radio" v-model="adminSlotStatus" value="booked" />
                  <span>已预约</span>
                </label>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">备注</span>
              <textarea v-model="adminSlotRemark" class="modal-textarea" placeholder="添加备注..." style="margin-top: 8px;"></textarea>
            </div>
            <div class="info-item">
              <span class="info-label">想踢人数</span>
              <div style="display: flex; align-items: center; gap: 12px;">
                <input type="number" v-model.number="wantToPlayEditCount" min="0" style="width: 100px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px;" />
                <span style="color: var(--text-secondary);">人</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-secondary" @click="showAdminSlotModal = false">取消</button>
          <button class="modal-btn modal-btn-primary" @click="saveAdminSlotChanges">保存</button>
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
const themeMode = ref('light') // 'light' | 'dark' | 'system'

// 系统主题监听
let mediaQuery = null

// 设置相关
const showProjectInfo = ref(false)
const showDeveloperInfo = ref(false)
const showLiabilityModal = ref(false)
const showFeedbackModal = ref(false)
const showSuggestionModal = ref(false)
const showHelpModal = ref(false)
const showFeedbackListModal = ref(false)

// 管理员登录相关
const isAdminLoggedIn = ref(false)
const showAdminLoginModal = ref(false)
const adminEmail = ref('')
const adminPassword = ref('')

// 想踢功能相关
const showSlotInfoModal = ref(false)
const showAdminSlotModal = ref(false)
const currentSlot = ref(null)
const wantToPlayButtonState = ref('idle') // 'idle' | 'loading' | 'success'
const initialWantToPlayStatus = ref(null) // 记录打开弹窗时的用户状态
const currentUser = ref(null) // 当前登录用户
// wantToPlayCache: { "venue_date": { "timeSlot": count } }
const wantToPlayCache = ref({})
const wantToPlayEditCount = ref(0)
const adminSlotRemark = ref('')
const adminSlotStatus = ref('')
const slotInfoStatus = ref('')
const slotInfoRemark = ref('')

// 获取当前日期的想踢数据（从缓存中）
const wantToPlayData = computed(() => {
  const cacheKey = `${currentVenue.value}_${selectedDate.value}`
  return wantToPlayCache.value[cacheKey] || {}
})

// 缓存当前日期的想踢数据，加速访问
const currentWantToPlay = computed(() => {
  const result = {}
  timeSlots.forEach(hour => {
    const key = getWantToPlayKey(currentVenue.value, selectedDate.value, hour)
    result[hour] = wantToPlayData.value[key] || 0
  })
  return result
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

// 切换页面
function switchPage(page) {
  currentPage.value = page
}

// 设置主题模式
function setThemeMode(mode) {
  themeMode.value = mode
  localStorage.setItem('themeMode', mode)
  applyTheme()
}

// 应用主题
function applyTheme() {
  if (themeMode.value === 'system') {
    if (mediaQuery && mediaQuery.matches) {
      currentTheme.value = 'theme-dark'
    } else {
      currentTheme.value = 'theme-light'
    }
  } else if (themeMode.value === 'dark') {
    currentTheme.value = 'theme-dark'
  } else {
    currentTheme.value = 'theme-light'
  }
}

// 系统主题变化监听
function handleSystemThemeChange(e) {
  if (themeMode.value === 'system') {
    applyTheme()
  }
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

// 清除想踢数据缓存
function clearWantToPlayCache() {
  // 清除所有想踢相关的缓存
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key && (key.startsWith('wantToPlay_') || key.startsWith('wantToPlayTime_'))) {
      localStorage.removeItem(key)
    }
  }
  // 重置数据
  wantToPlayData.value = {}
  alert('想踢数据缓存已清除！')
  // 重新加载数据
  fetchWantToPlayData(false)
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

// 反馈数据
const feedbackList = ref([])
const feedbackContent = ref('')

// 计算是否有未处理的反馈
const hasUnresolvedFeedback = computed(() => {
  return feedbackList.value.some(item => item.status !== 'resolved')
})

// 提交反馈
async function submitFeedback() {
  if (!feedbackContent.value.trim()) {
    alert('请输入反馈内容')
    return
  }

  try {
    const { error } = await supabase
      .from('feedback')
      .insert({
        type: 'feedback',
        content: feedbackContent.value.trim()
      })

    if (error) throw error

    alert('感谢您的反馈！我们会尽快处理。')
    showFeedbackModal.value = false
    feedbackContent.value = ''
  } catch (error) {
    console.error('提交反馈失败:', error)
    alert('提交失败，请重试')
  }
}

// 提交建议
async function submitSuggestion() {
  if (!feedbackContent.value.trim()) {
    alert('请输入建议内容')
    return
  }

  try {
    const { error } = await supabase
      .from('feedback')
      .insert({
        type: 'suggestion',
        content: feedbackContent.value.trim()
      })

    if (error) throw error

    alert('感谢您的建议！我们会认真考虑。')
    showSuggestionModal.value = false
    feedbackContent.value = ''
  } catch (error) {
    console.error('提交建议失败:', error)
    alert('提交失败，请重试')
  }
}

// 获取反馈列表（仅管理员）
async function fetchFeedbackList() {
  if (!isAdminLoggedIn.value) return

  try {
    const { data, error } = await supabase
      .from('feedback')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    feedbackList.value = data || []
  } catch (error) {
    console.error('获取反馈失败:', error)
  }
}

// 标记反馈为已处理
async function markFeedbackResolved(id) {
  try {
    const { error } = await supabase
      .from('feedback')
      .update({ status: 'resolved' })
      .eq('id', id)

    if (error) throw error
    fetchFeedbackList()
  } catch (error) {
    console.error('更新失败:', error)
  }
}

// 管理员登录
async function handleAdminLogin() {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: adminEmail.value,
      password: adminPassword.value
    })

    if (error) throw error

    isAdminLoggedIn.value = true
    localStorage.setItem('isAdminLoggedIn', 'true')
    showAdminLoginModal.value = false
    adminEmail.value = ''
    adminPassword.value = ''
    // 登录成功后获取反馈列表
    await fetchFeedbackList()
    alert('登录成功！')
  } catch (error) {
    console.error('登录失败:', error)
    alert('登录失败，请检查邮箱和密码')
  }
}

// 管理员退出
async function handleAdminLogout() {
  try {
    await supabase.auth.signOut()
    isAdminLoggedIn.value = false
    localStorage.removeItem('isAdminLoggedIn')
    alert('已退出登录')
  } catch (error) {
    console.error('退出失败:', error)
  }
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

// 选择日期
function selectDate(date) {
  selectedDate.value = date
  fetchWantToPlayData()
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
onMounted(async () => {
  // 设置加载页随机背景
  const randomIndex = Math.floor(Math.random() * bgImages.length)
  loadingBgImage.value = bgImages[randomIndex]
  
  // 从localStorage读取主题模式设置
  const savedThemeMode = localStorage.getItem('themeMode')
  if (savedThemeMode) {
    themeMode.value = savedThemeMode
  }
  
  // 检查管理员登录状态
  const { data: { session } } = await supabase.auth.getSession()
  isAdminLoggedIn.value = !!session
  if (session) {
    localStorage.setItem('isAdminLoggedIn', 'true')
    // 如果已登录，获取反馈列表
    await fetchFeedbackList()
  }
  
  // 监听登录状态变化
  supabase.auth.onAuthStateChange((_event, session) => {
    isAdminLoggedIn.value = !!session
    if (session) {
      localStorage.setItem('isAdminLoggedIn', 'true')
    } else {
      localStorage.removeItem('isAdminLoggedIn')
    }
  })
  
  // 初始化系统主题监听
  if (typeof window !== 'undefined' && window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', handleSystemThemeChange)
  }
  
  // 监听键盘事件（ESC 键）
  window.addEventListener('keydown', handleKeyDown)
  
  // 监听移动端返回键（popstate）
  window.addEventListener('popstate', handlePopState)
  
  // 添加一个初始的历史记录，用于拦截返回键
  history.pushState(null, '', window.location.href)
  
  // 应用主题
  applyTheme()

  const today = new Date()
  const month = today.getMonth() + 1
  const day = today.getDate()
  selectedDate.value = `${today.getFullYear()}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`

  // 先显示页面，天气数据在后台异步加载
  // 这样不会阻塞用户看到预约信息
  Promise.all([
    fetchBookings(),
    fetchVenueSlots(),
    subscribeToBookings(),
    preloadWantToPlayData()  // ← 预加载未来8天所有想踢数据
  ]).then(() => {
    isLoading.value = false
  })

  // 天气数据在后台加载，不阻塞页面显示
  fetchWeatherData()
})

// 检查是否有任何弹窗打开
function hasAnyModalOpen() {
  return showConfirmModal.value ||
         showRemarkModal.value ||
         showFeedbackModal.value ||
         showSuggestionModal.value ||
         showProjectInfo.value ||
         showDeveloperInfo.value ||
         showLiabilityModal.value ||
         showHelpModal.value ||
         showAdminLoginModal.value ||
         showFeedbackListModal.value ||
         showSlotInfoModal.value ||
         showAdminSlotModal.value
}

// 关闭所有弹窗
function closeAllModals() {
  showConfirmModal.value = false
  showRemarkModal.value = false
  showFeedbackModal.value = false
  showSuggestionModal.value = false
  showProjectInfo.value = false
  showDeveloperInfo.value = false
  showLiabilityModal.value = false
  showHelpModal.value = false
  showAdminLoginModal.value = false
  showFeedbackListModal.value = false
  showSlotInfoModal.value = false
  showAdminSlotModal.value = false
}

// 处理键盘事件（ESC 键）
function handleKeyDown(event) {
  if ((event.key === 'Escape' || event.keyCode === 27) && hasAnyModalOpen()) {
    event.preventDefault()
    event.stopPropagation()
    closeAllModals()
  }
}

// 处理移动端返回键（popstate）
function handlePopState(event) {
  if (hasAnyModalOpen()) {
    event.preventDefault()
    closeAllModals()
    // 重新 push state 回来，防止真正的页面后退
    history.pushState(null, '', window.location.href)
  }
}

onUnmounted(() => {
  // 清理系统主题监听
  if (mediaQuery) {
    mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }
  // 清理键盘事件监听
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('popstate', handlePopState)
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

// 获取周几的单个字符
function getWeekDayChar(weekStr) {
  const map = {
    '周日': '日',
    '周一': '一',
    '周二': '二',
    '周三': '三',
    '周四': '四',
    '周五': '五',
    '周六': '六'
  }
  return map[weekStr] || weekStr.charAt(weekStr.length - 1)
}

// 获取想踢数据的 key
function getWantToPlayKey(venue, date, timeSlot) {
  return `${venue}-${date}-${timeSlot}`
}

// 获取某个时段的想踢数量
function getWantToPlayCount(venue, date, timeSlot) {
  const key = getWantToPlayKey(venue, date, timeSlot)
  return wantToPlayData.value[key] || 0
}

// 获取或生成设备ID（用于用户去重）
function getDeviceId() {
  let deviceId = localStorage.getItem('deviceId')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('deviceId', deviceId)
  }
  return deviceId
}

// 检查用户是否已经想踢过某个时段
function hasUserWantToPlay(venue, date, timeSlot) {
  const deviceId = getDeviceId()
  const key = `wantToPlay_${venue}_${date}_${timeSlot}_${deviceId}`
  return localStorage.getItem(key) === 'true'
}

// 标记用户已想踢某个时段
function markUserWantToPlay(venue, date, timeSlot) {
  const deviceId = getDeviceId()
  const key = `wantToPlay_${venue}_${date}_${timeSlot}_${deviceId}`
  localStorage.setItem(key, 'true')
}

// 取消用户想踢标记
function unmarkUserWantToPlay(venue, date, timeSlot) {
  const deviceId = getDeviceId()
  const key = `wantToPlay_${venue}_${date}_${timeSlot}_${deviceId}`
  localStorage.removeItem(key)
}

// 公共函数：更新想踢数量（更新缓存和数据库）
async function updateWantToPlayCount(venue, date, timeSlot, count) {
  const key = getWantToPlayKey(venue, date, timeSlot)
  const cacheKey = `${venue}_${date}`
  const localStorageCacheKey = `wantToPlay_${venue}_${date}`

  // 更新内存缓存
  if (!wantToPlayCache.value[cacheKey]) {
    wantToPlayCache.value[cacheKey] = {}
  }
  wantToPlayCache.value[cacheKey][key] = count

  // 更新本地缓存
  localStorage.setItem(localStorageCacheKey, JSON.stringify(wantToPlayCache.value[cacheKey]))
  localStorage.setItem(`wantToPlayTime_${venue}_${date}`, Date.now().toString())

  // 更新数据库
  const { error } = await supabase
    .from('want_to_play')
    .upsert({
      venue,
      date,
      time_slot: timeSlot,
      count,
      updated_at: new Date().toISOString()
    }, { onConflict: 'venue,date,time_slot' })

  if (error) throw error
}

// 加载想踢数据（带本地缓存优化）- 可指定日期
async function fetchWantToPlayData(date = null, useCacheFirst = true) {
  const targetDate = date || selectedDate.value
  const cacheKey = `${currentVenue.value}_${targetDate}`
  const localStorageCacheKey = `wantToPlay_${currentVenue.value}_${targetDate}`
  const localStorageCacheTimeKey = `wantToPlayTime_${currentVenue.value}_${targetDate}`
  
  // 先尝试使用内存缓存
  if (wantToPlayCache.value[cacheKey]) {
    // 内存中有数据，直接使用，后台异步更新
    if (!date) { // 只有在加载当前日期时才后台更新
      updateWantToPlayCacheInBackground(targetDate)
    }
    return
  }
  
  // 再尝试使用本地缓存
  if (useCacheFirst) {
    const cachedData = localStorage.getItem(localStorageCacheKey)
    const cachedTime = localStorage.getItem(localStorageCacheTimeKey)
    const now = Date.now()
    
    if (cachedData && cachedTime && (now - parseInt(cachedTime)) < 5 * 60 * 1000) {
      // 5分钟内的本地缓存，先放到内存缓存，然后后台更新
      wantToPlayCache.value[cacheKey] = JSON.parse(cachedData)
      // 后台异步更新（仅当前日期）
      if (!date) {
        updateWantToPlayCacheInBackground(targetDate)
      }
      return
    }
  }
  
  // 缓存过期或没有缓存，从网络加载
  try {
    const { data, error } = await supabase
      .from('want_to_play')
      .select('*')
      .eq('venue', currentVenue.value)
      .eq('date', targetDate)

    if (error) throw error

    const newData = {}
    data.forEach(item => {
      const key = getWantToPlayKey(item.venue, item.date, item.time_slot)
      newData[key] = item.count
    })
    
    // 保存到内存缓存
    wantToPlayCache.value[cacheKey] = newData
    
    // 保存到本地缓存
    localStorage.setItem(localStorageCacheKey, JSON.stringify(newData))
    localStorage.setItem(localStorageCacheTimeKey, Date.now().toString())
  } catch (error) {
    console.error('获取想踢数据失败:', error)
    // 如果网络失败，尝试使用旧缓存
    const cachedData = localStorage.getItem(localStorageCacheKey)
    if (cachedData) {
      wantToPlayCache.value[cacheKey] = JSON.parse(cachedData)
    }
  }
}

// 预加载未来8天的所有想踢数据
async function preloadWantToPlayData() {
  const today = new Date()
  const preloadPromises = []
  
  for (let i = 0; i < 8; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    
    // 预加载，不使用缓存优先，直接从网络加载最新数据
    preloadPromises.push(fetchWantToPlayData(dateStr, false))
  }
  
  // 并行预加载所有日期
  await Promise.all(preloadPromises)
  console.log('未来8天想踢数据预加载完成')
}

// 后台更新想踢数据缓存 - 可指定日期
async function updateWantToPlayCacheInBackground(date = null) {
  const targetDate = date || selectedDate.value
  try {
    const { data, error } = await supabase
      .from('want_to_play')
      .select('*')
      .eq('venue', currentVenue.value)
      .eq('date', targetDate)

    if (error) throw error

    const newData = {}
    data.forEach(item => {
      const key = getWantToPlayKey(item.venue, item.date, item.time_slot)
      newData[key] = item.count
    })
    
    // 更新内存缓存
    const cacheKey = `${currentVenue.value}_${targetDate}`
    wantToPlayCache.value[cacheKey] = newData
    
    // 更新本地缓存
    localStorage.setItem(`wantToPlay_${currentVenue.value}_${targetDate}`, JSON.stringify(newData))
    localStorage.setItem(`wantToPlayTime_${currentVenue.value}_${targetDate}`, Date.now().toString())
  } catch (error) {
    console.error('后台更新想踢数据失败:', error)
  }
}

// 想踢+1
async function incrementWantToPlay() {
  if (!currentSlot.value) return

  const venue = currentVenue.value
  const date = selectedDate.value
  const timeSlot = currentSlot.value
  const cacheKey = `${venue}_${date}`

  // 检查用户是否已经想踢过
  if (hasUserWantToPlay(venue, date, timeSlot)) {
    alert('您已经表达过想踢的意愿啦！')
    return
  }

  const key = getWantToPlayKey(venue, date, timeSlot)
  const currentCount = wantToPlayCache.value[cacheKey]?.[key] || 0
  const newCount = currentCount + 1

  // 设置为加载状态
  wantToPlayButtonState.value = 'loading'

  try {
    // 使用公共函数更新想踢数量
    await updateWantToPlayCount(venue, date, timeSlot, newCount)

    // 标记用户已想踢
    markUserWantToPlay(venue, date, timeSlot)

    // 显示成功状态片刻
    wantToPlayButtonState.value = 'success'
    setTimeout(() => {
      // 成功状态显示完后，再切换按钮状态
      initialWantToPlayStatus.value = true
      wantToPlayButtonState.value = 'idle'
    }, 1000)

  } catch (error) {
    console.error('想踢+1失败:', error)
    
    // 回滚本地缓存
    if (wantToPlayCache.value[cacheKey]) {
      wantToPlayCache.value[cacheKey][key] = currentCount
    }
    
    // 重置按钮状态
    wantToPlayButtonState.value = 'idle'
    alert('操作失败，请重试')
  }
}

// 取消想踢
async function decrementWantToPlay() {
  if (!currentSlot.value) return

  const venue = currentVenue.value
  const date = selectedDate.value
  const timeSlot = currentSlot.value
  const cacheKey = `${venue}_${date}`

  // 检查用户是否已经想踢过（不应该出现，但双重检查）
  if (!hasUserWantToPlay(venue, date, timeSlot)) {
    alert('您还没有表达过想踢的意愿！')
    return
  }

  const key = getWantToPlayKey(venue, date, timeSlot)
  const currentCount = wantToPlayCache.value[cacheKey]?.[key] || 0
  const newCount = Math.max(0, currentCount - 1)

  // 设置为加载状态
  wantToPlayButtonState.value = 'loading'

  try {
    // 使用公共函数更新想踢数量
    await updateWantToPlayCount(venue, date, timeSlot, newCount)

    // 取消用户想踢标记
    unmarkUserWantToPlay(venue, date, timeSlot)

    // 显示成功状态片刻
    wantToPlayButtonState.value = 'success'
    setTimeout(() => {
      // 成功状态显示完后，再切换按钮状态
      initialWantToPlayStatus.value = false
      wantToPlayButtonState.value = 'idle'
    }, 1000)

  } catch (error) {
    console.error('取消想踢失败:', error)
    
    // 回滚本地缓存
    if (wantToPlayCache.value[cacheKey]) {
      wantToPlayCache.value[cacheKey][key] = currentCount
    }
    
    // 重置按钮状态
    wantToPlayButtonState.value = 'idle'
    alert('操作失败，请重试')
  }
}

// 管理员保存想踢数量
async function saveWantToPlayCount() {
  if (!currentSlot.value) return

  const venue = currentVenue.value
  const date = selectedDate.value
  const timeSlot = currentSlot.value
  const cacheKey = `${venue}_${date}`
  const key = getWantToPlayKey(venue, date, timeSlot)
  const currentCount = wantToPlayCache.value[cacheKey]?.[key] || 0

  try {
    // 使用公共函数更新想踢数量
    await updateWantToPlayCount(venue, date, timeSlot, wantToPlayEditCount.value)

    // 关闭弹窗
    showSlotInfoModal.value = false
  } catch (error) {
    console.error('保存想踢数量失败:', error)
    
    // 回滚本地缓存
    if (wantToPlayCache.value[cacheKey]) {
      wantToPlayCache.value[cacheKey][key] = currentCount
    }
    
    alert('保存失败，请重试')
  }
}

// 处理时段点击
function handleSlotClick(hour) {
  // 先设置当前时段
  currentSlot.value = hour
  
  // 重置按钮状态
  wantToPlayButtonState.value = 'idle'
  
  // 记录打开弹窗时的用户想踢状态（保持按钮颜色一致）
  initialWantToPlayStatus.value = hasUserWantToPlay(currentVenue.value, selectedDate.value, hour)
  
  // 获取想踢数量用于编辑
  wantToPlayEditCount.value = getWantToPlayCount(currentVenue.value, selectedDate.value, hour)
  
  if (isAdminLoggedIn.value) {
    // 管理员：打开整合的管理弹窗
    adminSlotStatus.value = isBooked(hour) ? 'booked' : 'available'
    adminSlotRemark.value = getRemark(hour) || ''
    showAdminSlotModal.value = true
  } else {
    // 普通用户：显示时段信息，先保存状态
    slotInfoStatus.value = isBooked(hour) ? '已预约' : (isExpired(hour) ? '已过期' : '可预约')
    slotInfoRemark.value = getRemark(hour) || ''
    showSlotInfoModal.value = true
  }
}

// 保存管理员时段修改
async function saveAdminSlotChanges() {
  if (!currentSlot.value) return

  try {
    // 1. 处理预约状态
    const isCurrentlyBooked = isBooked(currentSlot.value)
    const newStatusBooked = adminSlotStatus.value === 'booked'
    
    if (newStatusBooked !== isCurrentlyBooked) {
      await toggleBooking(currentSlot.value)
    }

    // 2. 处理备注
    const currentRemark = getRemark(currentSlot.value) || ''
    if (adminSlotRemark.value !== currentRemark) {
      // 先找到该时段的 booking 记录
      const venueBookings = getBookingsForVenueAndDate(currentVenue.value, selectedDate.value)
      const existingBooking = venueBookings.find(b => b.time_slot === currentSlot.value)

      if (existingBooking && adminSlotRemark.value) {
        // 更新备注
        const { error } = await supabase
          .from('bookings')
          .update({ remark: adminSlotRemark.value })
          .eq('id', existingBooking.id)
        
        if (error) throw error
      } else if (existingBooking && !adminSlotRemark.value) {
        // 删除备注（设为空）
        const { error } = await supabase
          .from('bookings')
          .update({ remark: null })
          .eq('id', existingBooking.id)
        
        if (error) throw error
      } else if (!existingBooking && adminSlotRemark.value) {
        // 如果没有 booking 记录但有备注，需要先创建 booking
        const { error } = await supabase
          .from('bookings')
          .insert({
            venue: currentVenue.value,
            date: selectedDate.value,
            time_slot: currentSlot.value,
            status: newStatusBooked ? 'booked' : 'available',
            remark: adminSlotRemark.value
          })
        
        if (error) throw error
      }
      
      // 重新获取 bookings 数据
      await fetchBookings()
    }

    // 3. 处理想踢数量
    const venue = currentVenue.value
    const date = selectedDate.value
    const timeSlot = currentSlot.value
    const cacheKey = `${venue}_${date}`
    const key = getWantToPlayKey(venue, date, timeSlot)
    const currentCount = wantToPlayCache.value[cacheKey]?.[key] || 0
    
    if (wantToPlayEditCount.value !== currentCount) {
      // 使用公共函数更新想踢数量
      await updateWantToPlayCount(venue, date, timeSlot, wantToPlayEditCount.value)
    }

    // 关闭弹窗
    showAdminSlotModal.value = false
    alert('保存成功！')
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败，请重试')
  }
}

// 确认切换预约状态
function confirmToggle() {
  if (confirmHour.value !== null) {
    toggleBooking(confirmHour.value)
  }
  showConfirmModal.value = false
  confirmHour.value = null
}

// 长按处理
let pressTimer = null

function startPress(hour) {
  if (!isAdminLoggedIn.value) {
    return
  }
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

  // 订阅 want_to_play 表变化（想踢数据实时更新）
  supabase
    .channel('want_to_play')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'want_to_play'
    }, (payload) => {
      console.log('收到 want_to_play 实时更新:', payload)
      // 实时更新想踢数据
      fetchWantToPlayData(false)
    })
    .subscribe()

  // 订阅 feedback 表变化（反馈数据实时更新）
  supabase
    .channel('feedback')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'feedback'
    }, (payload) => {
      console.log('收到 feedback 实时更新:', payload)
      // 实时更新反馈列表
      if (isAdminLoggedIn.value) {
        fetchFeedbackList()
      }
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
  --icon-filter: brightness(0) saturate(100%) invert(17%) sepia(14%) saturate(1147%) hue-rotate(173deg) brightness(93%) contrast(87%);
  --icon-filter-active: brightness(0) saturate(100%) invert(27%) sepia(98%) saturate(1268%) hue-rotate(197deg) brightness(93%) contrast(85%);
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
  --icon-filter: brightness(0) saturate(100%) invert(82%) sepia(4%) saturate(2497%) hue-rotate(177deg) brightness(102%) contrast(86%);
  --icon-filter-active: brightness(0) saturate(100%) invert(47%) sepia(95%) saturate(2340%) hue-rotate(207deg) brightness(98%) contrast(91%);
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
  padding: 0;
}

.icon-share {
  width: 24px;
  height: 24px;
  filter: var(--icon-filter);
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

/* ============ 预约预览条 ============ */
.booking-preview-bar {
  margin-bottom: 24px;
}

.preview-bar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
  background: var(--bg-secondary);
  padding: 8px;
  border-radius: 12px;
}

.preview-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: var(--bg-card);
}

.preview-bar-item.has-booking {
  background: var(--success);
}

.preview-bar-day {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
  line-height: 1;
}

.preview-bar-item.has-booking .preview-bar-day {
  color: #fff;
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

.date-day {
  font-size: 22px;
  font-weight: bold;
}

.theme-dark .date-day {
  color: #e2e8f0;
}

.date-week {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 4px;
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

.want-to-play-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  background: #F98025;
  padding: 3px 8px;
  border-radius: 10px;
  white-space: nowrap;
  height: fit-content;
}

.want-to-play-icon {
  flex-shrink: 0;
}

.time-slot-right {
  display: flex;
  align-items: center;
  gap: 8px;
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

.time-slot.time-slot-locked:not(.expired) {
  cursor: not-allowed;
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

.theme-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 10px;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 14px;
  cursor: pointer;
  position: relative;
  gap: 8px;
}

.theme-option.active {
  border-color: var(--accent);
  background: var(--bg-card);
}

.theme-icon {
  width: 32px;
  height: 32px;
  color: var(--text-primary);
}

.theme-option.active .theme-icon {
  color: var(--accent);
}

.theme-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.theme-option.active .theme-label {
  color: var(--accent);
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

.settings-item.active {
  background: var(--bg-card);
}

.settings-check {
  font-size: 20px;
  color: var(--accent);
  font-weight: bold;
  flex-shrink: 0;
}

/* 反馈管理未处理状态样式 */
.settings-item.feedback-unresolved {
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid var(--danger);
  animation: pulse 2s infinite;
}

.settings-item.feedback-unresolved .settings-item-title {
  color: var(--danger);
  font-weight: 600;
}

.feedback-badge {
  background: var(--danger);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
  margin-right: 4px;
  animation: badge-pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

@keyframes badge-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
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
  width: 26px;
  height: 26px;
  margin-bottom: 4px;
  opacity: 0.5;
  filter: var(--icon-filter);
}

.tab-label {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.5;
  color: var(--text-secondary);
}

.tab-item.active .tab-icon,
.tab-item.active .tab-label {
  opacity: 1;
}

.tab-item.active .tab-label {
  color: var(--accent);
}

.tab-item.active .tab-icon {
  filter: var(--icon-filter-active);
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
  padding: 32px;
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

.modal-btn-danger {
  background: var(--danger);
  color: #fff;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  padding: 8px 8px 8px 8px;
  max-height: 75vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.help-section {
  margin-bottom: 28px;
  padding: 0 8px;
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

<!-- 815d891 - 触发 Vercel 自动部署 -->