# launch_via_launcher.py
import os
import sys
import time
import shutil
import zipfile
import datetime
import subprocess
import psutil

# ---------- DPI 修复（必须在 import pyautogui 之前） ----------
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = PER_MONITOR_DPI_AWARE
    print("✅ 已设置 DPI awareness = 2")
except Exception as e:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        print("✅ 已设置 DPI awareness (user32 fallback)")
    except Exception as e2:
        print(f"⚠️ 设置 DPI awareness 失败: {e} / {e2}")

import pyautogui
import pygetwindow as gw

# ---------- 路径与配置 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LAUNCHER_PATH = r"D:\Game\Watcher of Realms\moontonlauncher.exe"
BUTTON_IMAGE = os.path.join(SCRIPT_DIR, "start_button.png")
UPDATE_BUTTON_IMAGE = os.path.join(SCRIPT_DIR, "update_button.png")

CONFIDENCE = 0.8
WINDOW_TITLE_KEYWORD = "Watcher Of Realms"
GAME_PROCESS_NAME = "Watcher of Realms.exe"

# 失败时的输出目录（不存在就跳过打包）
CACHE_DIR = r"D:\Application\Automate\Cache"

# 日志文件（脚本自己的调试日志）
DEBUG_LOG = os.path.join(SCRIPT_DIR, "pretask_debug.log")

# ---------- 失败时截图 + 打包 ----------
def dump_failure(reason=""):
    """
    运行失败时：
      1. 截一张当前屏幕图
      2. 把截图、脚本日志、调试日志一起打包成 zip
      3. 输出到 CACHE_DIR
    如果 CACHE_DIR 不存在，直接跳过，不报错。
    """
    if not os.path.isdir(CACHE_DIR):
        print(f"ℹ️ 缓存目录不存在，跳过打包: {CACHE_DIR}")
        return

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = os.path.join(CACHE_DIR, f"pretask_fail_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)

        # 1. 截图
        shot_path = os.path.join(work_dir, "screen.png")
        try:
            pyautogui.screenshot(shot_path)
            print(f"📷 已截图: {shot_path}")
        except Exception as e:
            print(f"⚠️ 截图失败: {e}")

        # 2. 收集日志
        log_files = [
            DEBUG_LOG,
            os.path.join(SCRIPT_DIR, "launch_via_launcher.log"),
        ]
        for lf in log_files:
            if os.path.isfile(lf):
                try:
                    shutil.copy2(lf, work_dir)
                except Exception as e:
                    print(f"⚠️ 复制日志失败 {lf}: {e}")

        # 3. 写一份说明
        info_path = os.path.join(work_dir, "reason.txt")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(f"失败时间: {timestamp}\n")
            f.write(f"失败原因: {reason}\n")
            f.write(f"cwd: {os.getcwd()}\n")
            f.write(f"__file__: {os.path.abspath(__file__)}\n")
            f.write(f"LAUNCHER_PATH: {LAUNCHER_PATH}\n")
            try:
                f.write(f"pyautogui.size(): {pyautogui.size()}\n")
            except Exception:
                pass

        # 4. 打包成 zip
        zip_path = os.path.join(CACHE_DIR, f"pretask_fail_{timestamp}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(work_dir):
                for name in files:
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, work_dir)
                    zf.write(full, rel)

        # 5. 删除临时目录，只留 zip
        shutil.rmtree(work_dir, ignore_errors=True)

        print(f"📦 已打包失败信息: {zip_path}")
    except Exception as e:
        print(f"⚠️ 打包失败: {e}")

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

        for _ in range(3):
            try:
                win.activate()
            except Exception:
                pass
            time.sleep(0.3)

        print(f"✅ 已强制激活窗口: {win.title} "
              f"(rect: {win.left},{win.top} - {win.right},{win.bottom})")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"⚠️ 激活窗口失败: {e}")
        return False

