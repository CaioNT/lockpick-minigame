import cv2
import numpy as np
import os

def detect_arrows_hud(image_path):
    """
    Detecta as 12 setas do HUD central.
    Ignora setas em outras posições (como as do canto esquerdo).
    """
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro: Não foi possível carregar a imagem {image_path}")
        return []
    
    height, width = img.shape[:2]
    print(f"Dimensões da imagem: {width}x{height}")
    
    # Define intervalo para cor branca
    lower_white = np.array([220, 220, 220])
    upper_white = np.array([255, 255, 255])
    
    # Cria máscara da imagem completa
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
        # Ignora setas no canto esquerdo inferior (Y > 1000)
        if y < 920 or y > 950:
            print(f"[IGNORADA] Contorno {idx}: Y={y} fora do range (920-950)")
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
    
    print(f"\nSetas aceitas: {len(arrows)}")
    
    # Ordena esquerda para direita
    arrows.sort(key=lambda a: a['center_x'])
    
    # Cria imagem de debug
    debug_img = img.copy()
    for i, arrow in enumerate(arrows):
        x, y, w, h = arrow['x'], arrow['y'], arrow['w'], arrow['h']
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(debug_img, f"{i+1}:{arrow['direction']}", (x, y-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imwrite('debug_arrows.png', debug_img)
    print("Imagem de debug salva: debug_arrows.png")
    
    return [arrow['direction'] for arrow in arrows]

def classify_arrow_direction(roi_mask):
    """
    Classifica direção analisando a distribuição de pixels.
    A PONTA da seta tem MAIS pixels (concentrado), a base tem MENOS.
    """
    h, w = roi_mask.shape
    
    if h < 3 or w < 3:
        return None
    
    # Divide em quadrantes
    h_mid = h // 2
    w_mid = w // 2
    
    # Conta pixels em cada metade
    top_row = np.sum(roi_mask[:h_mid, :])
    bottom_row = np.sum(roi_mask[h_mid:, :])
    left_col = np.sum(roi_mask[:, :w_mid])
    right_col = np.sum(roi_mask[:, w_mid:])
    
    # Total de pixels
    total_v = top_row + bottom_row
    total_h = left_col + right_col
    
    if total_v == 0 or total_h == 0:
        return None
    
    # Calcula percentuais
    top_pct = top_row / total_v
    bottom_pct = bottom_row / total_v
    left_pct = left_col / total_h
    right_pct = right_col / total_h
    
    # Lógica: onde tem MAIS pixels, a seta APONTA
    diff_vertical = abs(top_pct - bottom_pct)
    diff_horizontal = abs(left_pct - right_pct)
    
    # Ajusta threshold baseado no aspecto ratio
    # Se a seta é mais alta que larga, favorece vertical
    aspect_ratio = w / h if h > 0 else 1
    if aspect_ratio < 0.7:  # Setas mais altas
        vertical_adjusted = diff_vertical * 2  # Aumenta margem para vertical
    else:
        vertical_adjusted = diff_vertical * 1.1
    
    # Determina qual eixo tem maior diferença
    if vertical_adjusted > diff_horizontal:
        # Decisão vertical
        if top_pct > bottom_pct:
            return 'CIMA'
        else:
            return 'BAIXO'
    else:
        # Decisão horizontal
        if left_pct > right_pct:
            return 'ESQUERDA'
        else:
            return 'DIREITA'

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=== Reconhecedor de Setas HUD (12 setas centrais) ===\n")
    
    image_path = input("Digite o caminho da imagem: ").strip()
    
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo não encontrado: {image_path}")
    else:
        print("\n--- Detectando setas ---\n")
        directions = detect_arrows_hud(image_path)
        
        if directions:
            print(f"\n{'='*60}")
            print(f"Total de setas detectadas: {len(directions)}\n")
            print("Sequência de setas (DIREITA, BAIXO, BAIXO, CIMA, ...):")
            for i, direction in enumerate(directions, 1):
                print(f"  {i:2d}. {direction}")
            print(f"\nInput das direções:\n{' -> '.join(directions)}")
            print('='*60)
        else:
            print("Nenhuma seta foi detectada!")