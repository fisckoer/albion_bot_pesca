import sounddevice as sd
import numpy as np
import time

class AudioManager:
    """
    Clase para manejar la captura de audio y la detección de volumen utilizando sounddevice.
    """
    def __init__(self, max_volume, sample_rate=44100, channels=2):
        """
        Inicializa el AudioManager.
        
        :param max_volume: Umbral de volumen para detectar un evento.
        :param sample_rate: Tasa de muestreo del audio (por defecto 44100 Hz).
        :param channels: Número de canales de audio (por defecto 2, estéreo).
        """
        self.max_volume = max_volume
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.is_listening = False

    def check_volume(self):
        """
        Captura audio y devuelve True si el volumen supera el umbral definido.
        """
        #print(sd.query_devices())

        # Especifica el índice del dispositivo de entrada (VB-Cable)
        input_device_index = 5 

        audio_data=None
        duration = 0.1  # Duración de la captura en segundos
        audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels)
        #audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
         #                   channels=self.channels, dtype='float32', device=input_device_index)
        sd.wait()  # Espera a que la captura termine

        # Calcula el volumen RMS (Root Mean Square)
        rms_pure = np.sqrt(np.mean(np.square(audio_data)))
        rms= rms_pure*1000000
        if rms>15000 : 
            print(f"Sonido puro:{rms_pure}")
            print(f"Sonido aumentado:{rms}")
            print(f"max_volume:{self.max_volume}")
            print(f"check volumen:{rms > self.max_volume}")
        # Compara el volumen con el umbral
 
        return rms > self.max_volume

    def start_listening(self, callback):
        """
        Inicia el escaneo continuo del sonido y llama al callback cuando se detecta un sonido fuerte.
        """
        self.is_listening = True
        while self.is_listening:
            if self.check_volume():
                callback() # Llama al callback cuando se detecta un sonido fuerte
                self.is_listening = False #Tratamos de detener el listening
            time.sleep(0.1)  # Esperar un poco antes de volver a escanear

    def stop_listening(self):
        """
        Detiene el escaneo continuo del sonido.
        """
        print("Deteniendo listener de audio")
        self.is_listening = False