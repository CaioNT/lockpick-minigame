import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import os
import traceback

# ==========================
# Helpers
# ==========================

def resource_path(relative_path):
    # Procura primeiro no diretório do executável
    exe_dir = os.path.dirname(sys.executable)
    exe_path = os.path.join(exe_dir, relative_path)
    
    if os.path.exists(exe_path):
        return exe_path
    
    # Se não encontrar, tenta no diretório atual
    current_path = os.path.join(os.path.abspath("."), relative_path)
    if os.path.exists(current_path):
        return current_path
    
    # Fallback para o diretório do PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==========================
# Debug / Logging
# ==========================

def log_debug(msg):
    """Salva logs para debug"""
    try:
        with open("lockpick-debug.log", "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except:
        pass


# ==========================
# Script executor
# ==========================

CURRENT_BIND = None
RECORDING = False

def run_script():
    def task():
        try:
            log_debug("=== Iniciando run_script ===")
            
            # Tenta usar o .exe primeiro
            exe_path = resource_path("arrow-detector.exe")
            py_path = resource_path("arrow-detector.py")

            log_debug(f"Procurando .exe em: {exe_path}")
            log_debug(f"Procurando .py em: {py_path}")
            log_debug(f"Diretório atual: {os.getcwd()}")
            log_debug(f"Arquivos no diretório: {os.listdir('.')}")

            if os.path.exists(exe_path):
                log_debug(f"Encontrado .exe, executando: {exe_path}")
                result = subprocess.Popen(
                    [exe_path],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                log_debug(f"Processo iniciado com PID: {result.pid}")
                
            elif os.path.exists(py_path):
                log_debug(f"Encontrado .py, executando com python: {py_path}")
                result = subprocess.Popen(
                    [sys.executable, py_path],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                log_debug(f"Processo iniciado com PID: {result.pid}")
                
            else:
                log_debug("ERRO: Nenhum arquivo encontrado!")
                messagebox.showerror("Erro", 
                    f"arrow-detector não encontrado!\n\n"
                    f"Procurado em:\n"
                    f"{exe_path}\n{py_path}\n\n"
                    f"Arquivos disponíveis:\n"
                    f"{os.listdir('.')}")

        except Exception as e:
            error_msg = traceback.format_exc()
            log_debug(f"ERRO: {error_msg}")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}\n\nVerifique lockpick-debug.log")

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

    try:
        CURRENT_BIND = keyboard.add_hotkey(bind, run_script)
        log_debug(f"Hotkey registrada: {bind}")
    except Exception as e:
        log_debug(f"Erro ao registrar hotkey: {e}")
        raise


def start_record_hotkey():
    global RECORDING
    RECORDING = True
    hotkey_value_label.config(text="Aguardando tecla...")
    threading.Thread(target=capture_hotkey, daemon=True).start()


def capture_hotkey():
    global RECORDING
    try:
        key = keyboard.read_hotkey(suppress=False)
        RECORDING = False
        hotkey_value_label.config(text=key)
        register_hotkey(key)
    except Exception as e:
        RECORDING = False
        log_debug(f"Erro ao capturar hotkey: {e}")
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

label = tk.Label(root, text="Arrow Detector", font=("Segoe UI", 18, "bold"))
style(label)
label.pack(pady=10)

hotkey_title = tk.Label(root, text="Hotkey atual:", font=("Segoe UI", 12))
style(hotkey_title)
hotkey_title.pack(pady=5)

hotkey_value_label = tk.Label(root, text="Nenhuma", font=("Segoe UI", 14, "bold"))
style(hotkey_value_label)
hotkey_value_label.pack(pady=3)

btn_record = tk.Button(root, text="Gravar Nova Hotkey",
                       command=start_record_hotkey,
                       font=("Segoe UI", 12),
                       bg="#3b3b3b", fg="white",
                       width=20)
btn_record.pack(pady=10)

btn_run = tk.Button(root, text="Run",
                    command=run_script,
                    font=("Segoe UI", 14, "bold"),
                    bg="#5c5cff", fg="white",
                    width=20)
btn_run.pack(pady=10)

btn_debug = tk.Button(root, text="Ver Debug Log",
                      command=lambda: os.startfile("lockpick-debug.log") if os.path.exists("lockpick-debug.log") else messagebox.showinfo("Info", "Nenhum log encontrado ainda."),
                      font=("Segoe UI", 10),
                      bg="#555", fg="white")
btn_debug.pack(pady=5)

btn_hide = tk.Button(root, text="Minimizar P/ Bandeja",
                     command=hide_window,
                     font=("Segoe UI", 10),
                     bg="#333", fg="white")
btn_hide.pack(pady=5)

log_debug("=== APLICAÇÃO INICIADA ===")

icon = create_tray_icon()
threading.Thread(target=lambda: icon.run(), daemon=True).start()

root.protocol("WM_DELETE_WINDOW", quit_app)
root.mainloop()