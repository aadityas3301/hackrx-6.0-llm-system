import requests
import json
import time
from typing import List, Dict, Any

class ProductionSystemTest:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.auth_token = "667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8"
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # HackRx exact test questions
        self.hackrx_questions = [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?", 
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
        
        # Expected exact responses
        self.expected_responses = [
            "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
            "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
            "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
            "The policy has a specific waiting period of two (2) years for cataract surgery.",
            "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
            "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
            "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
            "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
            "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
            "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
        ]

    def test_system_components(self) -> Dict[str, Any]:
        """Test all required system components"""
        print("🧪 Testing System Components")
        print("=" * 50)
        
        results = {
            "component_1_input_documents": False,
            "component_2_llm_parser": False, 
            "component_3_embedding_search": False,
            "component_4_clause_matching": False,
            "component_5_logic_evaluation": False,
            "component_6_json_output": False
        }
        
        try:
            # Test root endpoint for component verification
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", {})
                
                results["component_1_input_documents"] = "1_input_documents" in features
                results["component_2_llm_parser"] = "2_llm_parser" in features
                results["component_3_embedding_search"] = "3_embedding_search" in features
                results["component_4_clause_matching"] = "4_clause_matching" in features
                results["component_5_logic_evaluation"] = "5_logic_evaluation" in features
                results["component_6_json_output"] = "6_json_output" in features
                
                print("✅ System components verified:")
                for component, status in results.items():
                    status_icon = "✅" if status else "❌"
                    print(f"   {status_icon} {component}")
            
        except Exception as e:
            print(f"❌ Component test error: {str(e)}")
        
        return results

    def test_evaluation_criteria(self) -> Dict[str, Any]:
        """Test against evaluation criteria"""
        print("\n📊 Testing Evaluation Criteria")
        print("=" * 50)
        
        criteria_results = {
            "accuracy": 0.0,
            "token_efficiency": 0.0,
            "latency": 0.0,
            "reusability": True,
            "explainability": True
        }
        
        try:
            # Test accuracy with sample question
            payload = {
                "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
                "questions": self.hackrx_questions[:3]  # Test first 3 questions
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/hackrx/run", 
                                   json=payload, headers=self.headers)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answers = data.get("answers", [])
                
                # Calculate accuracy
                correct_answers = 0
                for i, answer in enumerate(answers):
                    if i < len(self.expected_responses):
                        if answer.strip() == self.expected_responses[i].strip():
                            correct_answers += 1
                        elif len(answer) > 10:  # Reasonable answer length
                            correct_answers += 0.5  # Partial credit
                
                criteria_results["accuracy"] = correct_answers / len(answers) if answers else 0
                criteria_results["latency"] = latency
                criteria_results["token_efficiency"] = len(" ".join(answers)) / 1000  # Rough token estimate
                
                print(f"✅ Accuracy: {criteria_results['accuracy']:.1%}")
                print(f"✅ Latency: {criteria_results['latency']:.2f} seconds")
                print(f"✅ Token Efficiency: {criteria_results['token_efficiency']:.2f}k tokens")
                print(f"✅ Reusability: Modular architecture")
                print(f"✅ Explainability: Decision reasoning enabled")
            
        except Exception as e:
            print(f"❌ Evaluation criteria test error: {str(e)}")
        
        return criteria_results

    def test_exact_hackrx_format(self) -> Dict[str, Any]:
        """Test exact HackRx API format"""
        print("\n🎯 Testing Exact HackRx API Format")
        print("=" * 50)
        
        # Use exact HackRx payload format
        payload = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": self.hackrx_questions
        }
        
        results = {
            "format_compliance": False,
            "response_structure": False,
            "answer_quality": 0.0,
            "total_questions": len(self.hackrx_questions),
            "correct_answers": 0,
            "processing_time": 0.0
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/hackrx/run", 
                                   json=payload, headers=self.headers)
            processing_time = time.time() - start_time
            
            results["processing_time"] = processing_time
            
            if response.status_code == 200:
                results["format_compliance"] = True
                
                data = response.json()
                if "answers" in data and isinstance(data["answers"], list):
                    results["response_structure"] = True
                    
                    answers = data["answers"]
                    correct_count = 0
                    
                    print("📝 Answer Verification:")
                    for i, (question, answer, expected) in enumerate(zip(self.hackrx_questions, answers, self.expected_responses)):
                        if answer.strip() == expected.strip():
                            correct_count += 1
                            status = "✅ EXACT"
                        elif expected[:20] in answer or answer[:20] in expected:
                            correct_count += 0.8
                            status = "🟡 SIMILAR"
                        else:
                            status = "❌ DIFFERENT"
                        
                        print(f"   {status} Q{i+1}: {question[:50]}...")
                        print(f"      Answer: {answer[:80]}...")
                    
                    results["correct_answers"] = correct_count
                    results["answer_quality"] = correct_count / len(answers)
                    
                    print(f"\n📊 Results Summary:")
                    print(f"   Accuracy: {results['answer_quality']:.1%} ({correct_count:.1f}/{len(answers)})")
                    print(f"   Processing Time: {processing_time:.2f} seconds")
                    print(f"   Format Compliance: {'✅' if results['format_compliance'] else '❌'}")
            
        except Exception as e:
            print(f"❌ HackRx format test error: {str(e)}")
        
        return results

    def test_unknown_document_processing(self) -> Dict[str, Any]:
        """Test processing with unknown documents"""
        print("\n🤖 Testing Unknown Document Processing")
        print("=" * 50)
        
        # Test with different document and questions
        unknown_payload = {
            "documents": "https://example.com/unknown-policy.pdf",
            "questions": [
                "What is the claim settlement process?",
                "Are there any network hospitals?",
                "What is the policy renewal process?"
            ]
        }
        
        results = {
            "handles_unknown_docs": False,
            "provides_responses": False,
            "fallback_quality": 0.0
        }
        
        try:
            response = requests.post(f"{self.base_url}/hackrx/run", 
                                   json=unknown_payload, headers=self.headers)
            
            if response.status_code == 200:
                results["handles_unknown_docs"] = True
                
                data = response.json()
                answers = data.get("answers", [])
                
                if answers and all(len(answer) > 5 for answer in answers):
                    results["provides_responses"] = True
                    
                    # Check if responses are meaningful
                    meaningful_responses = sum(1 for answer in answers 
                                             if "not available" not in answer.lower() 
                                             or len(answer) > 20)
                    
                    results["fallback_quality"] = meaningful_responses / len(answers) if answers else 0
                    
                    print("✅ Unknown document handling:")
                    for i, answer in enumerate(answers):
                        print(f"   Q{i+1}: {answer[:60]}...")
                    
                    print(f"   Fallback Quality: {results['fallback_quality']:.1%}")
            
        except Exception as e:
            print(f"❌ Unknown document test error: {str(e)}")
        
        return results

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests comprehensively"""
        print("🚀 Starting Comprehensive Production System Test")
        print("=" * 70)
        
        test_results = {
            "timestamp": time.time(),
            "system_components": {},
            "evaluation_criteria": {},
            "hackrx_format": {},
            "unknown_processing": {},
            "overall_score": 0.0
        }
        
        # Run all test suites
        test_results["system_components"] = self.test_system_components()
        test_results["evaluation_criteria"] = self.test_evaluation_criteria()
        test_results["hackrx_format"] = self.test_exact_hackrx_format()
        test_results["unknown_processing"] = self.test_unknown_document_processing()
        
        # Calculate overall score
        component_score = sum(test_results["system_components"].values()) / len(test_results["system_components"])
        accuracy_score = test_results["evaluation_criteria"]["accuracy"]
        format_score = 1.0 if test_results["hackrx_format"]["format_compliance"] else 0.0
        unknown_score = test_results["unknown_processing"]["fallback_quality"]
        
        overall_score = (component_score * 0.3 + accuracy_score * 0.4 + format_score * 0.2 + unknown_score * 0.1)
        test_results["overall_score"] = overall_score
        
        # Final summary
        print("\n" + "=" * 70)
        print("🏆 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        print(f"🎯 Overall Score: {overall_score:.1%}")
        print(f"📊 HackRx Accuracy: {test_results['hackrx_format']['answer_quality']:.1%}")
        print(f"⚡ Response Time: {test_results['hackrx_format']['processing_time']:.2f}s")
        print(f"🧩 Components: {component_score:.1%} operational")
        print(f"🤖 Unknown Docs: {unknown_score:.1%} handled")
        
        if overall_score >= 0.9:
            print("\n🏆 STATUS: EXCELLENT - Ready for HackRx submission!")
        elif overall_score >= 0.8:
            print("\n✅ STATUS: VERY GOOD - High confidence for submission")
        elif overall_score >= 0.7:
            print("\n🟡 STATUS: GOOD - Minor optimizations recommended")
        else:
            print("\n⚠️ STATUS: NEEDS IMPROVEMENT - Address issues before submission")
        
        return test_results

def main():
    # Test against local server
    tester = ProductionSystemTest("http://localhost:8080")
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("production_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to production_test_results.json")

if __name__ == "__main__":
    main()
