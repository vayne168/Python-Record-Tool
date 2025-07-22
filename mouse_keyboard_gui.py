import os
import sys
import tkinter as tk
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfilename, askopenfilename
import threading, time, json
from pynput import mouse, keyboard
import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_script_path(filename):
    scripts_dir = os.path.join(get_exe_dir(), "Scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    return os.path.join(scripts_dir, filename)

# 全域狀態
events = {}
event_id = 0
prev_time = round(time.time() * 1000)
stop_flag = False
recording = False
f6_recording = False
f8_looping = False
loaded_file = get_script_path("default.json")
keyboard_controller = KeyboardController()
record_start_time = None

# GUI 初始化
root = tk.Tk()
root.title("滑鼠＋鍵盤 錄製 / 播放 工具")
root.attributes('-topmost', True)

status_label = tk.Label(root, text="狀態：等待操作")
status_label.pack()

log_area = scrolledtext.ScrolledText(root, width=60, height=20)
log_area.pack()

def log(text):
    log_area.insert(tk.END, text + "\n")
    log_area.see(tk.END)

# ===== 錄製邏輯 =====
def record_event(event_type, details):
    global event_id, prev_time, events
    now = round(time.time() * 1000)
    wait_time = now - prev_time
    event_id += 1
    events[event_id] = [wait_time, event_type] + details
    prev_time = now
    log(f"[{event_type}] {details}")

def on_click(x, y, button, pressed):
    action = 'mouse_down' if pressed else 'mouse_up'
    record_event(action, [str(button), x, y])

def on_press(key):
    global stop_flag
    if key in [keyboard.Key.f6]:
        return
    try:
        record_event('key_down', [str(key)])
    except:
        record_event('key_down', [str(key)])

def on_release(key):
    if key in [keyboard.Key.f6]:
        return
    try:
        record_event('key_up', [str(key)])
    except:
        record_event('key_up', [str(key)])

def start_recording():
    global stop_flag, recording, events, event_id, prev_time, record_start_time
    if recording:
        return
    stop_flag = False
    recording = True
    events = {}
    event_id = 0
    prev_time = round(time.time() * 1000)
    record_start_time = time.time()
    log("🚩 錄製開始...")

    def update_status_timer():
        while recording:
            elapsed = int(time.time() - record_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            status_label.config(text=f"狀態：錄製中 (按 F6 暫停) {minutes}:{seconds:02d}")
            time.sleep(0.5)

    threading.Thread(target=update_status_timer, daemon=True).start()

    def record_thread():
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        mouse_listener.start()
        keyboard_listener.start()
        while not stop_flag:
            time.sleep(0.01)
        mouse_listener.stop()
        keyboard_listener.stop()
        with open(get_script_path("default.json"), "w") as f:
            json.dump(events, f, indent=2)
        log("✅ 錄製完成，已儲存為 default.json")
        status_label.config(text="狀態：錄製完成")
        globals()['recording'] = False
        root.title("default.json")

    threading.Thread(target=record_thread).start()

def stop_recording():
    global stop_flag, recording
    stop_flag = True
    recording = False
    log("🛑 偵測到 Stop")

# ===== 另存為... =====
def save_to_file():
    global loaded_file
    if not events:
        log("⚠️ 沒有可儲存的事件")
        return
    filepath = asksaveasfilename(defaultextension=".json",
                                 filetypes=[("JSON Files", "*.json")],
                                 initialdir=os.path.join(get_exe_dir(), "Scripts"))
    if filepath:
        with open(filepath, "w") as f:
            json.dump(events, f, indent=2)
        loaded_file = filepath
        log(f"💾 已儲存事件至 {filepath}")
        root.title(os.path.basename(filepath))

# ===== 選擇播放檔案 =====
def load_event_file():
    global loaded_file
    filepath = askopenfilename(filetypes=[("JSON Files", "*.json")],
                                initialdir=os.path.join(get_exe_dir(), "Scripts"))
    if filepath:
        loaded_file = filepath
        log(f"📂 已選擇檔案：{filepath}")
        status_label.config(text="狀態：已載入檔案，按 F8 播放")
        root.title(os.path.basename(filepath))

# ===== 播放邏輯（循環播放） =====
def loop_play_events():
    global loaded_file
    if not loaded_file:
        log("⚠️ 尚未載入播放檔案，請先使用『讀取檔案』")
        return

    status_label.config(text="狀態：播放中（循環）")
    log("🔁 開始循環播放")

    def loop_thread():
        global f8_looping
        try:
            with open(loaded_file, "r") as f:
                data = json.load(f)
        except:
            log("❌ 無法讀取檔案")
            f8_looping = False
            return

        start_time = time.time()
        play_count = 0
        base_title = os.path.basename(loaded_file)

        def update_timer():
            while f8_looping:
                elapsed = int(time.time() - start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                status_label.config(text=f"狀態：播放中 (按 F8 停止) {minutes}:{seconds:02d} 目前共 {play_count} 次")
                time.sleep(0.5)

        threading.Thread(target=update_timer, daemon=True).start()

        while f8_looping:
            for key in sorted(data.keys(), key=int):
                wait_time, event_type, *event_data = data[key]
                time.sleep(wait_time / 1000.0)
                if not f8_looping:
                    break
                try:
                    if event_type == 'mouse_down':
                        b, x, y = event_data
                        pyautogui.mouseDown(x=int(x), y=int(y), button=b.split('.')[-1])
                    elif event_type == 'mouse_up':
                        b, x, y = event_data
                        pyautogui.mouseUp(x=int(x), y=int(y), button=b.split('.')[-1])
                    elif event_type == 'key_down':
                        k = event_data[0].replace("'", "")
                        key_obj = eval(k) if "Key." in k else k
                        keyboard_controller.press(key_obj)
                    elif event_type == 'key_up':
                        k = event_data[0].replace("'", "")
                        key_obj = eval(k) if "Key." in k else k
                        keyboard_controller.release(key_obj)
                except:
                    pass
            play_count += 1
            log("🔁 播放一次完成")

        log("⏹ 停止播放")
        status_label.config(text="狀態：播放停止")
        root.title(base_title)

    threading.Thread(target=loop_thread).start()

# ===== GUI 按鈕 =====
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="📂 讀取檔案", width=15, command=load_event_file).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="💾 另存為...", width=15, command=save_to_file).grid(row=0, column=1, padx=5)

# ===== 全域熱鍵監聽（F6 錄製、F8 播放）=====
def global_key_handler(key):
    global f6_recording, f8_looping, loaded_file
    try:
        if key == keyboard.Key.f6:
            if not f6_recording:
                f6_recording = True
                log("🔴 [F6] 開始錄製")
                start_recording()
            else:
                f6_recording = False
                log("🛑 [F6] 停止錄製")
                stop_recording()
        elif key == keyboard.Key.f8:
            if not f8_looping:
                if not loaded_file:
                    log("⚠️ 尚未載入播放檔案，請先使用『讀取檔案』")
                    return
                f8_looping = True
                loop_play_events()
            else:
                f8_looping = False
    except Exception as e:
        log(f"❌ 全域熱鍵錯誤: {e}")

threading.Thread(target=lambda: keyboard.Listener(on_press=global_key_handler).run(), daemon=True).start()

# ===== 主迴圈 =====
root.mainloop()
