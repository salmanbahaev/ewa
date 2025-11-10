"""Embeddings and semantic search for products"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from loguru import logger
import config


class EmbeddingsSearch:
    """Semantic search using OpenAI embeddings"""
    
    def __init__(self):
        """Initialize embeddings search"""
        # Если нужен прокси - раскомментируй следующие строки:
        # import httpx
        # http_client = httpx.Client(proxy="http://your-proxy:port")
        # self.client = OpenAI(api_key=config.OPENAI_API_KEY, http_client=http_client)
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.embeddings_cache_path = Path("data/embeddings_cache.json")
        self.catalog: List[Dict] = []
        self.embeddings: np.ndarray = None
        self.embedding_model = "text-embedding-3-small"  # Cheap and good
        
    async def initialize(self, catalog: List[Dict]):
        """
        Initialize embeddings index from catalog.
        
        Args:
            catalog: List of product dictionaries
        """
        self.catalog = catalog
        logger.info(f"Initializing embeddings for {len(catalog)} products")
        
        # Try to load cached embeddings
        if self._load_cached_embeddings():
            logger.info("Loaded embeddings from cache")
            return
        
        # Generate new embeddings
        logger.info("Generating new embeddings (this may take a minute)...")
        await self._generate_embeddings()
        self._save_embeddings_cache()
        logger.info("Embeddings generated and cached")
    
    def _load_cached_embeddings(self) -> bool:
        """
        Load embeddings from cache if available and valid.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.embeddings_cache_path.exists():
            return False
        
        try:
            with open(self.embeddings_cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verify cache is for current catalog
            if len(cache_data['product_ids']) != len(self.catalog):
                logger.warning("Cache size mismatch, regenerating embeddings")
                return False
            
            # Check if product IDs match
            current_ids = [p.get('id') for p in self.catalog]
            if cache_data['product_ids'] != current_ids:
                logger.warning("Product IDs changed, regenerating embeddings")
                return False
            
            # Load embeddings
            self.embeddings = np.array(cache_data['embeddings'])
            return True
            
        except Exception as e:
            logger.error(f"Error loading embeddings cache: {e}")
            return False
    
    def _save_embeddings_cache(self):
        """Save embeddings to cache"""
        try:
            cache_data = {
                'product_ids': [p.get('id') for p in self.catalog],
                'embeddings': self.embeddings.tolist(),
                'model': self.embedding_model
            }
            
            with open(self.embeddings_cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Embeddings cached to {self.embeddings_cache_path}")
            
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {e}")
    
    async def _generate_embeddings(self):
        """Generate embeddings for all products"""
        texts = []
        for product in self.catalog:
            # Combine ALL relevant fields for maximum context
            text_parts = [
                f"Название: {product.get('name', '')}",
                f"Категория: {product.get('category', '')}",
                f"Теги: {' '.join(product.get('tags', []))}",  # ALL tags
                f"Описание: {product.get('description', '')}"  # Full description
            ]
            text = ' '.join(filter(None, text_parts))
            texts.append(text)
        
        # Generate embeddings in batch
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings_list = [item.embedding for item in response.data]
            self.embeddings = np.array(embeddings_list)
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Get embedding for search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            )
            return np.array(response.data[0].embedding)
            
        except Exception as e:
            logger.error(f"Error getting query embedding: {e}")
            raise
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search products using semantic similarity.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching products sorted by relevance
        """
        if self.embeddings is None:
            logger.error("Embeddings not initialized!")
            return []
        
        # Get query embedding
        query_embedding = self._get_query_embedding(query)
        
        # Calculate similarities with all products
        similarities = []
        for i, product_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, product_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results with minimum score threshold
        MIN_SCORE_THRESHOLD = 0.25  # Filter out very low relevance results
        
        results = []
        for idx, score in similarities[:max_results * 2]:  # Get more candidates
            if score < MIN_SCORE_THRESHOLD:
                continue
            product = self.catalog[idx].copy()
            product['_similarity_score'] = float(score)
            results.append(product)
            if len(results) >= max_results:
                break
        
        logger.info(f"Semantic search for '{query}': found {len(results)} results")
        if results:
            logger.debug(f"Top result: {results[0].get('name')} (score: {results[0]['_similarity_score']:.3f})")
        
        return results


# Global instance
_embeddings_search: Optional[EmbeddingsSearch] = None


async def initialize_embeddings_search(catalog: List[Dict]):
    """
    Initialize global embeddings search instance.
    
    Args:
        catalog: Product catalog
    """
    global _embeddings_search
    _embeddings_search = EmbeddingsSearch()
    await _embeddings_search.initialize(catalog)


def get_embeddings_search() -> EmbeddingsSearch:
    """
    Get global embeddings search instance.
    
    Returns:
        EmbeddingsSearch instance
    """
    if _embeddings_search is None:
        raise RuntimeError("Embeddings search not initialized! Call initialize_embeddings_search() first")
    return _embeddings_search

