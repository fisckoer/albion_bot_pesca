import pyautogui
import random
import time
import threading

class FishingBot:
    """
    Clase principal del bot de pesca.
    Maneja el lanzamiento del anzuelo y la resolución del minijuego.
    """
    def __init__(self, bot_config_manager,audio_manager,image_detection, log_callback=None,coords=None,):
        self.bot_config_manager = bot_config_manager  # Referencia a BotConfigManager
        self.state = "IDLE"   # Estado actual del bot
        self.log_callback = log_callback  # Callback para registrar mensajes en la GUI
        self.coords = coords
        self.audio_manager = audio_manager  # Referencia a AudioManager
        self.image_detection = image_detection
    def cast_hook(self):
        """
        Lanza el anzuelo a una posición aleatoria dentro de las coordenadas definidas.
        Si no hay coordenadas, muestra un mensaje en el log.
        """
        self.listening_thread = None
        while True:
            print(f"STATUS:{self.state}")
            if self.state == "CASTING" or self.state == "STARTED":
                if not self.coords:  # Validar si hay coordenadas
                    if self.log_callback:
                        self.log_callback("No fishing spots defined. Please set fishing spots first.")
                    time.sleep(2)  # Esperar antes de volver a intentar
                    self.log_callback("Bot pause")
                    self.state="IDLE"
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
                self.listening_thread = threading.Thread(target=self.audio_manager.start_listening, args=(self.validateFish,))
                self.listening_thread.start() 
                self.state = "CAST"
                
            elif self.state == "CAST":
                count = 0
                while self.state !="SOLVING":
                    time.sleep(1)
                    count=count+1
                    if count>24:
                        break
                if self.state == "CAST":
                    if self.log_callback:
                        self.log_callback("Seems to be stuck on cast. Recasting.")
                    self.state = "CASTING"
                    self.audio_manager.stop_listening()
                    pyautogui.mouseDown()
                    time.sleep(0.1)
                    pyautogui.mouseUp()
                    time.sleep(1)
                    self.cast_hook()
            elif self.state == "STOPPED":
                self.audio_manager.stop_listening()
                self.listening_thread.join()
                break
            elif self.state == "SOLVING":
                self.do_minigame()
                time.sleep(25)
                self.state = "CASTING"    
            else:
                time.sleep(1)  # Esperar si el bot no está en estado de lanzar

    def get_new_spot(self):
        """
        Devuelve una posición aleatoria dentro de las coordenadas definidas.
        """
        return random.choice(self.coords)

    def validateFish(self):
        self.state = "SOLVING"
        

    def do_minigame(self):
        """
        Resuelve el minijuego de pesca detectando y siguiendo el flotador.
        """
        if self.state != "CASTING" and self.state != "STARTED":
            self.audio_manager.stop_listening()
            #self.state = "SOLVING"
            if self.log_callback:
                self.log_callback("Attempting Minigame")

            pyautogui.mouseDown()
            pyautogui.mouseUp()

            # Esperar a que aparezca el flotador
            time.sleep(0.5)

            # Detectar el flotador
            valid, location, size = self.image_detection.detect_bobber()
            if valid:
                if self.log_callback:
                    self.log_callback("Bobber detected. Solving minigame...")
                    print("Bobber detected. Solving minigame...")

                while True:
                    valid, location, size = self.image_detection.detect_bobber()
                    if valid:
                        if location[0] < size / 2:
                            pyautogui.mouseDown()
                        else:
                            pyautogui.mouseUp()
                    else:
                        if self.state != "CASTING":
                            self.state = "CASTING"
                           
                            time.sleep(1)
                            pyautogui.mouseUp()
                            break
            else:
                self.state = "CASTING"
                time.sleep(0.5)
                if self.log_callback:
                    print("Bobber not found. Recasting...")
                    self.log_callback("Bobber not found. Recasting...")  