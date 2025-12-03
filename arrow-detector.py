import time
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import keyboard
import threading

def detect_arrows_hud_realtime():
    """
    Detecta as 12 setas do HUD em tempo real capturando a tela.
    """
    
    print("Capturando screenshot da tela...")
    time.sleep(0.1)
    
    # Captura a tela
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    height, width = img.shape[:2]
    print(f"Dimensões da imagem: {width}x{height}")
    
    # Define intervalo para cor branca
    lower_white = np.array([220, 220, 220])
    upper_white = np.array([255, 255, 255])
    
    # Cria máscara
    mask = cv2.inRange(img, lower_white, upper_white)
    
    # Aplica morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # Detecta contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Total de contornos encontrados: {len(contours)}")
    
    arrows = []
    
    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filtro por tamanho
        if area < 80 or area > 140:
            continue
        
        # Aspecto ratio
        ratio = w / h if h > 0 else 0
        if ratio < 0.4 or ratio > 2.5:
            continue
        
        # FILTRO CRÍTICO: Aceita APENAS setas na faixa Y central (920-950)
        if y < 920 or y > 950:
            continue
        
        print(f"[ACEITA] Contorno {idx}: área={area:.0f}, pos=({x},{y}), tamanho=({w}x{h}), ratio={ratio:.2f}")
        
        roi_mask = mask[y:y+h, x:x+w]
        direction = classify_arrow_direction(roi_mask)
        
        if direction:
            arrows.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'direction': direction,
                'center_x': x + w // 2,
                'area': area
            })
    
    print(f"\nSetas detectadas: {len(arrows)}")
    
    # Ordena esquerda para direita
    arrows.sort(key=lambda a: a['center_x'])
    
    # Salva debug
    debug_img = img.copy()
    for i, arrow in enumerate(arrows):
        x, y, w, h = arrow['x'], arrow['y'], arrow['w'], arrow['h']
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(debug_img, f"{i+1}:{arrow['direction']}", (x, y-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imwrite('debug_arrows_realtime.png', debug_img)
    print("Imagem de debug salva: debug_arrows_realtime.png")
    
    return [arrow['direction'] for arrow in arrows]

def classify_arrow_direction(roi_mask):
    """
    Classifica direção analisando a distribuição de pixels.
    """
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
    if aspect_ratio < 0.7:
        vertical_adjusted = diff_vertical * 2
    else:
        vertical_adjusted = diff_vertical * 1.1
    
    if vertical_adjusted > diff_horizontal:
        if top_pct > bottom_pct:
            return 'CIMA'
        else:
            return 'BAIXO'
    else:
        if left_pct > right_pct:
            return 'ESQUERDA'
        else:
            return 'DIREITA'

from pynput.keyboard import Controller, Key
kb = Controller()

def press_arrow_key(direction, duration=0.1):
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
        print(f"Pressionou: {direction}")

def execute_arrows(directions, delay=0.2):
    """
    Executa a sequência de setas pressionando as teclas.
    """
    print(f"\n{'='*60}")
    print("Iniciando execução das setas...")
    print(f"Total de setas a pressionar: {len(directions)}")
    print('='*60)
    
    time.sleep(0.05)  # Aguarda 1 segundo antes de iniciar
    
    for i, direction in enumerate(directions, 1):
        print(f"[{i}/{len(directions)}] Pressionando: {direction}")
        press_arrow_key(direction)
        time.sleep(delay)
    
    print(f"\n{'='*60}")
    print("✓ Sequência concluída!")
    print('='*60)

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("=== RECONHECEDOR DE SETAS HUD - TEMPO REAL ===")
    print("=" * 60)
    print("\nO programa capturará a tela em 3 segundos...")
    print("Certifique-se de que o jogo com as setas está visível!\n")
    
    # Aguarda 3 segundos
    for i in range(3, 0, -1):
        print(f"Capturando em {i}...")
        time.sleep(1)
    
    print("\nCapturando...")
    directions = detect_arrows_hud_realtime()
    
    if directions:
        print(f"\n{'='*60}")
        print(f"✓ Total de setas detectadas: {len(directions)}\n")
        print("Sequência de setas:")
        for i, direction in enumerate(directions, 1):
            print(f"  {i:2d}. {direction}")
        print(f"\nInput das direções:")
        print(f"{' -> '.join(directions)}")
        print('='*60)
        
        print("\nExecutando as setas automaticamente em 1 segundo...\n")
        time.sleep(1)
        execute_arrows(directions, delay=0.05)
        
        print("\n(Programa encerrará em 2 segundos...)")
        time.sleep(2)
    else:
        print("\n✗ Nenhuma seta foi detectada!")
        print("Verifique se o jogo está visível e tente novamente.")
        time.sleep(3)