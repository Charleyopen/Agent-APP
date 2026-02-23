/**
 * Self_Center 模块配置
 * 宿主 APP 可通过 URL 参数、全局变量或 postMessage 注入配置
 */
(function (global) {
  function getQuery() {
    try {
      return Object.fromEntries(new URLSearchParams(location.search || ''));
    } catch (_) {
      return {};
    }
  }

  function parseConfig(str) {
    if (!str) return {};
    try {
      return JSON.parse(decodeURIComponent(str));
    } catch (_) {
      try {
        return JSON.parse(str);
      } catch (__) {
        return {};
      }
    }
  }

  var query = getQuery();
  var fromQuery = parseConfig(query.config || query.self_center_config || '{}');
  var fromGlobal = (global.__SELF_CENTER_CONFIG__ || {});
  var fromStorage = {};
  try {
    var stored = localStorage.getItem('self_center_config');
    if (stored) fromStorage = JSON.parse(stored);
  } catch (_) {}

  /**
   * 合并后的配置（优先级：query > global > storage > 默认）
   * 宿主可覆盖：user, theme, apiBase, strings, features
   */
  var defaultConfig = {
    user: {
      id: '',
      nickname: '用户',
      avatar: '',
      phone: '',
      email: '',
      account: ''
    },
    theme: {
      primary: '#1890ff',
      background: '#f5f5f5',
      dark: false
    },
    apiBase: '',
    strings: {
      title: '个人中心',
      settings: '设置',
      myDevices: '我的设备',
      messageCenter: '消息中心',
      accountSecurity: '账号与安全',
      notification: '消息通知',
      privacy: '隐私',
      deviceManage: '设备管理',
      firmware: '固件与更新',
      general: '通用',
      about: '关于'
    },
    features: {
      showMessageCenter: true,
      showDeviceManage: true,
      showFirmware: true,
      showLogout: true
    }
  };

  function deepMerge(target, source) {
    var out = {};
    for (var k in target) out[k] = target[k];
    for (var k in source) {
      if (source[k] != null && typeof source[k] === 'object' && !Array.isArray(source[k]) && typeof target[k] === 'object') {
        out[k] = deepMerge(target[k] || {}, source[k]);
      } else if (source[k] !== undefined) {
        out[k] = source[k];
      }
    }
    return out;
  }

  var config = deepMerge(deepMerge(deepMerge(defaultConfig, fromStorage), fromGlobal), fromQuery);

  /** 供宿主调用：更新配置（如登录后更新用户信息） */
  function updateConfig(patch) {
    config = deepMerge(config, patch);
    try {
      localStorage.setItem('self_center_config', JSON.stringify(config));
    } catch (_) {}
    if (global.__SELF_CENTER_ON_CONFIG__) global.__SELF_CENTER_ON_CONFIG__(config);
    return config;
  }

  global.SelfCenter = global.SelfCenter || {};
  global.SelfCenter.config = config;
  global.SelfCenter.updateConfig = updateConfig;
})(typeof window !== 'undefined' ? window : this);
