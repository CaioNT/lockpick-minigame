import time
import cv2
import numpy as np
from PIL import ImageGrab
from pynput.keyboard import Controller, Key
import traceback
from datetime import datetime
import os

LOG_FILE = "arrow-log.txt"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


# CLASSIFICA A DIREÇÃO
def classify_arrow_direction(roi_mask):
    try:
        h, w = roi_mask.shape
        if h < 3 or w < 3:
            return None

        h_mid = h // 2
        w_mid = w // 2

        top_row = np.sum(roi_mask[:h_mid, :])
        bottom_row = np.sum(roi_mask[h_mid:, :])
        left_col = np.sum(roi_mask[:, :w_mid])
        right_col = np.sum(roi_mask[:, w_mid:])

        total_v = top_row + bottom_row
        total_h = left_col + right_col

        if total_v == 0 or total_h == 0:
            return None

        top_pct = top_row / total_v
        bottom_pct = bottom_row / total_v
        left_pct = left_col / total_h
        right_pct = right_col / total_h

        diff_vertical = abs(top_pct - bottom_pct)
        diff_horizontal = abs(left_pct - right_pct)

        aspect_ratio = w / h if h > 0 else 1
        vertical_adjusted = diff_vertical * (2 if aspect_ratio < 0.7 else 1.1)

        if vertical_adjusted > diff_horizontal:
            return 'CIMA' if top_pct > bottom_pct else 'BAIXO'
        else:
            return 'ESQUERDA' if left_pct > right_pct else 'DIREITA'
    except:
        return None


# DETECÇÃO DAS SETAS - ADAPTATIVA PARA MÚLTIPLAS RESOLUÇÕES
def detect_arrows_hud_realtime():
    try:
        screenshot = ImageGrab.grab()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        height, width = img.shape[:2]
        
        log(f"Resolução detectada: {width}x{height}")
        
        # Adapta zona HUD baseado na resolução
        # Em 1920x1080, y está entre 920-950 (86-88% da altura)
        hud_start_pct = 0.855
        hud_end_pct = 0.880
        
        y_start = int(height * hud_start_pct)
        y_end = int(height * hud_end_pct)
        
        log(f"Zona HUD: y={y_start} até {y_end}")

        lower_white = np.array([220, 220, 220])
        upper_white = np.array([255, 255, 255])

        mask = cv2.inRange(img, lower_white, upper_white)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        arrows = []
        
        # Adapta limites de área baseado na resolução
        # Em 1920x1080: área entre 80-140
        resolution_factor = (width * height) / (1920 * 1080)
        area_min = int(80 * resolution_factor)
        area_max = int(140 * resolution_factor)
        
        log(f"Limites de área: {area_min}-{area_max}")

        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            # Verifica se está na zona HUD
            if y < y_start or y > y_end:
                continue
                
            if area < area_min or area > area_max:
                continue
                
            ratio = w / h if h > 0 else 0
            if ratio < 0.4 or ratio > 2.5:
                continue

            roi_mask = mask[y:y+h, x:x+w]
            direction = classify_arrow_direction(roi_mask)
            if direction:
                arrows.append({
                    'x': x,
                    'center_x': x + w // 2,
                    'direction': direction
                })

        arrows.sort(key=lambda a: a['center_x'])

        log(f"Setas detectadas: {[a['direction'] for a in arrows]}")
        return [arrow['direction'] for arrow in arrows]

    except Exception:
        log("Erro em detect_arrows_hud_realtime:\n" + traceback.format_exc())
        return []


# INPUT DAS SETAS
kb = Controller()

def press_arrow_key(direction, duration=0.01):
    try:
        direction_map = {
            'CIMA': Key.up,
            'BAIXO': Key.down,
            'ESQUERDA': Key.left,
            'DIREITA': Key.right
        }
        key = direction_map.get(direction)
        if key:
            kb.press(key)
            time.sleep(duration)
            kb.release(key)
    except:
        log("Erro ao pressionar tecla:\n" + traceback.format_exc())


def execute_arrows(directions, delay=0.01):
    for direction in directions:
        press_arrow_key(direction)
        time.sleep(delay)


# MAIN
if __name__ == "__main__":
    try:
        log("===== EXECUÇÃO DO SCRIPT =====")
        directions = detect_arrows_hud_realtime()
        if directions:
            execute_arrows(directions)
        else:
            log("Nenhuma seta detectada.")
    except:
        log("Erro no main:\n" + traceback.format_exc())