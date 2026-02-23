# Self_Center — 物联网 APP 个人中心模块

可接入**任意手机 APP**，作为物联网设备的「个人」页面，包含**个人页展示**与**完整设置管理**，适用于 IoT 设备控制类应用。

---

## 功能概览

### 个人页
- 头像、昵称、账号（手机/邮箱）展示
- 我的设备数量
- 入口：账号与安全、消息中心、设备管理、设置

### 设置管理（物联网 APP 常用项）
| 分类 | 项 |
|------|----|
| **账号与安全** | 修改密码、手机/邮箱绑定、第三方账号 |
| **消息通知** | 推送开关、勿扰时段、设备告警 |
| **隐私** | 隐私政策、数据与权限说明 |
| **设备管理** | 已绑定设备列表、添加设备、进入设备详情 |
| **固件与更新** | 检查更新、自动更新固件 |
| **通用** | 语言、主题、清除缓存 |
| **关于** | 当前版本、用户协议、注销账号 |

此外提供**退出登录**入口（可配置关闭）。

---

## 接入方式

本模块为 **H5 页面**，宿主 APP 通过 **WebView** 加载即可，无需原生依赖。

### 1. 直接打开 URL

在 APP 内打开 WebView，加载模块入口页：

```
https://你的域名/self-center/index.html
```

或本地打包进 APP 的静态资源路径，例如：

```
file:///android_asset/self-center/index.html
```

### 2. 注入配置

通过 **URL 参数** 传入用户与主题等（需 encode）：

```
index.html?config={"user":{"nickname":"张三","avatar":"https://..."},"theme":{"primary":"#1890ff"}}
```

或由宿主在 WebView 内**先注入全局变量**，再加载页面：

```javascript
window.__SELF_CENTER_CONFIG__ = {
  user: { id: '1', nickname: '张三', avatar: '', phone: '138****0000', email: '', account: 'user@example.com' },
  theme: { primary: '#1890ff', dark: false },
  features: { showMessageCenter: true, showDeviceManage: true, showFirmware: true, showLogout: true }
};
// 然后加载 index.html
```

配置字段说明见 [config.schema.json](./config.schema.json)。

### 3. 与原生交互（桥接）

模块内会调用以下能力，需由宿主在 WebView 中实现，否则仅使用静态配置或默认行为：

| 能力 | 说明 | 宿主实现方式 |
|------|------|----------------|
| 用户信息 | 个人页展示 | 注入 `__SELF_CENTER_CONFIG__.user` 或实现 `__SELF_CENTER_GET_USER__(callback)` |
| 设备列表 | 设备数量、设备管理页列表 | 实现 `__SELF_CENTER_GET_DEVICES__(callback)`，callback(数组) |
| 跳转 | 添加设备等 APP 内页 | 实现 `__SELF_CENTER_NAVIGATE__(path, params)` 或监听 postMessage |
| 退出登录 | 用户点击退出 | 实现 `__SELF_CENTER_LOGOUT__()` 或监听 postMessage `type: 'logout'` |
| 消息中心 | 点击消息中心 | 实现 `__SELF_CENTER_OPEN_MESSAGE_CENTER__()` 或 postMessage |
| 设备详情 | 点击某设备 | 实现 `__SELF_CENTER_OPEN_DEVICE__(deviceId)` 或 postMessage |

**postMessage 格式**（供 Android/iOS/React Native 等使用）：

```json
{ "source": "self_center", "type": "logout" | "navigate" | "openMessageCenter" | "openDevice", "payload": { ... } }
```

React Native 示例：`ReactNativeWebView.postMessage` 会收到上述 JSON 字符串。  
iOS：可注入 `webkit.messageHandlers.selfCenter.postMessage` 接收相同结构。

---

## 项目结构

```
Self_Center/
├── index.html          # 入口页
├── config.schema.json  # 配置结构说明
├── Readme.md           # 本说明
├── css/
│   └── theme.css       # 主题与布局（可被宿主覆盖 CSS 变量）
└── js/
    ├── config.js       # 配置合并与 updateConfig
    ├── bridge.js       # 与宿主桥接
    ├── router.js       # hash 路由
    └── app.js          # 个人页与设置页渲染
```

### 路由（hash）

- `#/profile` — 个人页
- `#/settings` — 设置首页
- `#/settings/account` — 账号与安全
- `#/settings/notification` — 消息通知
- `#/settings/privacy` — 隐私
- `#/settings/devices` — 设备管理
- `#/settings/firmware` — 固件与更新
- `#/settings/general` — 通用
- `#/settings/about` — 关于

---

## 主题定制

在包裹容器或 `body` 上增加 class `self-center`，并覆盖 CSS 变量即可（见 `css/theme.css`）：

```css
.self-center {
  --sc-primary: #你的主色;
  --sc-bg: #背景色;
  --sc-card: #卡片背景;
}
```

深色模式可加 class `dark`：`<body class="self-center dark">`，或通过 `theme.dark` 在运行时切换。

---

## 更新配置

若登录后或切换账号后需要更新用户信息，可在 WebView 中执行：

```javascript
window.SelfCenter.updateConfig({ user: { nickname: '新昵称', avatar: '...' } });
```

---

## 能力开关

通过配置 `features` 隐藏不需要的入口：

```javascript
__SELF_CENTER_CONFIG__.features = {
  showMessageCenter: false,
  showDeviceManage: true,
  showFirmware: true,
  showLogout: true
};
```

---

## 许可与使用

本模块为前端静态资源，可按项目需要修改或二次封装，用于任意物联网/设备类 APP 的「个人」与「设置」能力。