# ---------- 点击升级按钮 ----------
def find_and_click_update_button(click_interval=2, max_wait=300):
    """
    循环检测升级按钮：
      - 优先用 OpenCV 模板匹配（会打印分数，便于调阈值）
      - 如果 cv2 不可用，回退到 pyautogui.locate
      - 找到就点，点完等 click_interval 秒，直到按钮消失
    """
    activate_launcher_window()

    if not os.path.isfile(UPDATE_BUTTON_IMAGE):
        print(f"ℹ️ 未找到升级按钮图片，跳过升级检测: {UPDATE_BUTTON_IMAGE}")
        return False

    # 尝试加载模板
    template = None
    th = tw = 0
    cv2 = None
    np = None
    try:
        import cv2 as _cv2
        import numpy as _np
        cv2 = _cv2
        np = _np
        template = cv2.imread(UPDATE_BUTTON_IMAGE)
        if template is not None:
            th, tw = template.shape[:2]
            print(f"🖼️ 模板尺寸: {tw} x {th}, 当前阈值: {CONFIDENCE}")
        else:
            print(f"⚠️ cv2 无法读取模板，回退到 pyautogui.locate")
    except Exception as e:
        print(f"ℹ️ 未启用 OpenCV 匹配（{e}），回退到 pyautogui.locate")

    print(f"🖥️ pyautogui.size() = {pyautogui.size()}")

    clicked_any = False
    start_time = time.time()

    while time.time() - start_time < max_wait:
        match_top_left = None  # (x, y)

        # ---------- 优先用 OpenCV ----------
        if template is not None:
            try:
                screen = pyautogui.screenshot()
                screen_np = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
                result = cv2.matchTemplate(
                    screen_np, template, cv2.TM_CCOEFF_NORMED
                )
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                print(f"📊 最高匹配分数: {max_val:.4f}  (阈值 {CONFIDENCE})  位置: {max_loc}")

                if max_val >= CONFIDENCE:
                    match_top_left = max_loc
            except Exception as e:
                print(f"⚠️ OpenCV 匹配出错，本次回退 pyautogui: {e}")
                match_top_left = None

        # ---------- 回退方案 ----------
        if match_top_left is None and template is None:
            try:
                box = pyautogui.locate(UPDATE_BUTTON_IMAGE, confidence=CONFIDENCE)
                if box:
                    match_top_left = (box.left, box.top)
                    tw, th = box.width, box.height
                    print(f"🎯 locate 匹配区域: {box}")
            except Exception as e:
                print(f"⚠️ locate 识别失败: {e}")

        # ---------- 处理匹配结果 ----------
        if match_top_left is not None:
            x, y = match_top_left
            cx, cy = x + tw // 2, y + th // 2

            try:
                print(f"🎯 点击中心点: ({cx}, {cy})")
                pyautogui.click(cx, cy)
                clicked_any = True
                print(f"✅ 已点击，等待 {click_interval} 秒...")
            except Exception as e:
                print(f"⚠️ 点击失败: {e}")
            time.sleep(click_interval)
        else:
            if clicked_any:
                print("✅ 升级按钮已消失，升级流程已启动")
            else:
                print("ℹ️ 未检测到升级按钮，无需升级")
            return clicked_any

    print(f"⚠️ 升级按钮检测超时（{max_wait} 秒），停止点击")
    return clicked_any

# ---------- 点击开始按钮 ----------
def find_and_click_button():
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

    # 3.5 检测到界面后等待 5 秒，让启动器 UI 稳定
    print("⏳ 界面已就绪，等待 5 秒让 UI 稳定...")
    time.sleep(5)

    # 3.6 检测并循环点击升级按钮，直到按钮消失
    print("🔍 检测升级按钮...")
    if find_and_click_update_button(click_interval=2, max_wait=300):
        print("⏳ 升级已触发，等待 10 秒让升级流程稳定...")
        time.sleep(10)
    else:
        print("ℹ️ 无需升级，继续启动流程")

    # 4. 点击开始按钮
    for attempt in range(1, 6):
        print(f"🎯 第 {attempt} 次尝试点击开始按钮...")
        if find_and_click_button():
            print("🎮 游戏启动指令已发出！")
            break
        time.sleep(2)
    else:
        print("❌ 多次尝试后仍未点击成功")
        dump_failure("点击开始按钮失败（5 次尝试均未找到按钮）")
        return 1

    # 5. 等待游戏进程加载
    if not wait_for_game_process(timeout=120):
        print("❌ 游戏进程未检测到，预处理失败")
        dump_failure("等待游戏进程超时（120 秒内未检测到 Watcher of Realms.exe）")
        return 1

    print("✅ 游戏已完全加载，预处理完成")
    return 0

# ---------- 入口 ----------
if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        import traceback
        try:
            with open(DEBUG_LOG, "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception:
            pass
        dump_failure("脚本抛出未捕获异常")
        code = 2

    sys.exit(code)