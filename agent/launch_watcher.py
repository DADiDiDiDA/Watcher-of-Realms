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
GAME_PROCESS_NAME = "Watcher of Realms.exe"  # 游戏进程名

def close_game_process():
    """强制关闭游戏进程"""
    try:
        # 使用 taskkill 强制结束游戏进程
        result = subprocess.run(
            ["taskkill", "/f", "/im", GAME_PROCESS_NAME],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ 已关闭游戏进程: {GAME_PROCESS_NAME}")
            time.sleep(2)  # 等待进程完全退出
            return True
        elif "没有找到" in result.stderr or "not found" in result.stderr.lower():
            print(f"ℹ️ 游戏进程未运行: {GAME_PROCESS_NAME}")
            return True
        else:
            print(f"⚠️ 关闭进程失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 关闭进程异常: {e}")
        return False

def wait_for_launcher_window(timeout=60):
    """等待启动器窗口出现"""
    print(f"⏳ 等待启动器窗口加载（超时 {timeout} 秒）...")
    start_time = time.time()
    last_progress = 0
    
    while time.time() - start_time < timeout:
        try:
            windows = gw.getWindowsWithTitle(WINDOW_TITLE_KEYWORD)
            if windows:
                win = windows[0]
                # 如果窗口存在，尝试激活它
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(1)
                print(f"✅ 已激活窗口: {win.title}")
                return True
        except Exception as e:
            print(f"⚠️ 检查窗口时出错: {e}")
        
        # 每5秒输出进度
        elapsed = int(time.time() - start_time)
        if elapsed - last_progress >= 5:
            print(f"⏳ 等待启动器... {elapsed}秒")
            last_progress = elapsed
        
        # 每1秒检查一次
        time.sleep(1)
    
    print(f"⚠️ 等待启动器窗口超时（{timeout} 秒）")
    return False

def activate_launcher_window():
    """激活启动器窗口（已由 wait_for_launcher_window 处理）"""
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
    # ---- 新增：先关闭游戏进程 ----
    print("🔍 检查并关闭游戏进程...")
    close_game_process()
    # ------------------------------
    
    print("🚀 启动沐瞳启动器...")
    print(f"📂 路径: {LAUNCHER_PATH}")
    subprocess.Popen([LAUNCHER_PATH])
    
    print("⏳ 等待启动器加载...")
    
    # 等待启动器窗口出现（最多等待60秒）
    if not wait_for_launcher_window(timeout=60):
        print("⚠️ 启动器窗口未出现，将尝试直接识别按钮...")
        # 额外等待几秒再尝试识别按钮
        time.sleep(3)
    else:
        # 窗口激活后，再等待1秒让界面稳定
        time.sleep(1)
    
    # 尝试点击按钮
    for attempt in range(1, 6):  # 增加到5次尝试
        print(f"🎯 第 {attempt} 次尝试点击开始按钮...")
        if find_and_click_button():
            print("🎮 游戏启动指令已发出！")
            print("🔄 脚本执行完毕，自动退出...")
            time.sleep(1)
            sys.exit(0)
        time.sleep(2)
    
    print("❌ 多次尝试后仍未点击成功")
    print("🔄 3秒后自动退出...")
    time.sleep(3)
    sys.exit(1)

if __name__ == "__main__":
    launch_game()