import cv2
import numpy as np

class PanelDetector:
    def __init__(self, min_area=500):
        self.min_area = min_area

    def detect_panels(self, image_path):
        # Read the image
        image = cv2.imread(image_path)
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # Use Canny edge detection
        edges = cv2.Canny(blur, 30, 150)
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        panels = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                panels.append((x, y, w, h))
                
        return panels

# Example usage (uncomment to use):
# detector = PanelDetector(min_area=500)
# panel_coords = detector.detect_panels('path_to_image.jpg')
# print(panel_coords)