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
    exe_dir = os.path.dirname(sys.executable)
    exe_path = os.path.join(exe_dir, relative_path)
    
    if os.path.exists(exe_path):
        return exe_path
    
    current_path = os.path.join(os.path.abspath("."), relative_path)
    if os.path.exists(current_path):
        return current_path
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==========================
# Debug / Logging
# ==========================

def log_debug(msg):
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
            
            exe_path = resource_path("arrow-detector.exe")
            py_path = resource_path("arrow-detector.py")

            if os.path.exists(exe_path):
                log_debug(f"Encontrado .exe, executando: {exe_path}")
                subprocess.Popen(
                    [exe_path],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            elif os.path.exists(py_path):
                log_debug(f"Encontrado .py, executando com python: {py_path}")
                subprocess.Popen(
                    [sys.executable, py_path],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
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
        status_label.config(text="✓ Hotkey registrada", fg="#00ff00")
    except Exception as e:
        log_debug(f"Erro ao registrar hotkey: {e}")
        raise


def start_record_hotkey():
    global RECORDING
    RECORDING = True
    hotkey_value_label.config(text="Aguardando tecla...", fg="#ffaa00")
    status_label.config(text="Gravando...", fg="#ffaa00")
    threading.Thread(target=capture_hotkey, daemon=True).start()


def capture_hotkey():
    global RECORDING
    try:
        key = keyboard.read_hotkey(suppress=False)
        RECORDING = False
        hotkey_value_label.config(text=key, fg="#00ff00")
        register_hotkey(key)
    except Exception as e:
        RECORDING = False
        log_debug(f"Erro ao capturar hotkey: {e}")
        messagebox.showerror("Erro", "Não foi possível registrar esta hotkey.")


# ==========================
# Tray icon
# ==========================

def create_tray_icon():
    img = Image.new("RGB", (64, 64), color="#1a1a1a")
    draw = ImageDraw.Draw(img)
    draw.rectangle((8, 8, 56, 56), outline="#00ff00", width=2)
    draw.text((20, 24), "AD", fill="#00ff00")

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
# GUI / Dark Mode Premium
# ==========================

root = tk.Tk()
root.title("Arrow Detector")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="#0f0f0f")

# Cores
BG_PRIMARY = "#0f0f0f"
BG_SECONDARY = "#1a1a1a"
ACCENT_PRIMARY = "#00ff00"
ACCENT_SECONDARY = "#00cc00"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#aaaaaa"

# Frame principal com borda
main_frame = tk.Frame(root, bg=BG_PRIMARY)
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Título com estilo
title_frame = tk.Frame(main_frame, bg=BG_PRIMARY)
title_frame.pack(pady=20)

title_label = tk.Label(title_frame, text="▶ ARROW DETECTOR", 
                       font=("Courier New", 24, "bold"), 
                       fg=ACCENT_PRIMARY, bg=BG_PRIMARY)
title_label.pack()

subtitle_label = tk.Label(title_frame, text="Detecção automática de setas", 
                          font=("Courier New", 10), 
                          fg=TEXT_SECONDARY, bg=BG_PRIMARY)
subtitle_label.pack()

# Separador
separator1 = tk.Frame(main_frame, height=1, bg=ACCENT_PRIMARY)
separator1.pack(fill=tk.X, pady=10)

# Seção Hotkey
hotkey_section = tk.Frame(main_frame, bg=BG_SECONDARY, relief=tk.FLAT)
hotkey_section.pack(fill=tk.X, pady=10, padx=5)

hotkey_title = tk.Label(hotkey_section, text="⌨ HOTKEY CONFIGURADA", 
                        font=("Courier New", 11, "bold"), 
                        fg=ACCENT_PRIMARY, bg=BG_SECONDARY)
hotkey_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

hotkey_value_label = tk.Label(hotkey_section, text="Nenhuma", 
                              font=("Courier New", 14, "bold"), 
                              fg=TEXT_PRIMARY, bg=BG_SECONDARY)
hotkey_value_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

status_label = tk.Label(hotkey_section, text="Clique em 'Gravar Nova Hotkey'", 
                       font=("Courier New", 9), 
                       fg=TEXT_SECONDARY, bg=BG_SECONDARY)
status_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

# Separador
separator2 = tk.Frame(main_frame, height=1, bg=ACCENT_PRIMARY)
separator2.pack(fill=tk.X, pady=10)

# Botões de controle
button_frame = tk.Frame(main_frame, bg=BG_PRIMARY)
button_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Função para estilizar botões
def create_styled_button(parent, text, command, color, width=25):
    btn = tk.Button(parent, 
                   text=text,
                   command=command,
                   font=("Courier New", 11, "bold"),
                   bg=color,
                   fg="#000000" if color == ACCENT_PRIMARY else "#ffffff",
                   relief=tk.FLAT,
                   cursor="hand2",
                   width=width,
                   padx=10, pady=8)
    
    def on_enter(e):
        btn.config(bg=ACCENT_SECONDARY if color == ACCENT_PRIMARY else "#00aa00")
    
    def on_leave(e):
        btn.config(bg=color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

btn_record = create_styled_button(button_frame, "◉ GRAVAR HOTKEY", 
                                 start_record_hotkey, "#333333")
btn_record.pack(pady=8)

btn_run = create_styled_button(button_frame, "► EXECUTAR", 
                              run_script, ACCENT_PRIMARY)
btn_run.pack(pady=8)

# Frame para botões secundários
secondary_frame = tk.Frame(button_frame, bg=BG_PRIMARY)
secondary_frame.pack(fill=tk.X, pady=10)

btn_debug = create_styled_button(secondary_frame, "📋 DEBUG", 
                                lambda: os.startfile("lockpick-debug.log") if os.path.exists("lockpick-debug.log") else messagebox.showinfo("Info", "Nenhum log encontrado ainda."),
                                "#222222", width=12)
btn_debug.pack(side=tk.LEFT, padx=5)

btn_hide = create_styled_button(secondary_frame, "🗕 BANDEJA", 
                               hide_window, "#222222", width=12)
btn_hide.pack(side=tk.RIGHT, padx=5)

# Separador
separator3 = tk.Frame(main_frame, height=1, bg=ACCENT_PRIMARY)
separator3.pack(fill=tk.X, pady=10)

# Rodapé
footer = tk.Label(main_frame, text="v1.0 • Arrow Detector Pro", 
                 font=("Courier New", 8), 
                 fg=TEXT_SECONDARY, bg=BG_PRIMARY)
footer.pack(pady=10)

log_debug("=== APLICAÇÃO INICIADA ===")

icon = create_tray_icon()
threading.Thread(target=lambda: icon.run(), daemon=True).start()

root.protocol("WM_DELETE_WINDOW", quit_app)
root.mainloop()