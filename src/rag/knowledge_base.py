import logging
from typing import List, Dict, Optional, Any
from src.utils.config import get_config

logger = logging.getLogger("badminton_cv.rag")

class KnowledgeBase:
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the KnowledgeBase.
        """
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        self.documents = [] # List of {'text': str, 'metadata': dict}
        
        # Try to load sentence transformer for embeddings
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.has_encoder = True
            logger.info("SentenceTransformer loaded for semantic search.")
        except ImportError:
            self.has_encoder = False
            logger.warning("SentenceTransformer not found. Using keyword search.")
        except Exception as e:
             self.has_encoder = False
             logger.warning(f"Failed to load encoder: {e}. Using keyword search.")

    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base."""
        doc = {'text': text, 'metadata': metadata or {}}
        if self.has_encoder:
            doc['embedding'] = self.encoder.encode(text)
        self.documents.append(doc)

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents."""
        if not self.documents:
            return []

        if self.has_encoder:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            query_emb = self.encoder.encode(query_text).reshape(1, -1)
            doc_embs = np.array([d['embedding'] for d in self.documents])
            
            scores = cosine_similarity(query_emb, doc_embs)[0]
            top_k_indices = scores.argsort()[-n_results:][::-1]
            
            return [self.documents[i] for i in top_k_indices]
            
        else:
            # Simple keyword matching fallback
            scored_docs = []
            query_words = set(query_text.lower().split())
            
            for doc in self.documents:
                score = sum(1 for w in query_words if w in doc['text'].lower())
                scored_docs.append((score, doc))
                
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            return [d[1] for d in scored_docs[:n_results] if d[0] > 0]
