from pyannote.audio.pipelines import PretrainedSpeakerEmbedding
import torch
from scipy.spatial.distance import cosine

class AudioComparator:
    def __init__(self, model_name="pyannote/embedding", similarity_threshold=0.75):
        """
        Inicializa el modelo de embeddings de audio.
        :param model_name: Nombre del modelo preentrenado en Hugging Face.
        :param similarity_threshold: Valor mínimo para considerar un audio como similar.
        """
        self.model = PretrainedSpeakerEmbedding(model_name, device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.audio_embeddings = {}  # Diccionario para almacenar embeddings de audios entrenados
        self.similarity_threshold = similarity_threshold  # Umbral de similitud

    def extract_embedding(self, file_path):
        """Extrae el embedding del audio."""
        return self.model(file_path)

    def train(self, audio_files):
        """Guarda los embeddings de una lista de archivos de audio."""
        for file in audio_files:
            self.audio_embeddings[file] = self.extract_embedding(file)
        print(f"Entrenado con {len(audio_files)} audios.")

    def compare(self, new_audio):
        """Compara un nuevo audio con los entrenados y devuelve si es similar o no."""
        new_embedding = self.extract_embedding(new_audio)
        similarities = {}

        for file, emb in self.audio_embeddings.items():
            sim = 1 - cosine(new_embedding, emb)  # Distancia coseno (1 = idéntico, 0 = diferente)
            similarities[file] = sim

        # Obtener la similitud más alta
        best_match, best_score = max(similarities.items(), key=lambda x: x[1])

        # Decisión final
        is_similar = best_score >= self.similarity_threshold
        result = {
            "new_audio": new_audio,
            "most_similar_audio": best_match,
            "similarity_score": round(best_score, 2),
            "is_similar": is_similar
        }
        return result

# 🔹 **Ejemplo de uso**
if __name__ == "__main__":
    # ======= Ejemplo de uso =======
    audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]  # Audios de referencia
    comparator = AudioComparator(similarity_threshold=0.80)  # Ajusta el umbral de similitud
    comparator.train(audio_files)

    new_audio = "test.wav"
    result = comparator.compare(new_audio)

    # Mostrar resultado
    if result["is_similar"]:
        print(f"✅ El audio {result['new_audio']} es similar a {result['most_similar_audio']} con {result['similarity_score'] * 100:.2f}% de similitud.")
    else:
        print(f"❌ El audio {result['new_audio']} NO es similar a ninguno de los audios entrenados.")
