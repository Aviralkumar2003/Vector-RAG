from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            print(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model {self.model_name} loaded successfully. Embedding dimension: {self.model.get_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not loaded. Cannot generate embeddings.")
        try:
            print(f"Generating embeddings for {len(texts)} texts.")
            embeddings = self.model.encode(texts, show_progress_bar=True)
            print(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise

   