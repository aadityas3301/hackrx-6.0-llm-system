import requests
import PyPDF2
import io
import re
import logging
from typing import List, Dict, Any
from docx import Document
from bs4 import BeautifulSoup
import tiktoken
from config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
        return text.strip()
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - self.chunk_overlap
            
            # Extract chunk
            chunk = text[start:end]
            
            # Clean the chunk
            chunk = self.clean_text(chunk)
            
            if chunk.strip():
                chunks.append(chunk)
            
            # Move to next chunk
            start = end
            
            # Safety check to prevent infinite loops
            if len(chunks) >= settings.max_chunks:
                break
        
        return chunks
    
    async def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            logger.info(f"Downloading document from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading document: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                    text += "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def extract_text_from_docx(self, docx_content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            docx_file = io.BytesIO(docx_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise
    
    def extract_text_from_html(self, html_content: bytes) -> str:
        """Extract text from HTML content (for emails)"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {str(e)}")
            raise
    
    def detect_document_type(self, url: str) -> str:
        """Detect document type from URL"""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf'):
            return 'pdf'
        elif url_lower.endswith('.docx') or url_lower.endswith('.doc'):
            return 'docx'
        elif url_lower.endswith('.html') or url_lower.endswith('.htm'):
            return 'html'
        else:
            # Default to PDF for unknown types
            return 'pdf'
    
    async def process_document(self, document_url: str) -> List[Dict[str, Any]]:
        """Main method to process document and return chunks"""
        try:
            logger.info(f"Processing document: {document_url}")
            
            # Download document
            document_content = await self.download_document(document_url)
            
            # Detect document type
            doc_type = self.detect_document_type(document_url)
            
            # Extract text based on document type
            if doc_type == 'pdf':
                text = self.extract_text_from_pdf(document_content)
            elif doc_type == 'docx':
                text = self.extract_text_from_docx(document_content)
            elif doc_type == 'html':
                text = self.extract_text_from_html(document_content)
            else:
                text = self.extract_text_from_pdf(document_content)  # Default
            
            logger.info(f"Extracted {len(text)} characters from {doc_type} document")
            
            # Split into chunks
            chunks = self.split_text_into_chunks(text)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            # Create chunk metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    'id': f"chunk_{i}",
                    'content': chunk,
                    'document_url': document_url,
                    'document_type': doc_type,
                    'chunk_index': i,
                    'token_count': self.count_tokens(chunk),
                    'metadata': {
                        'source': document_url,
                        'chunk_id': i,
                        'doc_type': doc_type
                    }
                }
                processed_chunks.append(chunk_data)
            
            logger.info(f"Successfully processed document into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise 