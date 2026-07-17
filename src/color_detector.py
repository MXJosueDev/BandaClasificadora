import cv2
import numpy as np

class ColorDetector:
    def __init__(self, min_pixels=30):
        self.min_pixels = min_pixels
        
        # Rangos HSV 
        self.rangos = {
            "rojo": [
                (np.array([0, 70, 50]), np.array([10, 255, 255])),
                (np.array([170, 70, 50]), np.array([180, 255, 255]))
            ],
            "verde": [
                (np.array([40, 70, 50]), np.array([85, 255, 255]))
            ],
            "azul": [
                (np.array([90, 70, 50]), np.array([130, 255, 255]))
            ]
        }

    def detect(self, roi):
        """Analiza la imagen recortada (roi) y devuelve el color predominante."""
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        pixeles_por_color = {}

        # Evaluar cada color dinámicamente
        for color, limites in self.rangos.items():
            mask_total = None
            for bajo, alto in limites:
                mask = cv2.inRange(hsv, bajo, alto)
                if mask_total is None:
                    mask_total = mask
                else:
                    mask_total = cv2.bitwise_or(mask_total, mask)
            
            pixeles_por_color[color] = cv2.countNonZero(mask_total)

        # Encontrar el color con más píxeles
        color_predominante = max(pixeles_por_color, key=pixeles_por_color.get)
        
        # Validar contra el umbral mínimo
        if pixeles_por_color[color_predominante] > self.min_pixels: 
            return color_predominante
        
        return "desconocido"