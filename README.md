# Tide-Watcher · Watcher of Realms 日常挂机

> 个人自用存档，基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 把 Watcher of Realms 的日常活跃度任务自动化。
> 任务逻辑都写在 `assets` 里，欢迎直接 copy 改造。

## 它能做什么

自动完成与每日 / 每周活跃度相关的主要操作，包括但不限于：

- 🎮 登录游戏、自动回到主界面
- 🎁 领取商城免费礼包 / 签到奖励 / 邮件奖励
- ⛏️ 矿场领取 · 🛒 矮人超市购买 · 💪 友情点换体力
- ⛵ 航海 · 🚢 休伯利安 · 🌊 魔潮扫荡 · ⚔️ 刷体力
- 🐉 公会巨龙 · 🏛️ 公会奖励 · 🗿 泰坦废墟
- 📋 任务奖励领取 · ⚡ 装备升级 · 🔮 英灵召唤
- 🎟️ 通行证奖励 · ⏰ 在线奖励 · 🔄 每周交易所

每个任务的触发条件和说明见 `assets/interface.json` 与各任务节点。

## 使用前的游戏设置

- 模拟器分辨率建议 **720 × 1080**
- 开启 **自动战斗 → 后台战斗**
- 矮人商城：**金币购买不提示**
- 背包 → 装备 → 排序方式 → 按 **装备等级 · 升序** 排列

## 新设备需要准备的东西

- 安装 **Python 3** 并加入系统 PATH
- 运行 `DependencySetup_依赖库安装_win.bat` 安装 VC++ 运行库与 .NET 10
- 安装依赖：`pip install psutil pyautogui pygetwindow opencv-python pillow`
- 手动把 `moontonlauncher.lnk` 放到 `assets/resource/agent/` 目录下

## 说明

- 项目名沿用 Tide-Watcher，定位就是完成日常活跃度任务。
- 自用稳定，暂未发现明显 bug，近期不打算大改。
