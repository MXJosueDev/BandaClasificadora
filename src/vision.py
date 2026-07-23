import cv2

class MotionDetector:
    def __init__(self, min_area=3000):
        self.backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)
        self.min_area = min_area

    def detect(self, frame):
        """Procesa el frame y retorna si hay movimiento, el bounding box y el centro."""
        fgMask = self.backSub.apply(frame)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = None
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area and area > max_area:
                max_area = area
                largest_contour = contour

        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            centro_x = x + (w // 2)
            centro_y = y + (h // 2)
            return True, (x, y, w, h), centro_x, centro_y
            
        return False, None, None, None

    @staticmethod
    def get_roi(frame, bbox, padding=15):
        """Extrae la región de interés (ROI) con un padding de seguridad."""
        x, y, w, h = bbox
        y1 = max(0, y - padding)
        y2 = min(frame.shape[0], y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(frame.shape[1], x + w + padding)
        
        return frame[y1:y2, x1:x2], (x1, y1, x2, y2)