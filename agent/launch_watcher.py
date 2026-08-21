import pyautogui
import subprocess
import time
import os
import pygetwindow as gw
import sys

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 固定路径配置
LAUNCHER_PATH = r"D:\Game\Watcher of Realms\moontonlauncher.exe"
BUTTON_IMAGE = os.path.join(SCRIPT_DIR, "start_button.png")

CONFIDENCE = 0.8
WINDOW_TITLE_KEYWORD = "Watcher Of Realms"

def activate_launcher_window():
    try:
        windows = gw.getWindowsWithTitle(WINDOW_TITLE_KEYWORD)
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(1)
            print(f"✅ 已激活窗口: {win.title}")
            return True
        else:
            print(f"⚠️ 未找到标题包含 '{WINDOW_TITLE_KEYWORD}' 的窗口")
            return False
    except Exception as e:
        print(f"❌ 激活窗口失败: {e}")
        return False

def find_and_click_button():
    try:
        button_pos = pyautogui.locateCenterOnScreen(
            BUTTON_IMAGE,
            confidence=CONFIDENCE
        )
        if button_pos:
            pyautogui.click(button_pos)
            print(f"✅ 点击成功，位置: {button_pos}")
            return True
        else:
            print("⚠️ 未找到按钮")
            return False
    except Exception as e:
        print(f"❌ 识别失败: {e}")
        return False

def launch_game():
    print("🚀 启动沐瞳启动器...")
    print(f"📂 路径: {LAUNCHER_PATH}")
    subprocess.Popen([LAUNCHER_PATH])
    
    print("⏳ 等待启动器加载...")
    time.sleep(5)
    
    if not activate_launcher_window():
        print("⚠️ 未找到启动器窗口，将尝试直接识别...")
    
    for attempt in range(1, 4):
        print(f"🎯 第 {attempt} 次尝试点击开始按钮...")
        if find_and_click_button():
            print("🎮 游戏启动指令已发出！")
            # ---- 成功后自动退出 ----
            print("🔄 脚本执行完毕，自动退出...")
            time.sleep(1)
            sys.exit(0)  # 正常退出
            # -----------------------
        time.sleep(2)
    
    print("❌ 多次尝试后仍未点击成功")
    print("🔄 3秒后自动退出...")
    time.sleep(3)
    sys.exit(1)  # 失败退出

if __name__ == "__main__":
    launch_game()