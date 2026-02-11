#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for IQ Game
Tests all endpoints with realistic data and multiple scenarios
"""

import requests
import json
import time
from datetime import datetime
import random

# Get backend URL from frontend env
BACKEND_URL = "https://smart-trivia-game-1.preview.emergentagent.com/api"

# Test data
LANGUAGES = ['tr', 'en', 'de', 'fr', 'es']
DIFFICULTIES = ['easy', 'medium', 'hard']
CATEGORIES = ['logic', 'math', 'pattern', 'verbal', 'spatial']
MODES = ['classic', 'time_race', 'daily', 'multiplayer']

# Realistic user names for different languages
USER_NAMES = {
    'tr': ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya', 'Fatma Şahin'],
    'en': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis'],
    'de': ['Hans Mueller', 'Anna Schmidt', 'Klaus Weber', 'Maria Fischer'],
    'fr': ['Pierre Dubois', 'Marie Martin', 'Jean Bernard', 'Sophie Moreau'],
    'es': ['Carlos Garcia', 'Ana Rodriguez', 'Miguel Lopez', 'Isabel Martinez']
}

class IQGameAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_root_endpoint(self):
        """Test GET /api/"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'version' in data:
                    self.log_result("Root Endpoint", True, f"Message: {data['message']}, Version: {data['version']}")
                else:
                    self.log_result("Root Endpoint", False, "Missing required fields in response", response)
            else:
                self.log_result("Root Endpoint", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Exception: {str(e)}")
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result("Health Check", True, "Service is healthy")
                else:
                    self.log_result("Health Check", False, f"Unexpected status: {data.get('status')}", response)
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
    
    def test_init_questions(self):
        """Test POST /api/init-questions"""
        try:
            response = self.session.post(f"{BACKEND_URL}/init-questions")
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_result("Initialize Questions", True, data['message'])
                else:
                    self.log_result("Initialize Questions", False, "Missing message in response", response)
            else:
                self.log_result("Initialize Questions", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Initialize Questions", False, f"Exception: {str(e)}")
    
    def test_get_questions_basic(self):
        """Test GET /api/questions with basic parameters"""
        try:
            response = self.session.get(f"{BACKEND_URL}/questions?language=en&limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    question = data[0]
                    required_fields = ['id', 'category', 'difficulty', 'question', 'options', 'correct_answer']
                    if all(field in question for field in required_fields):
                        self.log_result("Get Questions Basic", True, f"Retrieved {len(data)} questions")
                    else:
                        missing = [f for f in required_fields if f not in question]
                        self.log_result("Get Questions Basic", False, f"Missing fields: {missing}", response)
                else:
                    self.log_result("Get Questions Basic", False, "No questions returned or invalid format", response)
            else:
                self.log_result("Get Questions Basic", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Questions Basic", False, f"Exception: {str(e)}")
    
    def test_get_questions_all_languages(self):
        """Test GET /api/questions for all supported languages"""
        for lang in LANGUAGES:
            try:
                response = self.session.get(f"{BACKEND_URL}/questions?language={lang}&limit=3")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Check if questions have content in the requested language
                        has_content = all(q.get('question', '').strip() for q in data)
                        if has_content:
                            self.log_result(f"Questions Language {lang.upper()}", True, f"Retrieved {len(data)} questions")
                        else:
                            self.log_result(f"Questions Language {lang.upper()}", False, "Empty question content", response)
                    else:
                        self.log_result(f"Questions Language {lang.upper()}", False, "No questions returned", response)
                else:
                    self.log_result(f"Questions Language {lang.upper()}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Questions Language {lang.upper()}", False, f"Exception: {str(e)}")
    
    def test_get_questions_by_difficulty(self):
        """Test GET /api/questions filtered by difficulty"""
        for difficulty in DIFFICULTIES:
            try:
                response = self.session.get(f"{BACKEND_URL}/questions?difficulty={difficulty}&language=en&limit=3")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Verify all questions have the requested difficulty
                        correct_difficulty = all(q.get('difficulty') == difficulty for q in data)
                        if correct_difficulty:
                            self.log_result(f"Questions Difficulty {difficulty.title()}", True, f"Retrieved {len(data)} {difficulty} questions")
                        else:
                            self.log_result(f"Questions Difficulty {difficulty.title()}", False, "Incorrect difficulty filtering", response)
                    else:
                        self.log_result(f"Questions Difficulty {difficulty.title()}", False, "No questions returned", response)
                else:
                    self.log_result(f"Questions Difficulty {difficulty.title()}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Questions Difficulty {difficulty.title()}", False, f"Exception: {str(e)}")
    
    def test_score_submission(self):
        """Test POST /api/scores with realistic data"""
        for lang in ['en', 'tr', 'de']:  # Test a few languages
            try:
                user_name = random.choice(USER_NAMES[lang])
                score_data = {
                    "user_name": user_name,
                    "score": random.randint(60, 95),
                    "total_questions": 10,
                    "correct_answers": random.randint(6, 9),
                    "difficulty": random.choice(DIFFICULTIES),
                    "mode": random.choice(MODES),
                    "language": lang
                }
                
                response = self.session.post(f"{BACKEND_URL}/scores", json=score_data)
                if response.status_code == 200:
                    data = response.json()
                    if 'id' in data and 'estimated_iq' in data:
                        iq = data['estimated_iq']
                        if 70 <= iq <= 160:  # Valid IQ range
                            self.log_result(f"Score Submission {lang.upper()}", True, f"User: {user_name}, IQ: {iq}")
                        else:
                            self.log_result(f"Score Submission {lang.upper()}", False, f"Invalid IQ: {iq}", response)
                    else:
                        self.log_result(f"Score Submission {lang.upper()}", False, "Missing required response fields", response)
                else:
                    self.log_result(f"Score Submission {lang.upper()}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Score Submission {lang.upper()}", False, f"Exception: {str(e)}")
    
    def test_leaderboard_basic(self):
        """Test GET /api/scores/leaderboard"""
        try:
            response = self.session.get(f"{BACKEND_URL}/scores/leaderboard?limit=10")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check leaderboard structure
                        entry = data[0]
                        required_fields = ['rank', 'user_name', 'score', 'estimated_iq', 'difficulty', 'mode']
                        if all(field in entry for field in required_fields):
                            # Check if sorted by IQ (descending)
                            is_sorted = all(data[i]['estimated_iq'] >= data[i+1]['estimated_iq'] 
                                          for i in range(len(data)-1))
                            if is_sorted:
                                self.log_result("Leaderboard Basic", True, f"Retrieved {len(data)} entries, properly sorted")
                            else:
                                self.log_result("Leaderboard Basic", False, "Leaderboard not sorted by IQ", response)
                        else:
                            missing = [f for f in required_fields if f not in entry]
                            self.log_result("Leaderboard Basic", False, f"Missing fields: {missing}", response)
                    else:
                        self.log_result("Leaderboard Basic", True, "Empty leaderboard (no scores yet)")
                else:
                    self.log_result("Leaderboard Basic", False, "Invalid response format", response)
            else:
                self.log_result("Leaderboard Basic", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Leaderboard Basic", False, f"Exception: {str(e)}")
    
    def test_leaderboard_filtering(self):
        """Test GET /api/scores/leaderboard with filters"""
        for mode in ['classic', 'time_race']:
            try:
                response = self.session.get(f"{BACKEND_URL}/scores/leaderboard?mode={mode}&limit=5")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        if len(data) > 0:
                            # Verify filtering
                            correct_mode = all(entry.get('mode') == mode for entry in data)
                            if correct_mode:
                                self.log_result(f"Leaderboard Filter {mode.title()}", True, f"Retrieved {len(data)} {mode} entries")
                            else:
                                self.log_result(f"Leaderboard Filter {mode.title()}", False, "Incorrect mode filtering", response)
                        else:
                            self.log_result(f"Leaderboard Filter {mode.title()}", True, f"No {mode} scores yet")
                    else:
                        self.log_result(f"Leaderboard Filter {mode.title()}", False, "Invalid response format", response)
                else:
                    self.log_result(f"Leaderboard Filter {mode.title()}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Leaderboard Filter {mode.title()}", False, f"Exception: {str(e)}")
    
    def test_daily_challenge(self):
        """Test GET /api/daily-challenge"""
        for lang in ['en', 'tr']:
            try:
                response = self.session.get(f"{BACKEND_URL}/daily-challenge?language={lang}")
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['date', 'completions', 'questions']
                    if all(field in data for field in required_fields):
                        questions = data['questions']
                        if isinstance(questions, list) and len(questions) > 0:
                            # Verify question structure
                            question = questions[0]
                            q_fields = ['id', 'category', 'difficulty', 'question', 'options', 'correct_answer']
                            if all(field in question for field in q_fields):
                                self.log_result(f"Daily Challenge {lang.upper()}", True, 
                                              f"Date: {data['date']}, Questions: {len(questions)}, Completions: {data['completions']}")
                            else:
                                self.log_result(f"Daily Challenge {lang.upper()}", False, "Invalid question structure", response)
                        else:
                            self.log_result(f"Daily Challenge {lang.upper()}", False, "No questions in challenge", response)
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_result(f"Daily Challenge {lang.upper()}", False, f"Missing fields: {missing}", response)
                else:
                    self.log_result(f"Daily Challenge {lang.upper()}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Daily Challenge {lang.upper()}", False, f"Exception: {str(e)}")
    
    def test_daily_challenge_complete(self):
        """Test POST /api/daily-challenge/complete"""
        try:
            response = self.session.post(f"{BACKEND_URL}/daily-challenge/complete")
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_result("Daily Challenge Complete", True, data['message'])
                else:
                    self.log_result("Daily Challenge Complete", False, "Missing message in response", response)
            else:
                self.log_result("Daily Challenge Complete", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Daily Challenge Complete", False, f"Exception: {str(e)}")
    
    def test_ai_question_generation(self):
        """Test POST /api/generate-question"""
        test_cases = [
            {"language": "en", "difficulty": "easy", "category": "logic"},
            {"language": "tr", "difficulty": "medium", "category": "math"},
            {"language": "de", "difficulty": "hard"}
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(f"{BACKEND_URL}/generate-question", json=case)
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['id', 'category', 'difficulty', 'question', 'options', 'correct_answer']
                    if all(field in data for field in required_fields):
                        # Verify options structure
                        options = data['options']
                        correct_answer = data['correct_answer']
                        if (isinstance(options, list) and len(options) == 4 and 
                            isinstance(correct_answer, int) and 0 <= correct_answer <= 3):
                            lang = case['language']
                            diff = case['difficulty']
                            self.log_result(f"AI Question Gen {lang.upper()}-{diff.title()}", True, 
                                          f"Generated question: {data['question'][:50]}...")
                        else:
                            self.log_result(f"AI Question Gen {case['language'].upper()}-{case['difficulty'].title()}", 
                                          False, "Invalid options or correct_answer format", response)
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_result(f"AI Question Gen {case['language'].upper()}-{case['difficulty'].title()}", 
                                      False, f"Missing fields: {missing}", response)
                else:
                    self.log_result(f"AI Question Gen {case['language'].upper()}-{case['difficulty'].title()}", 
                                  False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"AI Question Gen {case['language'].upper()}-{case['difficulty'].title()}", 
                              False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting IQ Game Backend API Tests")
        print("=" * 50)
        
        # Basic connectivity tests
        self.test_root_endpoint()
        self.test_health_endpoint()
        
        # Initialize questions (if needed)
        self.test_init_questions()
        
        # Question retrieval tests
        self.test_get_questions_basic()
        self.test_get_questions_all_languages()
        self.test_get_questions_by_difficulty()
        
        # Score system tests
        self.test_score_submission()
        self.test_leaderboard_basic()
        self.test_leaderboard_filtering()
        
        # Daily challenge tests
        self.test_daily_challenge()
        self.test_daily_challenge_complete()
        
        # AI generation tests
        self.test_ai_question_generation()
        
        # Summary
        print("=" * 50)
        print("🏁 Test Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = IQGameAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)