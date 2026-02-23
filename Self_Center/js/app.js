/**
 * Self_Center 主逻辑：个人页 + 设置页
 */
(function (global) {
  var C = global.SelfCenter && global.SelfCenter.config;
  var B = global.SelfCenter && global.SelfCenter.bridge;
  var R = global.SelfCenter && global.SelfCenter.router;

  if (!C || !B || !R) return;

  var root = document.getElementById('self-center-root');
  if (!root) return;

  function t(key) {
    var s = (C.strings || {})[key];
    return s != null ? s : key;
  }

  function renderProfile() {
    var user = C.user || {};
    var deviceCount = 0;
    B.getDevices(function (list) {
      deviceCount = Array.isArray(list) ? list.length : 0;
      updateDeviceCount(deviceCount);
    });

    function updateDeviceCount(n) {
      var el = document.getElementById('sc-device-count');
      if (el) el.textContent = n;
    }

    root.innerHTML =
      '<div class="sc-page">' +
        '<div class="sc-card" style="text-align:center; padding:24px 16px;">' +
          '<img class="sc-avatar" id="sc-avatar" src="' + (user.avatar || '') + '" alt="" onerror="this.style.display=\'none\'">' +
          '<div style="margin-top:12px; font-size:18px; font-weight:600;">' + (user.nickname || user.account || '用户') + '</div>' +
          '<div class="sc-meta">' + (user.account || user.phone || user.email || '未绑定账号') + '</div>' +
        '</div>' +
        '<div class="sc-card">' +
          '<a class="sc-list-item" href="#/settings/account" style="border-bottom:1px solid var(--sc-border);">' +
            '<span class="label">' + t('accountSecurity') + '</span><span class="arrow">›</span>' +
          '</a>' +
          (C.features.showMessageCenter !== false
            ? '<a class="sc-list-item" href="javascript:void(0)" id="sc-msg-center">' +
                '<span class="label">' + t('messageCenter') + '</span><span class="arrow">›</span>' +
              '</a>'
            : '') +
          (C.features.showDeviceManage !== false
            ? '<a class="sc-list-item" href="#/settings/devices">' +
                '<span class="label">' + t('myDevices') + '</span><span class="value" id="sc-device-count">' + deviceCount + '</span><span class="arrow">›</span>' +
              '</a>'
            : '') +
        '</div>' +
        '<div class="sc-card">' +
          '<a class="sc-list-item" href="#/settings">' +
            '<span class="label">' + t('settings') + '</span><span class="arrow">›</span>' +
          '</a>' +
        '</div>' +
      '</div>';

    var avatar = document.getElementById('sc-avatar');
    if (avatar && !user.avatar) avatar.style.display = 'none';

    var msgEl = document.getElementById('sc-msg-center');
    if (msgEl) msgEl.addEventListener('click', function () { B.openMessageCenter(); });
  }

  function renderSettings() {
    root.innerHTML =
      '<div class="sc-page">' +
        '<div class="sc-header">' +
          '<a class="sc-back" href="#/profile">‹ 返回</a>' +
          '<span class="sc-title">' + t('settings') + '</span>' +
          '<span style="width:60px;"></span>' +
        '</div>' +
        '<div class="sc-card">' +
          '<ul class="sc-list">' +
            '<a class="sc-list-item" href="#/settings/account"><span class="label">' + t('accountSecurity') + '</span><span class="arrow">›</span></a>' +
            '<a class="sc-list-item" href="#/settings/notification"><span class="label">' + t('notification') + '</span><span class="arrow">›</span></a>' +
            '<a class="sc-list-item" href="#/settings/privacy"><span class="label">' + t('privacy') + '</span><span class="arrow">›</span></a>' +
            (C.features.showDeviceManage !== false ? '<a class="sc-list-item" href="#/settings/devices"><span class="label">' + t('deviceManage') + '</span><span class="arrow">›</span></a>' : '') +
            (C.features.showFirmware !== false ? '<a class="sc-list-item" href="#/settings/firmware"><span class="label">' + t('firmware') + '</span><span class="arrow">›</span></a>' : '') +
            '<a class="sc-list-item" href="#/settings/general"><span class="label">' + t('general') + '</span><span class="arrow">›</span></a>' +
            '<a class="sc-list-item" href="#/settings/about"><span class="label">' + t('about') + '</span><span class="arrow">›</span></a>' +
          '</ul>' +
        '</div>' +
        (C.features.showLogout !== false
          ? '<div class="sc-card"><button class="sc-btn-primary" id="sc-logout">退出登录</button></div>'
          : '') +
      '</div>';

    var logoutBtn = document.getElementById('sc-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', function () { B.logout(); });
  }

  function renderSubSettings(sub, param) {
    var back = '<div class="sc-header"><a class="sc-back" href="#/settings">‹ 返回</a><span class="sc-title">' + t(sub) + '</span><span></span></div>';
    var content = '';

    if (sub === 'account') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">修改密码</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">手机号</span><span class="value">' + (C.user.phone || '未绑定') + '</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">邮箱</span><span class="value">' + (C.user.email || '未绑定') + '</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">第三方账号</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else if (sub === 'notification') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">推送通知</span><span class="value">已开启</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">勿扰时段</span><span class="value">22:00 - 08:00</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">设备告警</span><span class="value">已开启</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else if (sub === 'privacy') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">隐私政策</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">数据与权限说明</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else if (sub === 'devices') {
      content = '<div class="sc-card"><ul class="sc-list" id="sc-device-list"></ul></div>' +
        '<div class="sc-card"><a class="sc-list-item" href="javascript:void(0)" id="sc-add-device"><span class="label">添加设备</span><span class="arrow">›</span></a></div>';
      root.innerHTML = '<div class="sc-page">' + back + content + '</div>';
      B.getDevices(function (list) {
        var ul = document.getElementById('sc-device-list');
        if (!ul) return;
        if (!list || list.length === 0) {
          ul.innerHTML = '<li class="sc-list-item" style="color:var(--sc-text-secondary);">暂无设备</li>';
          return;
        }
        ul.innerHTML = list.map(function (d) {
          return '<li class="sc-list-item" data-id="' + (d.id || d.deviceId || '') + '">' +
            '<span class="label">' + (d.name || d.deviceName || '设备') + '</span><span class="arrow">›</span></li>';
        }).join('');
        ul.querySelectorAll('.sc-list-item[data-id]').forEach(function (li) {
          li.addEventListener('click', function () {
            B.openDevice(li.getAttribute('data-id'));
          });
        });
      });
      var addBtn = document.getElementById('sc-add-device');
      if (addBtn) addBtn.addEventListener('click', function () { B.navigate('addDevice', {}); });
      return;
    } else if (sub === 'firmware') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">检查更新</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">自动更新固件</span><span class="value">已开启</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else if (sub === 'general') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">语言</span><span class="value">简体中文</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">主题</span><span class="value">浅色</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">清除缓存</span><span class="value">0 MB</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else if (sub === 'about') {
      content = '<div class="sc-card">' +
        '<ul class="sc-list">' +
          '<li class="sc-list-item"><span class="label">当前版本</span><span class="value">1.0.0</span></li>' +
          '<li class="sc-list-item"><span class="label">用户协议</span><span class="arrow">›</span></li>' +
          '<li class="sc-list-item"><span class="label">注销账号</span><span class="arrow">›</span></li>' +
        '</ul></div>';
    } else {
      content = '<div class="sc-card"><p class="sc-meta">暂无更多设置</p></div>';
    }

    root.innerHTML = '<div class="sc-page">' + back + content + '</div>';
  }

  R.route('profile', function () {
    renderProfile();
  });

  R.route('settings', function (param) {
    if (param) renderSubSettings(param); else renderSettings();
  });

  R.init();
})(typeof window !== 'undefined' ? window : this);
