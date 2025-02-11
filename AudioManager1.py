import sounddevice as sd
import numpy as np
import time

class AudioManager1:
    """
    Captura el audio directamente del sistema y detecta picos de volumen.
    """
    def __init__(self, max_volume, sample_rate=44100, channels=2, device=None):
        """
        :param max_volume: Umbral de volumen para detectar un evento.
        :param sample_rate: Frecuencia de muestreo en Hz.
        :param channels: Número de canales (2 para estéreo).
        :param device: Nombre o índice del dispositivo de audio.
        """
        self.max_volume = max_volume
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device or self.get_loopback_device()
        self.is_listening = False

    def get_loopback_device(self):
        """Encuentra un dispositivo compatible con loopback."""
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if "loopback" in d["name"].lower():  # Busca dispositivos con loopback
                return i
        raise RuntimeError("No se encontró un dispositivo con loopback. Usa un software como VB-Audio o VoiceMeeter.")

    def check_volume(self):
        """Captura audio del sistema y detecta si supera el umbral."""
        duration = 0.1  # Tiempo de captura en segundos
        audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
                            channels=self.channels, device=self.device, dtype=np.float32)
        sd.wait()

        rms = np.sqrt(np.mean(audio_data**2)) * 1000  # Normaliza volumen
        print(f"Volumen detectado: {rms}")
        return rms > self.max_volume

    def start_listening(self, callback):
        """Inicia la escucha del audio del sistema en un bucle continuo."""
        self.is_listening = True
        while self.is_listening:
            if self.check_volume():
                callback()  # Llama al callback cuando se detecta un sonido fuerte
            time.sleep(0.1)

    def stop_listening(self):
        """Detiene la escucha de audio."""
        print("Deteniendo escucha de audio")
        self.is_listening = False

# 🔹 Ejemplo de uso
if __name__ == "__main__":
    def on_sound_detected():
        print("🎵 Sonido detectado!")

    audio_manager = AudioManager1(max_volume=5)
    audio_manager.start_listening(on_sound_detected)
