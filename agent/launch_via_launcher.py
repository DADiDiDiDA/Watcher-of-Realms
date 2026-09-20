# launch_via_launcher.py
import os
import sys
import time
import subprocess
import psutil
import pyautogui
import pygetwindow as gw

# ---------- 路径与配置 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LAUNCHER_PATH = r"D:\Game\Watcher of Realms\moontonlauncher.exe"
BUTTON_IMAGE = os.path.join(SCRIPT_DIR, "start_button.png")

CONFIDENCE = 0.8
WINDOW_TITLE_KEYWORD = "Watcher Of Realms"
GAME_PROCESS_NAME = "Watcher of Realms.exe"

# ---------- 关闭已有游戏进程 ----------
def close_game_process():
    try:
        result = subprocess.run(
            ["taskkill", "/f", "/im", GAME_PROCESS_NAME],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ 已关闭游戏进程: {GAME_PROCESS_NAME}")
            time.sleep(2)
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

# ---------- 等待启动器窗口 ----------
def wait_for_launcher_window(timeout=60):
    print(f"⏳ 等待启动器窗口加载（超时 {timeout} 秒）...")
    start_time = time.time()
    last_progress = 0

    while time.time() - start_time < timeout:
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
        except Exception as e:
            print(f"⚠️ 检查窗口时出错: {e}")

        elapsed = int(time.time() - start_time)
        if elapsed - last_progress >= 5:
            print(f"⏳ 等待启动器... {elapsed}秒")
            last_progress = elapsed
        time.sleep(1)

    print(f"⚠️ 等待启动器窗口超时（{timeout} 秒）")
    return False

# ---------- 强制激活启动器窗口 ----------
def activate_launcher_window():
    """在截图前把启动器窗口拉到最前，确保找图能看到它。"""
    try:
        windows = gw.getWindowsWithTitle(WINDOW_TITLE_KEYWORD)
        if not windows:
            print(f"⚠️ 未找到标题含 '{WINDOW_TITLE_KEYWORD}' 的窗口")
            return False

        win = windows[0]
        if win.isMinimized:
            win.restore()
            time.sleep(0.3)

        # 多次尝试激活，避免被其他窗口抢占
        for _ in range(3):
            try:
                win.activate()
            except Exception:
                pass
            time.sleep(0.3)

        print(f"✅ 已强制激活窗口: {win.title}")
        # 给窗口置顶留一点时间
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"⚠️ 激活窗口失败: {e}")
        return False

# ---------- 点击开始按钮 ----------
def find_and_click_button():
    # 先强制激活启动器窗口，确保它在最前
    activate_launcher_window()

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

# ---------- 等待游戏进程 ----------
def wait_for_game_process(timeout=120):
    print(f"⏳ 等待游戏进程加载（超时 {timeout} 秒）...")
    print(f"💡 检测进程: {GAME_PROCESS_NAME}")
    start_time = time.time()
    last_progress = 0
    process_found = False

    while time.time() - start_time < timeout:
        try:
            game_running = False
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] == GAME_PROCESS_NAME:
                        game_running = True
                        process_found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if game_running:
                print(f"✅ 游戏进程已启动: {GAME_PROCESS_NAME}")
                print("⏳ 等待窗口完全加载...")
                time.sleep(5)
                return True

            elapsed = int(time.time() - start_time)
            if elapsed - last_progress >= 10:
                print(f"⏳ 已等待 {elapsed} 秒...")
                last_progress = elapsed
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 检查进程时出错: {e}")
            time.sleep(2)

    if process_found:
        print("⚠️ 游戏进程曾经启动但可能已退出")
    else:
        print(f"⚠️ 等待游戏进程超时（{timeout} 秒）")
    return False

# ---------- 主流程 ----------
def main():
    print("=" * 50)
    print("🎯 启动器预处理 - 启动游戏并等待加载")
    print("=" * 50)

    # 1. 关闭已有游戏进程
    print("🔍 检查并关闭游戏进程...")
    close_game_process()

    # 2. 启动沐瞳启动器
    print("🚀 启动沐瞳启动器...")
    print(f"📂 路径: {LAUNCHER_PATH}")
    subprocess.Popen([LAUNCHER_PATH])

    # 3. 等待启动器窗口
    print("⏳ 等待启动器加载...")
    if not wait_for_launcher_window(timeout=60):
        print("⚠️ 启动器窗口未出现，将尝试直接识别按钮...")
        time.sleep(3)
    else:
        time.sleep(1)

    # 4. 点击开始按钮
    for attempt in range(1, 6):
        print(f"🎯 第 {attempt} 次尝试点击开始按钮...")
        if find_and_click_button():
            print("🎮 游戏启动指令已发出！")
            break
        time.sleep(2)
    else:
        print("❌ 多次尝试后仍未点击成功")
        return 1

    # 5. 等待游戏进程加载
    if not wait_for_game_process(timeout=120):
        print("❌ 游戏进程未检测到，预处理失败")
        return 1

    print("✅ 游戏已完全加载，预处理完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())