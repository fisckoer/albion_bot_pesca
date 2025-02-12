import pyautogui
import time


class MiniGameSolver:
    """
    Clase encargada de resolver el minijuego de pesca.
    """
    def __init__(self, image_detection, log_callback=None):
        self.image_detection = image_detection
        self.log_callback = log_callback
        self.status ="START"
    
    def solve(self):
        """
        Resuelve el minijuego detectando y siguiendo el flotador.
        """
        while self.status=="START":
            print(f"✅ esperando minijuego")
            if self.log_callback:
                self.log_callback("Attempting Minigame")

            valid, location, size = self.image_detection.detect_bobber()
            if valid:
                print("valid")
                print("pescando ....")
                if self.log_callback:
                    self.log_callback("Bobber detected. Solving minigame...")

                while True:
                    valid, location, size = self.image_detection.detect_bobber()
                    if valid:
                        if location[0] < size / 2:
                            pyautogui.mouseDown()
                        else:
                            pyautogui.mouseUp()
                    else:
                        print("Termino la pesca ....")
                        pyautogui.mouseUp()
                        break
            else:
                time.sleep(0.5)
                """
                print("Bobber not found. Recasting...")
                pyautogui.mouseUp()
                if self.log_callback:
                    self.log_callback("Bobber not found. Recasting...")"""
            
