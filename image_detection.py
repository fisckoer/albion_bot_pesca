import cv2
import numpy as np
import mss
import time

class ImageDetection:
    """
    Clase para detectar el flotador en la pantalla utilizando OpenCV.
    """
    def __init__(self, screen_area):
        self.screen_area = screen_area

    def detect_bobber(self):
        """
        Detecta el flotador en la zona de la pantalla definida.
        Devuelve si el flotador fue detectado y su posición.
        """
        with mss.mss() as sct:
            base = np.array(sct.grab(self.screen_area))
            base = np.flip(base[:, :, :3], 2)
            base = cv2.cvtColor(base, cv2.COLOR_RGB2BGR)
            bobber = cv2.imread('bobber.png')
            bobber = np.array(bobber, dtype=np.uint8)
            bobber = np.flip(bobber[:, :, :3], 2)
            bobber = cv2.cvtColor(bobber, cv2.COLOR_RGB2BGR)
            result = cv2.matchTemplate(base, bobber, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.55:
                return True, max_loc, base.shape[1]
            else:
                return False, max_loc, base.shape[1]