import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        # Try to import pinecone, fall back gracefully if not available
        try:
            import pinecone
            self.pinecone = pinecone
            self.PINECONE_AVAILABLE = True
        except ImportError:
            self.pinecone = None
            self.PINECONE_AVAILABLE = False
            logger.warning("Pinecone not available, using in-memory vector store only")
        
        # Initialize Pinecone
        if settings.pinecone_api_key and self.PINECONE_AVAILABLE:
            try:
                # Use the new Pinecone initialization
                self.pinecone_client = self.pinecone.Pinecone(
                    api_key=settings.pinecone_api_key
                )
                self._setup_index()
            except Exception as e:
                logger.warning(f"Pinecone initialization failed: {str(e)}")
                logger.info("Falling back to in-memory vector store")
                self.use_pinecone = False
        else:
            logger.info("No Pinecone API key provided or Pinecone not available, using in-memory vector store")
            self.use_pinecone = False
        
        # In-memory storage as fallback
        self.in_memory_vectors = {}
        self.in_memory_embeddings = {}
    
    def _setup_index(self):
        """Setup Pinecone index"""
        try:
            index_name = settings.pinecone_index_name
            
            # Check if index exists
            if index_name not in self.pinecone_client.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=self.dimension,
                    metric='cosine'
                )
            
            # Connect to index
            self.index = self.pinecone_client.Index(index_name)
            self.use_pinecone = True
            logger.info(f"Successfully connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {str(e)}")
            self.use_pinecone = False
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def store_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Store document chunks in vector database"""
        try:
            if not chunks:
                logger.warning("No chunks to store")
                return False
            
            # Extract texts for embedding
            texts = [chunk['content'] for chunk in chunks]
            chunk_ids = [chunk['id'] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.get_embeddings(texts)
            
            if self.use_pinecone and self.index:
                # Store in Pinecone
                vectors_to_upsert = []
                for i, (chunk_id, embedding, chunk) in enumerate(zip(chunk_ids, embeddings, chunks)):
                    vector_data = {
                        'id': chunk_id,
                        'values': embedding,
                        'metadata': {
                            'content': chunk['content'][:1000],  # Limit metadata size
                            'document_url': chunk['document_url'],
                            'chunk_index': chunk['chunk_index'],
                            'token_count': chunk['token_count']
                        }
                    }
                    vectors_to_upsert.append(vector_data)
                
                # Upsert in batches
                batch_size = 100
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                
                logger.info(f"Successfully stored {len(chunks)} chunks in Pinecone")
                
            else:
                # Store in memory
                for i, (chunk_id, embedding, chunk) in enumerate(zip(chunk_ids, embeddings, chunks)):
                    self.in_memory_vectors[chunk_id] = embedding
                    self.in_memory_embeddings[chunk_id] = chunk
                
                logger.info(f"Successfully stored {len(chunks)} chunks in memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks"""
        try:
            # Generate query embedding
            query_embedding = self.get_embeddings([query])[0]
            
            if self.use_pinecone and self.index:
                # Search in Pinecone
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                # Format results
                chunks = []
                for match in results.matches:
                    chunk_data = {
                        'id': match.id,
                        'content': match.metadata.get('content', ''),
                        'score': match.score,
                        'metadata': match.metadata
                    }
                    chunks.append(chunk_data)
                
            else:
                # Search in memory
                chunks = self._search_in_memory(query_embedding, top_k)
            
            # Sort by score (highest first)
            chunks.sort(key=lambda x: x['score'], reverse=True)
            
            # Filter by similarity threshold
            filtered_chunks = [
                chunk for chunk in chunks 
                if chunk['score'] >= settings.similarity_threshold
            ]
            
            logger.info(f"Found {len(filtered_chunks)} relevant chunks for query")
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def _search_in_memory(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in in-memory vectors"""
        if not self.in_memory_vectors:
            return []
        
        # Calculate cosine similarities
        similarities = []
        for chunk_id, vector in self.in_memory_vectors.items():
            similarity = self._cosine_similarity(query_embedding, vector)
            similarities.append((chunk_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k results
        results = []
        for chunk_id, score in similarities[:top_k]:
            chunk_data = self.in_memory_embeddings[chunk_id]
            results.append({
                'id': chunk_id,
                'content': chunk_data['content'],
                'score': score,
                'metadata': chunk_data['metadata']
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def clear_index(self):
        """Clear all stored vectors"""
        try:
            if self.use_pinecone and self.index:
                self.index.delete(delete_all=True)
                logger.info("Cleared Pinecone index")
            else:
                self.in_memory_vectors.clear()
                self.in_memory_embeddings.clear()
                logger.info("Cleared in-memory vectors")
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            if self.use_pinecone and self.index:
                stats = self.index.describe_index_stats()
                return {
                    'total_vectors': stats.total_vector_count,
                    'dimension': stats.dimension,
                    'index_type': 'pinecone'
                }
            else:
                return {
                    'total_vectors': len(self.in_memory_vectors),
                    'dimension': self.dimension,
                    'index_type': 'memory'
                }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {'error': str(e)} 