# Mouse & Keyboard Recorder Tool

A Python-based desktop GUI tool for recording and replaying mouse and keyboard actions.  
Perfect for automation, UI testing, macro scripting, and productivity tasks.

---

## 🎯 Features

- 🎬 Record mouse clicks and keyboard keystrokes with timing
- 💾 Save recordings as `.json` scripts
- ▶️ Replay scripts in a loop
- 🖱️ Global hotkeys:  
  - `F6`: Start/Stop recording  
  - `F8`: Start/Stop playback
- 📁 All scripts stored in a `Scripts/` folder next to the executable
- 🪟 Always-on-top GUI with live status and timers

---

## 📦 How to Use

1. **Download or clone this repo**
2. **Run the `.exe` file** (no Python needed)
3. Use the buttons or hotkeys to record/play actions
4. Scripts are automatically saved to `Scripts/default.json`, or you can save/load custom ones

> 🔧 Want to customize? Use the Python source file `mouse_keyboard_gui.py`.

---

## 📂 File Structure

```
/
├── mouse_keyboard_gui.py       # Python source code
├── mouse_keyboard_gui.exe      # Standalone executable
├── Scripts/                    # All recorded or imported .json scripts
│   └── default.json
```

---
## 📥 Releases

Download the latest `.exe` from the [Releases](../../releases) page.

---

## 📄 License

MIT License — feel free to use, modify, and share.
