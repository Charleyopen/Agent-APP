/**
 * 与宿主 APP 的桥接协议
 * 宿主 APP 在 WebView 中实现以下接口，供本模块调用；本模块会 postMessage 通知宿主
 */
(function (global) {
  var bridge = {
    /** 获取用户信息（宿主可实现后由 WebView 注入） */
    getUser: function (cb) {
      if (global.__SELF_CENTER_GET_USER__ && typeof global.__SELF_CENTER_GET_USER__ === 'function') {
        return global.__SELF_CENTER_GET_USER__(cb);
      }
      cb && cb(global.SelfCenter && global.SelfCenter.config ? global.SelfCenter.config.user : null);
    },

    /** 获取设备列表（宿主实现） */
    getDevices: function (cb) {
      if (global.__SELF_CENTER_GET_DEVICES__ && typeof global.__SELF_CENTER_GET_DEVICES__ === 'function') {
        return global.__SELF_CENTER_GET_DEVICES__(cb);
      }
      cb && cb([]);
    },

    /** 跳转到 APP 内某页（宿主实现，如 scheme 或 native 路由） */
    navigate: function (path, params) {
      if (global.__SELF_CENTER_NAVIGATE__ && typeof global.__SELF_CENTER_NAVIGATE__ === 'function') {
        return global.__SELF_CENTER_NAVIGATE__(path, params);
      }
      post('navigate', { path: path, params: params || {} });
    },

    /** 通知宿主：退出登录 */
    logout: function () {
      post('logout', {});
      if (global.__SELF_CENTER_LOGOUT__ && typeof global.__SELF_CENTER_LOGOUT__ === 'function') {
        return global.__SELF_CENTER_LOGOUT__();
      }
    },

    /** 通知宿主：打开消息中心 */
    openMessageCenter: function () {
      post('openMessageCenter', {});
      if (global.__SELF_CENTER_OPEN_MESSAGE_CENTER__) global.__SELF_CENTER_OPEN_MESSAGE_CENTER__();
    },

    /** 通知宿主：打开设备详情或设备管理 */
    openDevice: function (deviceId) {
      post('openDevice', { deviceId: deviceId });
      if (global.__SELF_CENTER_OPEN_DEVICE__) global.__SELF_CENTER_OPEN_DEVICE__(deviceId);
    }
  };

  function post(type, payload) {
    try {
      if (global.ReactNativeWebView && global.ReactNativeWebView.postMessage) {
        global.ReactNativeWebView.postMessage(JSON.stringify({ type: type, payload: payload }));
      }
      if (global.webkit && global.webkit.messageHandlers && global.webkit.messageHandlers.selfCenter) {
        global.webkit.messageHandlers.selfCenter.postMessage({ type: type, payload: payload });
      }
      if (global.parent !== global && global.postMessage) {
        global.postMessage({ source: 'self_center', type: type, payload: payload }, '*');
      }
    } catch (_) {}
  }

  global.SelfCenter = global.SelfCenter || {};
  global.SelfCenter.bridge = bridge;
})(typeof window !== 'undefined' ? window : this);
