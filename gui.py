import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import os

# ==========================
# Helpers
# ==========================

def resource_path(relative):
    """Permite achar arquivos ao virar EXE com PyInstaller"""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, relative)

# ==========================
# Script executor
# ==========================

CURRENT_BIND = None
RECORDING = False

def run_script():
    def task():
        try:
            script_path = resource_path("arrow-detector.py")
            subprocess.Popen(
                ["python", script_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

    threading.Thread(target=task, daemon=True).start()


# ==========================
# Hotkey
# ==========================

def register_hotkey(bind):
    global CURRENT_BIND

    if CURRENT_BIND:
        try:
            keyboard.remove_hotkey(CURRENT_BIND)
        except:
            pass

    CURRENT_BIND = keyboard.add_hotkey(bind, run_script)


def start_record_hotkey():
    global RECORDING
    RECORDING = True

    hotkey_value_label.config(text="Aguardando tecla...")

    threading.Thread(target=capture_hotkey, daemon=True).start()


def capture_hotkey():
    global RECORDING
    key = keyboard.read_hotkey(suppress=False)

    RECORDING = False
    hotkey_value_label.config(text=key)

    try:
        register_hotkey(key)
        messagebox.showinfo("Sucesso", f"Hotkey configurada: {key}")
    except:
        messagebox.showerror("Erro", "Não foi possível registrar esta hotkey.")


# ==========================
# Tray icon
# ==========================

def create_tray_icon():
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.rectangle((8, 8, 56, 56), outline="white")

    menu = pystray.Menu(
        pystray.MenuItem("Abrir", show_window),
        pystray.MenuItem("Sair", quit_app)
    )

    icon = pystray.Icon("ArrowDetector", img, "Arrow Detector", menu)
    return icon

def show_window():
    root.deiconify()

def hide_window():
    root.withdraw()

def quit_app(icon=None, item=None):
    if icon:
        icon.stop()
    root.destroy()
    os._exit(0)


# ==========================
# GUI / Dark Mode
# ==========================

root = tk.Tk()
root.title("Arrow Detector")
root.geometry("480x350")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

def style(widget, fg="white", bg="#1e1e1e"):
    widget.configure(fg=fg, bg=bg)

# Title
label = tk.Label(root, text="Arrow Detector", font=("Segoe UI", 18, "bold"))
style(label)
label.pack(pady=10)

# Hotkey section
hotkey_title = tk.Label(root, text="Hotkey atual:", font=("Segoe UI", 12))
style(hotkey_title)
hotkey_title.pack(pady=5)

hotkey_value_label = tk.Label(root, text="Nenhuma", font=("Segoe UI", 14, "bold"))
style(hotkey_value_label)
hotkey_value_label.pack(pady=3)

# Button: record hotkey
btn_record = tk.Button(root, text="Gravar Nova Hotkey",
                       command=start_record_hotkey,
                       font=("Segoe UI", 12),
                       bg="#3b3b3b", fg="white",
                       width=20)
btn_record.pack(pady=10)

# Run button
btn_run = tk.Button(root, text="Run",
                    command=run_script,
                    font=("Segoe UI", 14, "bold"),
                    bg="#5c5cff", fg="white",
                    width=20)
btn_run.pack(pady=10)

# Hide to tray
btn_hide = tk.Button(root, text="Minimizar P/ Bandeja",
                     command=hide_window,
                     font=("Segoe UI", 10),
                     bg="#333", fg="white")
btn_hide.pack(pady=5)

# Tray icon thread
icon = create_tray_icon()
threading.Thread(target=lambda: icon.run(), daemon=True).start()

root.protocol("WM_DELETE_WINDOW", quit_app)
root.mainloop()
