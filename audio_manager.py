import sounddevice as sd
import numpy as np
import soundfile as sf
import time
import os
from datetime import datetime
from scipy.signal import correlate

class AudioManager:
    """
    Clase para manejar la captura de audio y la detección de volumen utilizando sounddevice.
    """
    def __init__(self, max_volume, sample_rate=44100, channels=2,
                 match_threshold=0.7):
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
        self.match_threshold = match_threshold

        # Cargar audio de referencia
        self.reference_audio, self.ref_sample_rate = sf.read("./audios/blob.wav")
        if self.ref_sample_rate != self.sample_rate:
            raise ValueError(f"La tasa de muestreo del audio de referencia ({self.ref_sample_rate} Hz) no coincide con {self.sample_rate} Hz.")
          # 🔹 Definir muestras de referencia directamente en el código
        self.reference_samples = self.load_samples("./audios/")

    def load_samples(self, samples_path):
        """
        Carga archivos de audio de la carpeta de muestras y los almacena en un diccionario.
        """
        samples = {}
        if not os.path.exists(samples_path):
            raise FileNotFoundError(f"La carpeta '{samples_path}' no existe.")

        for file in os.listdir(samples_path):
            if file.endswith(".wav"):
                file_path = os.path.join(samples_path, file)
                audio, rate = sf.read(file_path)
                if rate != self.sample_rate:
                    print(f"⚠️ Advertencia: {file} tiene una tasa de muestreo diferente ({rate} Hz), se ajustará automáticamente.")
                    audio = self.resample_audio(audio, rate)
                samples[file] = self.normalize_audio(audio)
                print(f"✅ Muestra cargada: {file}")

        if not samples:
            raise ValueError("No se encontraron archivos .wav en la carpeta de muestras.")

        return samples    



    def check_volume_and_match(self):
        """
        Captura audio y devuelve True si el volumen supera el umbral definido.
        """
        audio_data=None
        #duration = 0.1  # Duración de la captura en segundos
        duration = len(self.reference_audio) / self.sample_rate
        audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, dtype='float32')
        sd.wait()  

        # Calcular volumen RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        rms= rms*1000000

        if rms < self.max_volume:
            return False  # Ignorar sonidos débiles
        
        """ Guardar el sonido fuerte en un archivo .wav con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./sound_{timestamp}.wav"
        sf.write(filename, audio_data, self.sample_rate)
        print(f"💾 Sonido fuerte guardado en: {filename}")"""

        # Comparar con cada muestra en la matriz de referencia
        for sample_name, reference_audio in self.reference_samples.items():
            similarity = self.compute_similarity(audio_data, reference_audio)
            print(f"🔍 Comparación con {sample_name}: {similarity:.3f} (Umbral: {self.match_threshold})")

            if similarity >= self.match_threshold:
                print(f"✅ Coincidencia detectada con {sample_name}")
                return True  # Detener la búsqueda tras la primera coincidencia

       # if rms>2000 : 
            #print(f"Sonido puro:{rms_pure}")
        #    print(f"Sonido aumentado:{rms}")
         #   print(f"max_volume:{self.max_volume}")
          #  print(f"check volumen:{rms > self.max_volume}")
        # Compara el volumen con el umbral
 
        return False # No se encontró ninguna coincidencia

    def start_listening(self, callback):
        """
        Inicia el escaneo continuo del sonido y llama al callback cuando se detecta un sonido fuerte.
        """
        self.is_listening = True
        while self.is_listening:
            if self.check_volume_and_match():
                callback() # Llama al callback cuando se detecta un sonido fuerte
                self.is_listening = False #Tratamos de detener el listening
            time.sleep(0.1)  # Esperar un poco antes de volver a escanear

    def stop_listening(self):
        """
        Detiene el escaneo continuo del sonido.
        """
        print("Deteniendo listener de audio")
        self.is_listening = False



    def normalize_audio(self, audio):
        """Normaliza el audio a un rango de -1 a 1 y lo convierte a mono si es necesario."""
        if len(audio.shape) > 1:  # Convertir a mono si tiene múltiples canales
            audio = np.mean(audio, axis=1)
        return audio / np.max(np.abs(audio))  # Normalizar

    def compute_similarity(self, recorded_audio, reference_audio):
        """Usa correlación cruzada para medir la similitud entre señales."""
        recorded_audio = self.normalize_audio(recorded_audio)
        reference_audio = self.normalize_audio(reference_audio)

        # Ajustar longitudes
        min_len = min(len(recorded_audio), len(reference_audio))
        recorded_audio = recorded_audio[:min_len]
        reference_audio = reference_audio[:min_len]

        # Aplicar una ventana de Hann para reducir efectos de borde
        window = np.hanning(min_len)
        recorded_audio *= window
        reference_audio *= window

        # Calcular la correlación cruzada normalizada
        correlation = correlate(recorded_audio, reference_audio)
        correlation /= np.max(correlation)  # Normalización

        max_correlation = np.max(correlation)  # Buscar el pico de coincidencia
        return max_correlation
    

# 🔹 **Ejemplo de uso**
if __name__ == "__main__":
    def on_sound_match():
        print("🎵 Sonido fuerte detectado y coincide con la muestra!")

    audio_manager = AudioManager(max_volume=3000)
    audio_manager.start_listening(on_sound_match)        
    