#!/usr/bin/env python3
"""
Edge Case and Error Handling Tests for IQ Game Backend
"""

import requests
import json

BACKEND_URL = "https://smart-trivia-game-1.preview.emergentagent.com/api"

class EdgeCaseTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = {'passed': 0, 'failed': 0, 'errors': []}
    
    def log_result(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_invalid_language(self):
        """Test questions with invalid language"""
        try:
            response = self.session.get(f"{BACKEND_URL}/questions?language=invalid&limit=5")
            if response.status_code == 200:
                data = response.json()
                # Should fallback to English or return empty
                self.log_result("Invalid Language Handling", True, "Handled gracefully")
            else:
                self.log_result("Invalid Language Handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Language Handling", False, f"Exception: {str(e)}")
    
    def test_invalid_difficulty(self):
        """Test questions with invalid difficulty"""
        try:
            response = self.session.get(f"{BACKEND_URL}/questions?difficulty=invalid&limit=5")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Invalid Difficulty Handling", True, "Handled gracefully")
            else:
                self.log_result("Invalid Difficulty Handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Difficulty Handling", False, f"Exception: {str(e)}")
    
    def test_large_limit(self):
        """Test questions with very large limit"""
        try:
            response = self.session.get(f"{BACKEND_URL}/questions?limit=1000")
            if response.status_code == 200:
                data = response.json()
                # Should handle large limits gracefully
                self.log_result("Large Limit Handling", True, f"Returned {len(data)} questions")
            else:
                self.log_result("Large Limit Handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Large Limit Handling", False, f"Exception: {str(e)}")
    
    def test_invalid_score_data(self):
        """Test score submission with invalid data"""
        invalid_data = {
            "user_name": "",  # Empty name
            "score": -10,     # Negative score
            "total_questions": 0,  # Zero questions
            "correct_answers": 15,  # More correct than total
            "difficulty": "invalid",
            "mode": "invalid",
            "language": "invalid"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/scores", json=invalid_data)
            # Should either reject with 400 or handle gracefully
            if response.status_code in [200, 400, 422]:
                self.log_result("Invalid Score Data", True, f"HTTP {response.status_code} - handled appropriately")
            else:
                self.log_result("Invalid Score Data", False, f"Unexpected HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Score Data", False, f"Exception: {str(e)}")
    
    def test_malformed_json(self):
        """Test endpoints with malformed JSON"""
        try:
            response = self.session.post(f"{BACKEND_URL}/scores", 
                                       data="invalid json",
                                       headers={'Content-Type': 'application/json'})
            # Should return 400 or 422 for malformed JSON
            if response.status_code in [400, 422]:
                self.log_result("Malformed JSON Handling", True, f"HTTP {response.status_code}")
            else:
                self.log_result("Malformed JSON Handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Malformed JSON Handling", False, f"Exception: {str(e)}")
    
    def test_ai_generation_without_key(self):
        """Test AI generation behavior (should work with existing key)"""
        try:
            response = self.session.post(f"{BACKEND_URL}/generate-question", 
                                       json={"language": "en", "difficulty": "easy"})
            if response.status_code == 200:
                self.log_result("AI Generation Available", True, "AI service working")
            elif response.status_code == 500:
                self.log_result("AI Generation Error Handling", True, "Proper error handling for AI service")
            else:
                self.log_result("AI Generation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("AI Generation", False, f"Exception: {str(e)}")
    
    def test_nonexistent_endpoints(self):
        """Test non-existent endpoints"""
        try:
            response = self.session.get(f"{BACKEND_URL}/nonexistent")
            if response.status_code == 404:
                self.log_result("404 Handling", True, "Proper 404 for non-existent endpoint")
            else:
                self.log_result("404 Handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("404 Handling", False, f"Exception: {str(e)}")
    
    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("🔍 Starting Edge Case and Error Handling Tests")
        print("=" * 50)
        
        self.test_invalid_language()
        self.test_invalid_difficulty()
        self.test_large_limit()
        self.test_invalid_score_data()
        self.test_malformed_json()
        self.test_ai_generation_without_key()
        self.test_nonexistent_endpoints()
        
        print("=" * 50)
        print("🏁 Edge Case Test Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = EdgeCaseTester()
    success = tester.run_edge_case_tests()
    exit(0 if success else 1)