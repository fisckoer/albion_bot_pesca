import pyautogui
import random
import time
import threading

class FishingBot:
    """
    Clase principal del bot de pesca.
    Maneja el lanzamiento del anzuelo y la resolución del minijuego.
    """
    def __init__(self, bot_config_manager, audio_manager, image_detection, log_callback=None, coords=None):
        self.bot_config_manager = bot_config_manager
        self.state = "IDLE"
        self.log_callback = log_callback
        self.coords = coords
        self.audio_manager = audio_manager
        self.image_detection = image_detection
        self.listening_thread = None

    def cast_hook(self):
        """
        Lanza el anzuelo y espera la activación del minijuego por detección de sonido.
        """
        self.listening_thread = None
        while True:
            print(f"STATUS: {self.state}")
            if self.state in ["CASTING", "STARTED"]:
                if not self.coords:
                    if self.log_callback:
                        self.log_callback("No fishing spots defined. Please set fishing spots first.")
                    time.sleep(2)
                    self.log_callback("Bot pause")
                    self.state = "IDLE"
                    continue

                time.sleep(2.6)
                pyautogui.mouseUp()
                x, y = self.get_new_spot()
                pyautogui.moveTo(x, y, duration=0.2)
                time.sleep(0.2)
                pyautogui.mouseDown()
                time.sleep(random.uniform(0.4, 0.8))
                pyautogui.mouseUp()

                if self.log_callback:
                    self.log_callback(f"Casted towards: {x, y}")

                time.sleep(2.5)

                # Iniciar la detección de sonido en un hilo separado
                self.listening_thread = threading.Thread(target=self.audio_manager.start_listening, args=(self.validateFish,))
                self.listening_thread.start()

                self.state = "CAST"
                
            elif self.state == "CAST":
                count = 0
                while self.state != "SOLVING":
                    time.sleep(1)
                    count += 1
                    if count > 30:
                        break
                if self.state == "CAST":
                    if self.log_callback:
                        self.log_callback("No encuentras nada, Recuperando ...")
                    self.state = "CASTING"
                    self.audio_manager.stop_listening()
                    pyautogui.mouseDown()
                    time.sleep(0.1)
                    pyautogui.mouseUp()
                    time.sleep(1)
                    self.cast_hook()
            elif self.state == "STOPPED":
                self.audio_manager.stop_listening()
                if self.listening_thread:
                    self.listening_thread.join()
                break
            elif self.state == "SOLVING":
                self.do_minigame()
                self.state = "CASTING"
                time.sleep(1.5)
            else:
                time.sleep(1)

    def get_new_spot(self):
        """
        Devuelve una posición aleatoria dentro de las coordenadas definidas.
        """
        return random.choice(self.coords)

    def validateFish(self):
        """
        Se activa cuando se detecta un sonido fuerte (indica que un pez ha mordido).
        """
        if self.state == "CAST":
            self.state = "SOLVING"
            self.do_minigame()

    def do_minigame(self):
        """
        Resuelve el minijuego de pesca detectando y siguiendo el flotador.
        """
        if self.state != "SOLVING":
            return

        self.audio_manager.stop_listening()

        if self.log_callback:
            self.log_callback("Attempting Minigame")

        pyautogui.mouseDown()
        pyautogui.mouseUp()
        print("do_minigame")
        #time.sleep(0.5)

        valid, location, size = self.image_detection.detect_bobber()
        if valid:
            print("valid")
            if self.log_callback:
                self.log_callback("Bobber detected. Solving minigame...")

            while self.state == "SOLVING":
                print("pescando ....")
                valid, location, size = self.image_detection.detect_bobber()
                print("pescando ....")
                print(f"valid  {valid}, location  {location}, size {size}")
                if valid:
                    if location[0] < size / 2:
                        pyautogui.mouseDown()
                    else:
                        pyautogui.mouseUp()
                else:
                    self.state = "CASTING"
                    print("Termino la pesca ....")
                    #time.sleep(1)
                    pyautogui.mouseUp()
                    break
        else:
            self.state = "CASTING"
            if self.log_callback:
                self.log_callback("Bobber not found. Recasting...")
