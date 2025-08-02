import numpy as np
import pickle
import logging
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import os
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    
class LightweightVectorStore:
    """Lightweight vector store using scikit-learn instead of FAISS"""
    
    def __init__(self, max_features: int = 1000):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.chunks = []
        self.chunk_metadata = []
        self.document_vectors = None
        self.vectorizer_fitted = False
        
    def add_documents(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to vector store"""
        try:
            if not chunks:
                return False
            
            logger.info(f"Adding {len(chunks)} documents to lightweight vector store")
            
            # Extract texts for vectorization
            texts = [chunk.content for chunk in chunks]
            
            # Fit vectorizer and transform texts
            if not self.vectorizer_fitted:
                self.document_vectors = self.vectorizer.fit_transform(texts)
                self.vectorizer_fitted = True
            else:
                # Transform new texts using existing vectorizer
                new_vectors = self.vectorizer.transform(texts)
                if self.document_vectors is not None:
                    # Stack with existing vectors
                    from scipy.sparse import vstack
                    self.document_vectors = vstack([self.document_vectors, new_vectors])
                else:
                    self.document_vectors = new_vectors
            
            # Store chunks and metadata
            for chunk in chunks:
                self.chunks.append(chunk)
                self.chunk_metadata.append({
                    'id': chunk.id,
                    'metadata': chunk.metadata,
                    'content_preview': chunk.content[:200]
                })
            
            logger.info(f"Successfully added {len(chunks)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar documents"""
        try:
            if not self.vectorizer_fitted or len(self.chunks) == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Transform query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.document_vectors)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    score = similarities[idx]
                    results.append((chunk, float(score)))
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def semantic_search_with_metadata(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Enhanced search with metadata and scoring"""
        results = self.search(query, top_k)
        
        enhanced_results = []
        for chunk, similarity_score in results:
            result = {
                'chunk_id': chunk.id,
                'content': chunk.content,
                'similarity_score': similarity_score,
                'metadata': chunk.metadata,
                'relevance_explanation': self._explain_relevance(query, chunk, similarity_score)
            }
            enhanced_results.append(result)
        
        return enhanced_results
    
    def _explain_relevance(self, query: str, chunk: DocumentChunk, score: float) -> str:
        """Provide explanation for why chunk is relevant"""
        query_words = set(query.lower().split())
        chunk_words = set(chunk.content.lower().split())
        
        common_words = query_words & chunk_words
        
        if score > 0.8:
            explanation = f"High similarity ({score:.2f})"
        elif score > 0.6:
            explanation = f"Good match ({score:.2f})"
        elif score > 0.4:
            explanation = f"Moderate relevance ({score:.2f})"
        else:
            explanation = f"Low relevance ({score:.2f})"
        
        if common_words:
            explanation += f", common terms: {', '.join(list(common_words)[:3])}"
        
        return explanation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_chunks': len(self.chunks),
            'vector_dimensions': self.max_features,
            'vectorizer_fitted': self.vectorizer_fitted,
            'implementation': 'lightweight_sklearn'
        }

class SemanticMatcher:
    """Lightweight semantic matching for clause identification"""
    
    def __init__(self, vector_store: LightweightVectorStore):
        self.vector_store = vector_store
        
        # Policy-specific patterns
        self.clause_patterns = {
            'grace_period': [
                'grace period', 'premium payment', 'due date', 'thirty days'
            ],
            'waiting_period': [
                'waiting period', 'pre-existing disease', 'PED', 'months'
            ],
            'maternity': [
                'maternity expenses', 'childbirth', 'pregnancy', 'months'
            ],
            'cataract': [
                'cataract surgery', 'eye surgery', 'years'
            ],
            'organ_donor': [
                'organ donor', 'transplant', 'medical expenses'
            ],
            'ncd': [
                'No Claim Discount', 'NCD', 'percent'
            ],
            'health_checkup': [
                'health check-up', 'preventive', 'reimbursement'
            ],
            'hospital_definition': [
                'hospital defined', 'beds', 'nursing staff'
            ],
            'ayush': [
                'AYUSH treatment', 'Ayurveda', 'Naturopathy'
            ],
            'room_rent': [
                'room rent', 'ICU charges', 'percent'
            ]
        }
    
    def find_relevant_clauses(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find relevant clauses using semantic search"""
        
        # Get semantic search results
        search_results = self.vector_store.semantic_search_with_metadata(query, top_k * 2)
        
        # Enhance with pattern matching
        enhanced_results = []
        for result in search_results:
            # Add pattern matching score
            pattern_score = self._calculate_pattern_score(query, result['content'])
            
            # Combine semantic and pattern scores
            combined_score = (result['similarity_score'] * 0.7) + (pattern_score * 0.3)
            
            enhanced_result = {
                **result,
                'pattern_score': pattern_score,
                'combined_score': combined_score,
                'clause_type': self._identify_clause_type(query, result['content'])
            }
            
            enhanced_results.append(enhanced_result)
        
        # Sort by combined score and return top_k
        enhanced_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return enhanced_results[:top_k]
    
    def _calculate_pattern_score(self, query: str, content: str) -> float:
        """Calculate pattern matching score"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        max_score = 0.0
        
        for clause_type, patterns in self.clause_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern.lower() in query_lower and pattern.lower() in content_lower:
                    score += 1.0
            
            normalized_score = score / len(patterns)
            max_score = max(max_score, normalized_score)
        
        return min(max_score, 1.0)
    
    def _identify_clause_type(self, query: str, content: str) -> str:
        """Identify the type of clause"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        best_match = "general"
        best_score = 0.0
        
        for clause_type, patterns in self.clause_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern.lower() in query_lower and pattern.lower() in content_lower:
                    score += 1.0
            
            if score > best_score:
                best_score = score
                best_match = clause_type
        
        return best_match

# Alias for compatibility
VectorStore = LightweightVectorStore
