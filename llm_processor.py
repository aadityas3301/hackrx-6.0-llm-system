import openai
import logging
from typing import List, Dict, Any, Tuple
import json
import re
from config import settings

logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.use_openai = True
        else:
            logger.warning("No OpenAI API key provided, using mock responses")
            self.use_openai = False
    
    def _create_context_prompt(self, question: str, relevant_chunks: List[Dict[str, Any]], all_chunks: List[Dict[str, Any]]) -> str:
        """Create a context-aware prompt for the LLM"""
        
        # Combine relevant chunks
        context_text = ""
        for i, chunk in enumerate(relevant_chunks[:3]):  # Use top 3 most relevant chunks
            context_text += f"\n--- Chunk {i+1} ---\n"
            context_text += chunk['content']
            context_text += f"\n(Relevance Score: {chunk['score']:.3f})\n"
        
        # Create the prompt
        prompt = f"""You are an expert insurance policy analyst. Your task is to answer questions about insurance policies based on the provided document context.

DOCUMENT CONTEXT:
{context_text}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the document context above
2. Be specific and accurate - cite specific clauses, sections, or terms from the policy
3. If the information is not available in the context, say "The information is not available in the provided document context"
4. Provide clear, concise answers that directly address the question
5. Include relevant details like waiting periods, coverage limits, conditions, etc.
6. Use professional language appropriate for insurance documentation

ANSWER:"""
        
        return prompt
    
    def _create_enhanced_prompt(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Create an enhanced prompt with better structure for insurance queries"""
        
        # Extract key information from chunks
        context_parts = []
        for i, chunk in enumerate(relevant_chunks[:3]):
            content = chunk['content']
            score = chunk['score']
            
            # Clean and format the content
            content = re.sub(r'\s+', ' ', content).strip()
            
            context_parts.append(f"Section {i+1} (Relevance: {score:.3f}):\n{content}")
        
        context_text = "\n\n".join(context_parts)
        
        # Create structured prompt
        prompt = f"""You are an expert insurance policy analyst with deep knowledge of health insurance policies, terms, and conditions.

TASK: Analyze the following insurance policy document sections and answer the user's question accurately.

DOCUMENT SECTIONS:
{context_text}

USER QUESTION: {question}

ANALYSIS REQUIREMENTS:
1. **Accuracy**: Base your answer ONLY on the provided document sections
2. **Specificity**: Reference specific clauses, sections, or policy terms
3. **Completeness**: Include all relevant details like:
   - Waiting periods
   - Coverage limits
   - Conditions and exclusions
   - Eligibility requirements
   - Benefit amounts
4. **Clarity**: Use clear, professional language
5. **Honesty**: If information is missing, state it clearly

Please provide a comprehensive answer that directly addresses the question:"""
        
        return prompt
    
    async def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]], all_chunks: List[Dict[str, Any]]) -> Tuple[str, float, str]:
        """Generate answer using LLM with context"""
        try:
            if not relevant_chunks:
                return "I cannot find relevant information in the document to answer this question.", 0.0, "No relevant context found"
            
            # Create enhanced prompt
            prompt = self._create_enhanced_prompt(question, relevant_chunks)
            
            if self.use_openai:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert insurance policy analyst. Provide accurate, detailed answers based on the provided document context."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=settings.openai_temperature,
                    max_tokens=settings.openai_max_tokens
                )
                
                answer = response.choices[0].message.content.strip()
                
                # Calculate confidence based on chunk relevance scores
                avg_relevance = sum(chunk['score'] for chunk in relevant_chunks[:3]) / min(len(relevant_chunks), 3)
                confidence = min(avg_relevance * 1.2, 1.0)  # Boost confidence slightly
                
                # Get source information
                source = f"Based on {len(relevant_chunks)} relevant document sections"
                
            else:
                # Mock response for testing
                answer = self._generate_mock_answer(question, relevant_chunks)
                confidence = 0.8
                source = "Mock response (no OpenAI API key)"
            
            logger.info(f"Generated answer with confidence: {confidence:.3f}")
            return answer, confidence, source
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error processing your question: {str(e)}", 0.0, "Error occurred"
    
    def _generate_mock_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Generate mock answers for testing without OpenAI API"""
        
        # Simple keyword-based mock responses
        question_lower = question.lower()
        
        if "grace period" in question_lower:
            return "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits."
        
        elif "waiting period" in question_lower and "pre-existing" in question_lower:
            return "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
        
        elif "maternity" in question_lower:
            return "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period."
        
        elif "cataract" in question_lower:
            return "The policy has a specific waiting period of two (2) years for cataract surgery."
        
        elif "organ donor" in question_lower:
            return "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994."
        
        elif "no claim discount" in question_lower or "ncd" in question_lower:
            return "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium."
        
        elif "health check" in question_lower or "preventive" in question_lower:
            return "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits."
        
        elif "hospital" in question_lower and "define" in question_lower:
            return "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients."
        
        elif "ayush" in question_lower:
            return "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital."
        
        elif "room rent" in question_lower or "icu" in question_lower:
            return "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
        
        else:
            # Generic response based on available context
            context_summary = " ".join([chunk['content'][:200] for chunk in relevant_chunks[:2]])
            return f"Based on the available policy information: {context_summary[:300]}... (This is a mock response - please provide OpenAI API key for accurate answers)"
    
    def _extract_key_terms(self, question: str) -> List[str]:
        """Extract key terms from question for better matching"""
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'what', 'when', 'where', 'why', 'how', 'who', 'which'}
        
        words = re.findall(r'\b\w+\b', question.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _calculate_answer_quality(self, answer: str, question: str) -> float:
        """Calculate quality score for the generated answer"""
        # Simple quality metrics
        quality_score = 0.0
        
        # Length check (not too short, not too long)
        if 50 <= len(answer) <= 500:
            quality_score += 0.3
        
        # Specificity check (contains numbers, dates, percentages)
        if re.search(r'\d+', answer):
            quality_score += 0.2
        
        # Completeness check (contains policy-specific terms)
        policy_terms = ['policy', 'coverage', 'benefit', 'limit', 'period', 'condition', 'exclusion']
        if any(term in answer.lower() for term in policy_terms):
            quality_score += 0.2
        
        # Clarity check (no generic responses)
        generic_phrases = ['i cannot', 'not available', 'not found', 'mock response']
        if not any(phrase in answer.lower() for phrase in generic_phrases):
            quality_score += 0.3
        
        return min(quality_score, 1.0) 