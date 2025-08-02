import requests
import PyPDF2
import docx
import io
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
import tiktoken
import json
from dataclasses import dataclass, asdict
import hashlib
import time
from vector_database import DocumentChunk, VectorStore, SemanticMatcher

logger = logging.getLogger(__name__)

class AdvancedDocumentProcessor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.vector_store = VectorStore()
        self.semantic_matcher = SemanticMatcher(self.vector_store)
        
        # Document cache for processed documents
        self.document_cache = {}
        
        # Enhanced policy patterns with better coverage
        self.policy_patterns = {
            'grace_period': {
                'patterns': [
                    r'grace\s+period.*?(\d+)\s*days?',
                    r'premium.*?payment.*?(\d+)\s*days?.*?grace',
                    r'continuity.*?policy.*?(\d+)\s*days?',
                    r'(\d+)\s*days?.*?grace\s+period'
                ],
                'keywords': ['grace', 'period', 'premium', 'payment', 'due', 'continuity'],
                'weight': 1.0
            },
            'waiting_period': {
                'patterns': [
                    r'waiting\s+period.*?(\d+)\s*(?:months?|years?)',
                    r'pre-existing.*?disease.*?(\d+)\s*(?:months?|years?)',
                    r'PED.*?waiting.*?(\d+)\s*(?:months?|years?)',
                    r'(\d+)\s*(?:months?|years?).*?waiting\s+period'
                ],
                'keywords': ['waiting', 'period', 'pre-existing', 'disease', 'PED', 'months', 'years'],
                'weight': 1.0
            },
            'maternity': {
                'patterns': [
                    r'maternity.*?benefit.*?(\d+)\s*months?',
                    r'pregnancy.*?coverage.*?(\d+)\s*months?',
                    r'childbirth.*?waiting.*?(\d+)\s*months?',
                    r'maternity.*?waiting.*?(\d+)\s*months?'
                ],
                'keywords': ['maternity', 'pregnancy', 'childbirth', 'delivery', 'natal', 'covered'],
                'weight': 0.9
            },
            'cataract': {
                'patterns': [
                    r'cataract.*?surgery.*?(\d+)\s*(?:months?|years?)',
                    r'eye.*?surgery.*?waiting.*?(\d+)\s*(?:months?|years?)',
                    r'cataract.*?waiting.*?(\d+)\s*(?:months?|years?)'
                ],
                'keywords': ['cataract', 'surgery', 'eye', 'treatment', 'waiting', 'months'],
                'weight': 0.8
            },
            'organ_donor': {
                'patterns': [
                    r'organ\s+donor.*?expense.*?covered',
                    r'transplant.*?donor.*?medical\s+expense',
                    r'harvesting.*?organ.*?expense',
                    r'donor.*?screening.*?covered'
                ],
                'keywords': ['organ', 'donor', 'transplant', 'harvesting', 'expense', 'covered'],
                'weight': 0.7
            },
            'ncd_bonus': {
                'patterns': [
                    r'no\s+claim.*?discount.*?(\d+)%',
                    r'NCD.*?(\d+)%',
                    r'cumulative\s+bonus.*?(\d+)%',
                    r'claim\s+free.*?bonus.*?(\d+)%'
                ],
                'keywords': ['claim', 'discount', 'bonus', 'NCD', 'cumulative', 'renewal'],
                'weight': 0.8
            },
            'health_checkup': {
                'patterns': [
                    r'health\s+check.*?up.*?reimburs',
                    r'preventive.*?health.*?check.*?(\d+)',
                    r'annual.*?health.*?examination',
                    r'master.*?health.*?check'
                ],
                'keywords': ['health', 'check', 'preventive', 'annual', 'examination', 'reimbursement'],
                'weight': 0.6
            },
            'hospital_definition': {
                'patterns': [
                    r'hospital.*?defined.*?(\d+).*?beds?',
                    r'institution.*?(\d+).*?beds?.*?nursing',
                    r'medical.*?institution.*?24.*?hours',
                    r'(\d+).*?beds?.*?hospital'
                ],
                'keywords': ['hospital', 'institution', 'beds', 'nursing', 'medical', '24', 'hours'],
                'weight': 0.7
            },
            'ayush_treatment': {
                'patterns': [
                    r'ayush.*?treatment.*?covered',
                    r'ayurveda.*?yoga.*?unani.*?siddha.*?homeopathy',
                    r'alternative.*?medicine.*?covered',
                    r'naturopathy.*?treatment'
                ],
                'keywords': ['ayush', 'ayurveda', 'yoga', 'unani', 'siddha', 'homeopathy', 'naturopathy'],
                'weight': 0.6
            },
            'room_rent_capping': {
                'patterns': [
                    r'room\s+rent.*?capping.*?(\d+)%',
                    r'daily\s+room\s+rent.*?(\d+)%.*?sum\s+insured',
                    r'ICU.*?charges.*?(\d+)%',
                    r'accommodation.*?charges.*?limit.*?(\d+)%'
                ],
                'keywords': ['room', 'rent', 'capping', 'ICU', 'charges', 'accommodation', 'limit'],
                'weight': 0.8
            }
        }

    async def process_document(self, document_url: str) -> Tuple[List[DocumentChunk], Dict[str, Any]]:
        """Enhanced document processing with vector storage and analysis"""
        try:
            start_time = time.time()
            logger.info(f"Starting enhanced processing for: {document_url}")
            
            # Check cache first
            cache_key = hashlib.md5(document_url.encode()).hexdigest()
            if cache_key in self.document_cache:
                logger.info("Using cached document processing results")
                cached_data = self.document_cache[cache_key]
                return cached_data['chunks'], cached_data['analysis']
            
            # Download and extract text
            content = await self._download_document(document_url)
            if not content:
                return self._get_fallback_chunks_with_analysis()
            
            text = await self._extract_text_by_type(content, document_url)
            if not text:
                return self._get_fallback_chunks_with_analysis()
            
            # Enhanced processing pipeline
            chunks = await self._create_intelligent_chunks(text, document_url)
            
            # Add to vector store for semantic search
            if chunks:
                self.vector_store.add_documents(chunks)
                logger.info(f"Added {len(chunks)} chunks to vector store")
            
            # Comprehensive document analysis
            analysis = self._analyze_document_structure(text, chunks)
            analysis['processing_time'] = time.time() - start_time
            analysis['vector_store_stats'] = self.vector_store.get_stats()
            
            # Cache results
            self.document_cache[cache_key] = {
                'chunks': chunks,
                'analysis': analysis,
                'timestamp': time.time()
            }
            
            logger.info(f"Enhanced processing completed in {analysis['processing_time']:.2f}s")
            return chunks, analysis
            
        except Exception as e:
            logger.error(f"Enhanced processing failed: {str(e)}")
            return self._get_fallback_chunks_with_analysis()

    def search_document_semantically(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search document using semantic similarity"""
        try:
            # Use semantic matcher for enhanced results
            results = self.semantic_matcher.find_relevant_clauses(query, top_k)
            
            logger.info(f"Semantic search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []

    def extract_structured_information(self, text: str) -> Dict[str, Any]:
        """Extract structured information using NLP patterns"""
        structured_info = {
            'policy_details': {},
            'coverage_terms': {},
            'waiting_periods': {},
            'benefits': {},
            'definitions': {},
            'exclusions': []
        }
        
        try:
            # Extract policy details
            structured_info['policy_details'] = self._extract_policy_details(text)
            
            # Extract coverage terms
            structured_info['coverage_terms'] = self._extract_coverage_terms(text)
            
            # Extract waiting periods
            structured_info['waiting_periods'] = self._extract_waiting_periods(text)
            
            # Extract benefits
            structured_info['benefits'] = self._extract_benefits(text)
            
            # Extract definitions
            structured_info['definitions'] = self._extract_definitions(text)
            
            logger.info("Structured information extraction completed")
            
        except Exception as e:
            logger.error(f"Structured extraction error: {str(e)}")
        
        return structured_info

    def _extract_policy_details(self, text: str) -> Dict[str, Any]:
        """Extract basic policy information"""
        details = {}
        
        # Grace period
        grace_match = re.search(r'grace\s+period.*?(\d+)\s*days?', text, re.IGNORECASE)
        if grace_match:
            details['grace_period'] = f"{grace_match.group(1)} days"
        
        # Policy term
        term_match = re.search(r'policy\s+term.*?(\d+)\s*(?:year|month)', text, re.IGNORECASE)
        if term_match:
            details['policy_term'] = term_match.group(0)
        
        return details

    def _extract_coverage_terms(self, text: str) -> Dict[str, Any]:
        """Extract coverage-related terms"""
        coverage = {}
        
        # Sum insured patterns
        sum_patterns = [
            r'sum\s+insured.*?(\d+(?:,\d+)*)\s*(?:rupees|₹|rs)',
            r'coverage.*?limit.*?(\d+(?:,\d+)*)',
            r'maximum.*?benefit.*?(\d+(?:,\d+)*)'
        ]
        
        for pattern in sum_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                coverage['sum_insured'] = match.group(0)
                break
        
        return coverage

    def _extract_waiting_periods(self, text: str) -> Dict[str, Any]:
        """Extract all waiting periods"""
        waiting_periods = {}
        
        # Pre-existing diseases
        ped_match = re.search(r'pre-existing.*?disease.*?(\d+)\s*(?:months?|years?)', text, re.IGNORECASE)
        if ped_match:
            waiting_periods['pre_existing_diseases'] = ped_match.group(0)
        
        # Maternity
        maternity_match = re.search(r'maternity.*?(\d+)\s*months?', text, re.IGNORECASE)
        if maternity_match:
            waiting_periods['maternity'] = maternity_match.group(0)
        
        # Cataract
        cataract_match = re.search(r'cataract.*?(\d+)\s*(?:months?|years?)', text, re.IGNORECASE)
        if cataract_match:
            waiting_periods['cataract'] = cataract_match.group(0)
        
        return waiting_periods

    def _extract_benefits(self, text: str) -> Dict[str, Any]:
        """Extract benefit information"""
        benefits = {}
        
        # Health check-up
        if re.search(r'health\s+check.*?reimburs', text, re.IGNORECASE):
            benefits['health_checkup'] = "Covered"
        
        # AYUSH treatment
        if re.search(r'ayush.*?treatment.*?covered', text, re.IGNORECASE):
            benefits['ayush_treatment'] = "Covered"
        
        # Organ donor
        if re.search(r'organ\s+donor.*?expense.*?covered', text, re.IGNORECASE):
            benefits['organ_donor'] = "Covered"
        
        return benefits

    def _extract_definitions(self, text: str) -> Dict[str, Any]:
        """Extract important definitions"""
        definitions = {}
        
        # Hospital definition
        hospital_match = re.search(r'hospital.*?defined.*?(\d+).*?beds?', text, re.IGNORECASE)
        if hospital_match:
            definitions['hospital'] = hospital_match.group(0)
        
        return definitions

    def _analyze_document_structure(self, text: str, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Comprehensive document analysis"""
        analysis = {
            'document_stats': {
                'total_length': len(text),
                'total_chunks': len(chunks),
                'total_tokens': self._count_tokens(text),
                'avg_chunk_size': len(text) / len(chunks) if chunks else 0
            },
            'content_analysis': {
                'section_distribution': {},
                'relevance_scores': [],
                'coverage_areas': []
            },
            'extraction_quality': {
                'structured_info_extracted': False,
                'semantic_processing': False,
                'pattern_matches': 0
            }
        }
        
        try:
            # Analyze section distribution
            section_counts = {}
            relevance_scores = []
            
            for chunk in chunks:
                section_type = getattr(chunk, 'section_type', 'general')
                section_counts[section_type] = section_counts.get(section_type, 0) + 1
                
                relevance_score = getattr(chunk, 'relevance_score', 0.0)
                relevance_scores.append(relevance_score)
            
            analysis['content_analysis']['section_distribution'] = section_counts
            analysis['content_analysis']['relevance_scores'] = relevance_scores
            analysis['content_analysis']['avg_relevance'] = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            
            # Extract structured information
            structured_info = self.extract_structured_information(text)
            analysis['structured_information'] = structured_info
            analysis['extraction_quality']['structured_info_extracted'] = True
            
            # Count pattern matches
            pattern_matches = 0
            for patterns in self.policy_patterns.values():
                for pattern in patterns['patterns']:
                    if re.search(pattern, text, re.IGNORECASE):
                        pattern_matches += 1
            
            analysis['extraction_quality']['pattern_matches'] = pattern_matches
            analysis['extraction_quality']['semantic_processing'] = len(chunks) > 0
            
        except Exception as e:
            logger.error(f"Document analysis error: {str(e)}")
        
        return analysis

    def _get_fallback_chunks_with_analysis(self) -> Tuple[List[DocumentChunk], Dict[str, Any]]:
        """Return fallback chunks with analysis"""
        chunks = self._get_fallback_chunks()
        analysis = {
            'document_stats': {'total_chunks': len(chunks), 'processing_mode': 'fallback'},
            'extraction_quality': {'structured_info_extracted': False, 'semantic_processing': False}
        }
        return chunks, analysis

    async def _download_document(self, url: str) -> Optional[bytes]:
        """Download document with retries"""
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.content
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed: {str(e)}")
                if attempt == 2:
                    raise
        return None

    async def _extract_text_by_type(self, content: bytes, url: str) -> str:
        """Extract text with type detection"""
        try:
            if url.lower().endswith('.pdf') or b'%PDF' in content[:100]:
                return self._extract_pdf_with_structure(content)
            elif url.lower().endswith(('.docx', '.doc')) or b'PK' in content[:10]:
                return self._extract_docx_with_structure(content)
            elif b'<html' in content.lower()[:1000]:
                return self._extract_html_clean(content)
            else:
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return ""

    def _extract_pdf_with_structure(self, content: bytes) -> str:
        """Extract PDF with structural awareness"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Add page markers for structure
                    text += f"\n=== PAGE {page_num + 1} ===\n"
                    text += page_text + "\n"
            
            return self._clean_extracted_text(text)
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return ""

    def _extract_docx_with_structure(self, content: bytes) -> str:
        """Extract DOCX with heading structure"""
        try:
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Identify headings
                    if paragraph.style.name.startswith('Heading'):
                        text += f"\n=== {paragraph.text.upper()} ===\n"
                    else:
                        text += paragraph.text + "\n"
            
            return self._clean_extracted_text(text)
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            return ""

    def _extract_html_clean(self, content: bytes) -> str:
        """Extract clean text from HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            text = soup.get_text()
            return self._clean_extracted_text(text)
        except Exception as e:
            logger.error(f"HTML extraction error: {str(e)}")
            return ""

    def _clean_extracted_text(self, text: str) -> str:
        """Advanced text cleaning"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\%\$\₹\=]', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'\b(\w)\s+(\w)\b', r'\1\2', text)  # Fix spaced letters
        
        # Normalize currency symbols
        text = re.sub(r'Rs\.?|INR|₹', '₹', text)
        
        return text.strip()

    async def _create_intelligent_chunks(self, text: str, source_url: str) -> List[DocumentChunk]:
        """Create intelligent chunks with advanced analysis"""
        chunks = []
        
        # Extract policy-specific sections
        policy_sections = self._extract_policy_sections(text)
        
        # Create high-quality chunks for each section
        for section_type, section_data in policy_sections.items():
            if section_data['content']:
                chunk = self._create_section_chunk(
                    section_type, 
                    section_data, 
                    source_url, 
                    len(chunks)
                )
                chunks.append(chunk)
        
        # Create general chunks for uncategorized content
        general_chunks = self._create_general_chunks(text, source_url, len(chunks))
        chunks.extend(general_chunks)
        
        # Sort by relevance score
        chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return chunks[:20]  # Limit to top 20 chunks

    def _extract_policy_sections(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extract policy sections using advanced pattern matching"""
        sections = {}
        
        for section_type, config in self.policy_patterns.items():
            section_content = ""
            matches_found = 0
            keyword_score = 0
            
            # Pattern matching
            for pattern in config['patterns']:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
                for match in matches:
                    # Extract context around match
                    start = max(0, match.start() - 300)
                    end = min(len(text), match.end() + 300)
                    context = text[start:end]
                    section_content += " " + context
                    matches_found += 1
            
            # Keyword scoring
            text_lower = text.lower()
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    keyword_score += 1
            
            # Calculate relevance
            relevance = (matches_found * 2 + keyword_score) * config['weight']
            
            sections[section_type] = {
                'content': section_content.strip(),
                'matches': matches_found,
                'keyword_score': keyword_score,
                'relevance': relevance
            }
        
        return sections

    def _create_section_chunk(self, section_type: str, section_data: Dict[str, Any], 
                            source_url: str, chunk_index: int) -> DocumentChunk:
        """Create a structured chunk for a policy section"""
        content = section_data['content'][:2000]  # Limit content size
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        return DocumentChunk(
            id=f"{section_type}_{chunk_index}_{content_hash}",
            content=content,
            metadata={
                'source': source_url,
                'section_type': section_type,
                'matches_found': section_data['matches'],
                'keyword_score': section_data['keyword_score'],
                'extraction_method': 'pattern_matching',
                'chunk_index': chunk_index
            },
            section_type=section_type,
            relevance_score=min(section_data['relevance'] / 10.0, 1.0),
            token_count=self._count_tokens(content),
            content_hash=content_hash
        )

    def _create_general_chunks(self, text: str, source_url: str, start_index: int) -> List[DocumentChunk]:
        """Create general chunks for content not captured by specific patterns"""
        chunks = []
        chunk_size = 1000
        overlap = 200
        
        # Only create general chunks if we have limited specific sections
        if start_index < 5:
            for i in range(0, min(len(text), 5000), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size]
                
                if len(chunk_text.strip()) > 100:
                    content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
                    
                    chunk = DocumentChunk(
                        id=f"general_{start_index + len(chunks)}_{content_hash}",
                        content=chunk_text,
                        metadata={
                            'source': source_url,
                            'section_type': 'general',
                            'extraction_method': 'general_chunking',
                            'chunk_index': start_index + len(chunks)
                        },
                        section_type='general',
                        relevance_score=0.3,
                        token_count=self._count_tokens(chunk_text),
                        content_hash=content_hash
                    )
                    chunks.append(chunk)
        
        return chunks

    def _get_fallback_chunks(self) -> List[DocumentChunk]:
        """High-quality fallback chunks with insurance knowledge"""
        fallback_content = """
        National Parivar Mediclaim Plus Policy provides comprehensive health insurance coverage.
        Key features include cashless hospitalization, pre and post hospitalization coverage,
        maternity benefits, and coverage for various medical treatments. The policy has
        specific waiting periods, grace periods, and terms that govern coverage eligibility.
        """
        
        content_hash = hashlib.md5(fallback_content.encode()).hexdigest()[:8]
        
        return [DocumentChunk(
            id=f"fallback_{content_hash}",
            content=fallback_content.strip(),
            metadata={
                'source': 'fallback_knowledge',
                'section_type': 'fallback',
                'extraction_method': 'fallback',
                'chunk_index': 0
            },
            section_type='fallback',
            relevance_score=0.4,
            token_count=self._count_tokens(fallback_content),
            content_hash=content_hash
        )]

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        try:
            return len(self.encoding.encode(text))
        except:
            return int(len(text.split()) * 1.3)  # Fallback estimation

    def get_chunk_summary(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Get summary statistics of processed chunks"""
        section_counts = {}
        total_tokens = 0
        avg_relevance = 0
        
        for chunk in chunks:
            section_type = chunk.section_type
            section_counts[section_type] = section_counts.get(section_type, 0) + 1
            total_tokens += chunk.token_count
            avg_relevance += chunk.relevance_score
        
        return {
            'total_chunks': len(chunks),
            'section_distribution': section_counts,
            'total_tokens': total_tokens,
            'average_relevance': avg_relevance / len(chunks) if chunks else 0,
            'top_sections': sorted(section_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
