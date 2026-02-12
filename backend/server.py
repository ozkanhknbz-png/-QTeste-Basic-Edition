from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, date
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'iq_game_db')]

# Create the main app
app = FastAPI(title="IQ Game API")
api_router = APIRouter(prefix="/api")

# Supported languages
LANGUAGES = ['tr', 'en', 'de', 'fr', 'es']
DIFFICULTIES = ['easy', 'medium', 'hard']

# Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # logic, math, pattern, verbal, spatial
    difficulty: str  # easy, medium, hard
    translations: Dict[str, Dict]  # {lang: {question, options, correct_answer}}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuestionCreate(BaseModel):
    category: str
    difficulty: str
    translations: Dict[str, Dict]

class UserScore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str
    score: int
    total_questions: int
    correct_answers: int
    difficulty: str
    mode: str  # classic, time_race, daily, multiplayer
    estimated_iq: int
    language: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScoreCreate(BaseModel):
    user_name: str
    score: int
    total_questions: int
    correct_answers: int
    difficulty: str
    mode: str
    language: str

class DailyChallenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    question_ids: List[str]
    completions: int = 0

class AIQuestionRequest(BaseModel):
    language: str
    difficulty: str
    category: Optional[str] = None

# Privacy Policy HTML
PRIVACY_POLICY_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IQ Game - Gizlilik Politikası / Privacy Policy</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
        }
        h1 { 
            color: #4ECDC4; 
            text-align: center; 
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            text-align: center;
            color: #a0a0a0;
            margin-bottom: 30px;
        }
        h2 { 
            color: #FFD93D; 
            margin-top: 30px; 
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        h3 {
            color: #4ECDC4;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        p, li { 
            color: #e0e0e0; 
            margin-bottom: 10px; 
        }
        ul { 
            padding-left: 25px; 
            margin-bottom: 15px;
        }
        li { margin-bottom: 8px; }
        .highlight {
            background: rgba(78, 205, 196, 0.2);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #4ECDC4;
            margin: 20px 0;
        }
        .contact {
            background: rgba(255, 217, 61, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            text-align: center;
        }
        .date {
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .lang-switch {
            text-align: center;
            margin-bottom: 20px;
        }
        .lang-switch a {
            color: #4ECDC4;
            text-decoration: none;
            margin: 0 10px;
            padding: 5px 15px;
            border: 1px solid #4ECDC4;
            border-radius: 20px;
        }
        .lang-switch a:hover {
            background: #4ECDC4;
            color: #1a1a2e;
        }
        .section { margin-bottom: 25px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 IQ Game</h1>
        <p class="subtitle">Gizlilik Politikası / Privacy Policy</p>
        
        <div class="lang-switch">
            <a href="#turkish">🇹🇷 Türkçe</a>
            <a href="#english">🇬🇧 English</a>
        </div>

        <!-- TURKISH VERSION -->
        <section id="turkish">
            <h2>🇹🇷 Gizlilik Politikası</h2>
            
            <div class="section">
                <h3>1. Giriş</h3>
                <p>IQ Game uygulamasını kullandığınız için teşekkür ederiz. Bu gizlilik politikası, uygulamamızı kullanırken kişisel verilerinizin nasıl toplandığını, kullanıldığını ve korunduğunu açıklamaktadır.</p>
            </div>

            <div class="section">
                <h3>2. Toplanan Bilgiler</h3>
                <p>Uygulamamız aşağıdaki bilgileri toplayabilir:</p>
                <ul>
                    <li><strong>Kullanıcı Adı:</strong> Oyun sırasında girdiğiniz takma ad</li>
                    <li><strong>Oyun Skorları:</strong> Oyun performansınız ve sonuçlarınız</li>
                    <li><strong>Dil Tercihi:</strong> Seçtiğiniz uygulama dili</li>
                    <li><strong>Cihaz Bilgileri:</strong> Cihaz türü ve işletim sistemi (anonim)</li>
                </ul>
            </div>

            <div class="section">
                <h3>3. Bilgilerin Kullanımı</h3>
                <p>Topladığımız bilgiler şu amaçlarla kullanılır:</p>
                <ul>
                    <li>Oyun deneyiminizi kişiselleştirmek</li>
                    <li>Liderlik tablosunu oluşturmak</li>
                    <li>Günlük zorlukları sunmak</li>
                    <li>Uygulama performansını iyileştirmek</li>
                </ul>
            </div>

            <div class="highlight">
                <h3>4. Reklam Hizmetleri</h3>
                <p>Uygulamamız Google AdMob reklam hizmetini kullanmaktadır. AdMob, size daha alakalı reklamlar göstermek için cihaz tanımlayıcıları ve kullanım verileri toplayabilir. Daha fazla bilgi için <a href="https://policies.google.com/privacy" style="color: #FFD93D;">Google Gizlilik Politikası</a>'nı inceleyebilirsiniz.</p>
            </div>

            <div class="section">
                <h3>5. Veri Güvenliği</h3>
                <p>Verilerinizin güvenliği bizim için önemlidir. Bilgilerinizi korumak için endüstri standardı güvenlik önlemleri kullanıyoruz. Ancak, internet üzerinden hiçbir veri aktarımının %100 güvenli olmadığını unutmayın.</p>
            </div>

            <div class="section">
                <h3>6. Çocukların Gizliliği</h3>
                <p>Uygulamamız tüm yaş gruplarına uygundur. 13 yaşından küçük çocuklardan bilerek kişisel bilgi toplamıyoruz. Ebeveynler veya veliler, çocuklarının kişisel bilgi sağladığını düşünüyorlarsa bizimle iletişime geçebilirler.</p>
            </div>

            <div class="section">
                <h3>7. Haklarınız</h3>
                <p>Aşağıdaki haklara sahipsiniz:</p>
                <ul>
                    <li>Verilerinize erişim talep etme</li>
                    <li>Verilerinizin düzeltilmesini isteme</li>
                    <li>Verilerinizin silinmesini talep etme</li>
                    <li>Veri işlemeye itiraz etme</li>
                </ul>
            </div>
        </section>

        <!-- ENGLISH VERSION -->
        <section id="english" style="margin-top: 50px; padding-top: 30px; border-top: 2px solid rgba(255,255,255,0.1);">
            <h2>🇬🇧 Privacy Policy</h2>
            
            <div class="section">
                <h3>1. Introduction</h3>
                <p>Thank you for using IQ Game. This privacy policy explains how your personal data is collected, used, and protected when you use our application.</p>
            </div>

            <div class="section">
                <h3>2. Information We Collect</h3>
                <p>Our application may collect the following information:</p>
                <ul>
                    <li><strong>Username:</strong> The nickname you enter during the game</li>
                    <li><strong>Game Scores:</strong> Your game performance and results</li>
                    <li><strong>Language Preference:</strong> Your selected app language</li>
                    <li><strong>Device Information:</strong> Device type and operating system (anonymous)</li>
                </ul>
            </div>

            <div class="section">
                <h3>3. How We Use Information</h3>
                <p>The information we collect is used to:</p>
                <ul>
                    <li>Personalize your gaming experience</li>
                    <li>Create the leaderboard</li>
                    <li>Provide daily challenges</li>
                    <li>Improve application performance</li>
                </ul>
            </div>

            <div class="highlight">
                <h3>4. Advertising Services</h3>
                <p>Our application uses Google AdMob advertising service. AdMob may collect device identifiers and usage data to show you more relevant ads. For more information, please review <a href="https://policies.google.com/privacy" style="color: #FFD93D;">Google's Privacy Policy</a>.</p>
            </div>

            <div class="section">
                <h3>5. Data Security</h3>
                <p>The security of your data is important to us. We use industry-standard security measures to protect your information. However, please note that no data transmission over the internet is 100% secure.</p>
            </div>

            <div class="section">
                <h3>6. Children's Privacy</h3>
                <p>Our application is suitable for all age groups. We do not knowingly collect personal information from children under 13. Parents or guardians who believe their child has provided personal information can contact us.</p>
            </div>

            <div class="section">
                <h3>7. Your Rights</h3>
                <p>You have the following rights:</p>
                <ul>
                    <li>Request access to your data</li>
                    <li>Request correction of your data</li>
                    <li>Request deletion of your data</li>
                    <li>Object to data processing</li>
                </ul>
            </div>
        </section>

        <div class="contact">
            <h3>📧 İletişim / Contact</h3>
            <p>Sorularınız için / For questions:</p>
            <p><strong>iqgame.app@gmail.com</strong></p>
        </div>

        <p class="date">Son Güncelleme / Last Updated: Şubat 2025 / February 2025</p>
    </div>
</body>
</html>
"""

# Helper function to calculate IQ
def calculate_iq(correct: int, total: int, difficulty: str, time_bonus: int = 0) -> int:
    if total == 0:
        return 100
    
    accuracy = correct / total
    
    # Base IQ calculation
    base_iq = 85 + (accuracy * 30)  # 85-115 range for accuracy
    
    # Difficulty bonus
    difficulty_bonus = {'easy': 0, 'medium': 10, 'hard': 20}
    bonus = difficulty_bonus.get(difficulty, 0)
    
    # Time bonus (for time race mode)
    time_iq_bonus = min(time_bonus // 10, 15)  # Max 15 points from time
    
    estimated_iq = int(base_iq + bonus + time_iq_bonus)
    
    # Clamp between 70 and 160
    return max(70, min(160, estimated_iq))

# Routes
@api_router.get("/")
async def root():
    return {"message": "IQ Game API", "version": "1.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# Question endpoints
@api_router.get("/questions")
async def get_questions(
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    language: str = 'en',
    limit: int = 10
):
    query = {}
    if difficulty:
        query['difficulty'] = difficulty
    if category:
        query['category'] = category
    
    questions = await db.questions.find(query).to_list(limit * 3)
    
    # Shuffle and limit
    random.shuffle(questions)
    questions = questions[:limit]
    
    # Format for response
    result = []
    for q in questions:
        trans = q.get('translations', {}).get(language, q.get('translations', {}).get('en', {}))
        result.append({
            'id': q['id'],
            'category': q['category'],
            'difficulty': q['difficulty'],
            'question': trans.get('question', ''),
            'options': trans.get('options', []),
            'correct_answer': trans.get('correct_answer', 0)
        })
    
    return result

@api_router.post("/questions")
async def create_question(question: QuestionCreate):
    q_dict = question.dict()
    q_dict['id'] = str(uuid.uuid4())
    q_dict['created_at'] = datetime.utcnow()
    await db.questions.insert_one(q_dict)
    return {"id": q_dict['id'], "message": "Question created"}

@api_router.post("/questions/bulk")
async def create_bulk_questions(questions: List[QuestionCreate]):
    for question in questions:
        q_dict = question.dict()
        q_dict['id'] = str(uuid.uuid4())
        q_dict['created_at'] = datetime.utcnow()
        await db.questions.insert_one(q_dict)
    return {"message": f"{len(questions)} questions created"}

# Score endpoints
@api_router.post("/scores")
async def submit_score(score_data: ScoreCreate):
    estimated_iq = calculate_iq(
        score_data.correct_answers,
        score_data.total_questions,
        score_data.difficulty
    )
    
    score_dict = score_data.dict()
    score_dict['id'] = str(uuid.uuid4())
    score_dict['estimated_iq'] = estimated_iq
    score_dict['created_at'] = datetime.utcnow()
    
    await db.scores.insert_one(score_dict)
    
    return {
        "id": score_dict['id'],
        "estimated_iq": estimated_iq,
        "message": "Score submitted"
    }

@api_router.get("/scores/leaderboard")
async def get_leaderboard(
    mode: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 20
):
    query = {}
    if mode:
        query['mode'] = mode
    if difficulty:
        query['difficulty'] = difficulty
    
    scores = await db.scores.find(query).sort('estimated_iq', -1).to_list(limit)
    
    return [{
        'rank': i + 1,
        'user_name': s['user_name'],
        'score': s['score'],
        'estimated_iq': s['estimated_iq'],
        'difficulty': s['difficulty'],
        'mode': s['mode'],
        'date': s['created_at'].strftime('%Y-%m-%d') if s.get('created_at') else ''
    } for i, s in enumerate(scores)]

# Daily Challenge endpoints
@api_router.get("/daily-challenge")
async def get_daily_challenge(language: str = 'en'):
    today = date.today().isoformat()
    
    # Check if challenge exists for today
    challenge = await db.daily_challenges.find_one({'date': today})
    
    if not challenge:
        # Create new daily challenge
        all_questions = await db.questions.find().to_list(100)
        if len(all_questions) < 10:
            raise HTTPException(status_code=404, detail="Not enough questions in database")
        
        random.shuffle(all_questions)
        selected = all_questions[:10]
        question_ids = [q['id'] for q in selected]
        
        challenge = {
            'id': str(uuid.uuid4()),
            'date': today,
            'question_ids': question_ids,
            'completions': 0
        }
        await db.daily_challenges.insert_one(challenge)
    
    # Get questions for challenge
    questions = await db.questions.find({'id': {'$in': challenge['question_ids']}}).to_list(10)
    
    result = []
    for q in questions:
        trans = q.get('translations', {}).get(language, q.get('translations', {}).get('en', {}))
        result.append({
            'id': q['id'],
            'category': q['category'],
            'difficulty': q['difficulty'],
            'question': trans.get('question', ''),
            'options': trans.get('options', []),
            'correct_answer': trans.get('correct_answer', 0)
        })
    
    return {
        'date': today,
        'completions': challenge.get('completions', 0),
        'questions': result
    }

@api_router.post("/daily-challenge/complete")
async def complete_daily_challenge():
    today = date.today().isoformat()
    await db.daily_challenges.update_one(
        {'date': today},
        {'$inc': {'completions': 1}}
    )
    return {"message": "Challenge completion recorded"}

# AI Question Generation
@api_router.post("/generate-question")
async def generate_ai_question(request: AIQuestionRequest):
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        language_names = {
            'tr': 'Turkish',
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish'
        }
        
        difficulty_desc = {
            'easy': 'simple and straightforward',
            'medium': 'moderately challenging',
            'hard': 'complex and challenging'
        }
        
        lang_name = language_names.get(request.language, 'English')
        diff_desc = difficulty_desc.get(request.difficulty, 'moderately challenging')
        
        prompt = f"""Generate a unique IQ test question in {lang_name}. The question should be {diff_desc}.

Rules:
1. Create a logic, pattern recognition, or mathematical reasoning question
2. Provide exactly 4 answer options
3. Indicate which option (0-3) is correct

Respond in this exact JSON format:
{{
  "question": "Your question here in {lang_name}",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0
}}

Only respond with the JSON, nothing else."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"iq-gen-{uuid.uuid4()}",
            system_message="You are an IQ test question generator. Generate creative and unique questions."
        ).with_model("openai", "gpt-4.1-mini")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse response
        import json
        # Clean response
        response_clean = response.strip()
        if response_clean.startswith('```json'):
            response_clean = response_clean[7:]
        if response_clean.startswith('```'):
            response_clean = response_clean[3:]
        if response_clean.endswith('```'):
            response_clean = response_clean[:-3]
        
        question_data = json.loads(response_clean.strip())
        
        return {
            'id': str(uuid.uuid4()),
            'category': 'ai_generated',
            'difficulty': request.difficulty,
            'question': question_data['question'],
            'options': question_data['options'],
            'correct_answer': question_data['correct_answer']
        }
        
    except Exception as e:
        logging.error(f"AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

# Initialize sample questions
@api_router.post("/init-questions")
async def init_sample_questions():
    # Check if questions already exist
    count = await db.questions.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} questions"}
    
    sample_questions = [
        # Logic Questions - Easy
        {
            "category": "logic",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Bir çiftçinin 17 koyunu var. 9 tanesi hariç hepsi öldü. Kaç koyun kaldı?", "options": ["8", "9", "17", "0"], "correct_answer": 1},
                "en": {"question": "A farmer has 17 sheep. All but 9 die. How many sheep are left?", "options": ["8", "9", "17", "0"], "correct_answer": 1},
                "de": {"question": "Ein Bauer hat 17 Schafe. Alle außer 9 sterben. Wie viele Schafe bleiben übrig?", "options": ["8", "9", "17", "0"], "correct_answer": 1},
                "fr": {"question": "Un fermier a 17 moutons. Tous sauf 9 meurent. Combien de moutons reste-t-il?", "options": ["8", "9", "17", "0"], "correct_answer": 1},
                "es": {"question": "Un granjero tiene 17 ovejas. Todas menos 9 mueren. ¿Cuántas ovejas quedan?", "options": ["8", "9", "17", "0"], "correct_answer": 1}
            }
        },
        # Math Questions - Easy
        {
            "category": "math",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "12 + 8 × 2 = ?", "options": ["40", "28", "32", "20"], "correct_answer": 1},
                "en": {"question": "12 + 8 × 2 = ?", "options": ["40", "28", "32", "20"], "correct_answer": 1},
                "de": {"question": "12 + 8 × 2 = ?", "options": ["40", "28", "32", "20"], "correct_answer": 1},
                "fr": {"question": "12 + 8 × 2 = ?", "options": ["40", "28", "32", "20"], "correct_answer": 1},
                "es": {"question": "12 + 8 × 2 = ?", "options": ["40", "28", "32", "20"], "correct_answer": 1}
            }
        },
        # Pattern Questions - Easy
        {
            "category": "pattern",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Sıradaki sayı nedir? 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "correct_answer": 1},
                "en": {"question": "What is the next number? 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "correct_answer": 1},
                "de": {"question": "Was ist die nächste Zahl? 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "correct_answer": 1},
                "fr": {"question": "Quel est le prochain nombre? 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "correct_answer": 1},
                "es": {"question": "¿Cuál es el siguiente número? 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "correct_answer": 1}
            }
        },
        # Logic Questions - Medium
        {
            "category": "logic",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir odada 6 kişi var. Her biri diğerleriyle el sıkışıyor. Toplam kaç el sıkışma olur?", "options": ["30", "15", "12", "6"], "correct_answer": 1},
                "en": {"question": "There are 6 people in a room. Each one shakes hands with everyone else. How many handshakes occur?", "options": ["30", "15", "12", "6"], "correct_answer": 1},
                "de": {"question": "In einem Raum sind 6 Personen. Jeder gibt jedem anderen die Hand. Wie viele Händedrücke gibt es?", "options": ["30", "15", "12", "6"], "correct_answer": 1},
                "fr": {"question": "Il y a 6 personnes dans une pièce. Chacun serre la main de tous les autres. Combien de poignées de main y a-t-il?", "options": ["30", "15", "12", "6"], "correct_answer": 1},
                "es": {"question": "Hay 6 personas en una habitación. Cada una le da la mano a todas las demás. ¿Cuántos apretones de manos hay?", "options": ["30", "15", "12", "6"], "correct_answer": 1}
            }
        },
        # Math Questions - Medium
        {
            "category": "math",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir sayının %25'i 20'dir. Bu sayı kaçtır?", "options": ["5", "80", "100", "45"], "correct_answer": 1},
                "en": {"question": "25% of a number is 20. What is the number?", "options": ["5", "80", "100", "45"], "correct_answer": 1},
                "de": {"question": "25% einer Zahl ist 20. Was ist die Zahl?", "options": ["5", "80", "100", "45"], "correct_answer": 1},
                "fr": {"question": "25% d'un nombre est 20. Quel est ce nombre?", "options": ["5", "80", "100", "45"], "correct_answer": 1},
                "es": {"question": "El 25% de un número es 20. ¿Cuál es el número?", "options": ["5", "80", "100", "45"], "correct_answer": 1}
            }
        },
        # Pattern Questions - Medium
        {
            "category": "pattern",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Sıradaki sayı nedir? 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "correct_answer": 2},
                "en": {"question": "What is the next number? 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "correct_answer": 2},
                "de": {"question": "Was ist die nächste Zahl? 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "correct_answer": 2},
                "fr": {"question": "Quel est le prochain nombre? 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "correct_answer": 2},
                "es": {"question": "¿Cuál es el siguiente número? 1, 1, 2, 3, 5, 8, ?", "options": ["11", "12", "13", "14"], "correct_answer": 2}
            }
        },
        # Verbal Questions - Medium
        {
            "category": "verbal",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "DOKTOR kelimesini tersten yazınca hangi harfle başlar?", "options": ["D", "R", "O", "K"], "correct_answer": 1},
                "en": {"question": "If you reverse DOCTOR, what letter does it start with?", "options": ["D", "R", "O", "C"], "correct_answer": 1},
                "de": {"question": "Wenn Sie ARZT rückwärts schreiben, mit welchem Buchstaben beginnt es?", "options": ["A", "T", "Z", "R"], "correct_answer": 1},
                "fr": {"question": "Si vous inversez MÉDECIN, par quelle lettre commence-t-il?", "options": ["M", "N", "I", "E"], "correct_answer": 1},
                "es": {"question": "Si inviertes DOCTOR, ¿con qué letra empieza?", "options": ["D", "R", "O", "C"], "correct_answer": 1}
            }
        },
        # Logic Questions - Hard
        {
            "category": "logic",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "Ali, Berk'ten uzun. Can, Ali'den kısa ama Deniz'den uzun. En kısa kim?", "options": ["Ali", "Berk", "Can", "Deniz"], "correct_answer": 3},
                "en": {"question": "Ali is taller than Berk. Can is shorter than Ali but taller than Deniz. Who is the shortest?", "options": ["Ali", "Berk", "Can", "Deniz"], "correct_answer": 3},
                "de": {"question": "Ali ist größer als Berk. Can ist kleiner als Ali, aber größer als Deniz. Wer ist der Kleinste?", "options": ["Ali", "Berk", "Can", "Deniz"], "correct_answer": 3},
                "fr": {"question": "Ali est plus grand que Berk. Can est plus petit qu'Ali mais plus grand que Deniz. Qui est le plus petit?", "options": ["Ali", "Berk", "Can", "Deniz"], "correct_answer": 3},
                "es": {"question": "Ali es más alto que Berk. Can es más bajo que Ali pero más alto que Deniz. ¿Quién es el más bajo?", "options": ["Ali", "Berk", "Can", "Deniz"], "correct_answer": 3}
            }
        },
        # Math Questions - Hard
        {
            "category": "math",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "√144 + 3³ = ?", "options": ["39", "30", "27", "45"], "correct_answer": 0},
                "en": {"question": "√144 + 3³ = ?", "options": ["39", "30", "27", "45"], "correct_answer": 0},
                "de": {"question": "√144 + 3³ = ?", "options": ["39", "30", "27", "45"], "correct_answer": 0},
                "fr": {"question": "√144 + 3³ = ?", "options": ["39", "30", "27", "45"], "correct_answer": 0},
                "es": {"question": "√144 + 3³ = ?", "options": ["39", "30", "27", "45"], "correct_answer": 0}
            }
        },
        # Pattern Questions - Hard
        {
            "category": "pattern",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "Sıradaki sayı nedir? 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "correct_answer": 1},
                "en": {"question": "What is the next number? 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "correct_answer": 1},
                "de": {"question": "Was ist die nächste Zahl? 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "correct_answer": 1},
                "fr": {"question": "Quel est le prochain nombre? 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "correct_answer": 1},
                "es": {"question": "¿Cuál es el siguiente número? 2, 6, 12, 20, 30, ?", "options": ["40", "42", "44", "36"], "correct_answer": 1}
            }
        },
        # Spatial Questions - Easy
        {
            "category": "spatial",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Bir küpün kaç yüzeyi vardır?", "options": ["4", "6", "8", "12"], "correct_answer": 1},
                "en": {"question": "How many faces does a cube have?", "options": ["4", "6", "8", "12"], "correct_answer": 1},
                "de": {"question": "Wie viele Flächen hat ein Würfel?", "options": ["4", "6", "8", "12"], "correct_answer": 1},
                "fr": {"question": "Combien de faces a un cube?", "options": ["4", "6", "8", "12"], "correct_answer": 1},
                "es": {"question": "¿Cuántas caras tiene un cubo?", "options": ["4", "6", "8", "12"], "correct_answer": 1}
            }
        },
        # Spatial Questions - Medium
        {
            "category": "spatial",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir dikdörtgenin köşegenlerinin sayısı kaçtır?", "options": ["1", "2", "4", "Sonsuz"], "correct_answer": 1},
                "en": {"question": "How many diagonals does a rectangle have?", "options": ["1", "2", "4", "Infinite"], "correct_answer": 1},
                "de": {"question": "Wie viele Diagonalen hat ein Rechteck?", "options": ["1", "2", "4", "Unendlich"], "correct_answer": 1},
                "fr": {"question": "Combien de diagonales a un rectangle?", "options": ["1", "2", "4", "Infini"], "correct_answer": 1},
                "es": {"question": "¿Cuántas diagonales tiene un rectángulo?", "options": ["1", "2", "4", "Infinito"], "correct_answer": 1}
            }
        },
        # Spatial Questions - Hard
        {
            "category": "spatial",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "Bir ikosahedronun (düzgün yirmi yüzlü) kaç köşesi vardır?", "options": ["10", "12", "20", "30"], "correct_answer": 1},
                "en": {"question": "How many vertices does an icosahedron have?", "options": ["10", "12", "20", "30"], "correct_answer": 1},
                "de": {"question": "Wie viele Ecken hat ein Ikosaeder?", "options": ["10", "12", "20", "30"], "correct_answer": 1},
                "fr": {"question": "Combien de sommets a un icosaèdre?", "options": ["10", "12", "20", "30"], "correct_answer": 1},
                "es": {"question": "¿Cuántos vértices tiene un icosaedro?", "options": ["10", "12", "20", "30"], "correct_answer": 1}
            }
        },
        # Logic - Easy
        {
            "category": "logic",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Ayın son günü 31 ise, ayın ilk günü hangi gündür?", "options": ["Pazartesi", "1", "31", "Bilinmiyor"], "correct_answer": 1},
                "en": {"question": "If the last day of a month is 31, what is the first day of that month?", "options": ["Monday", "1", "31", "Unknown"], "correct_answer": 1},
                "de": {"question": "Wenn der letzte Tag des Monats der 31. ist, welcher ist der erste Tag?", "options": ["Montag", "1", "31", "Unbekannt"], "correct_answer": 1},
                "fr": {"question": "Si le dernier jour du mois est le 31, quel est le premier jour?", "options": ["Lundi", "1", "31", "Inconnu"], "correct_answer": 1},
                "es": {"question": "Si el último día del mes es 31, ¿cuál es el primer día?", "options": ["Lunes", "1", "31", "Desconocido"], "correct_answer": 1}
            }
        },
        # Math - Easy
        {
            "category": "math",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "100'ün yarısının yarısı kaçtır?", "options": ["50", "25", "12.5", "10"], "correct_answer": 1},
                "en": {"question": "What is half of half of 100?", "options": ["50", "25", "12.5", "10"], "correct_answer": 1},
                "de": {"question": "Was ist die Hälfte von der Hälfte von 100?", "options": ["50", "25", "12.5", "10"], "correct_answer": 1},
                "fr": {"question": "Quelle est la moitié de la moitié de 100?", "options": ["50", "25", "12.5", "10"], "correct_answer": 1},
                "es": {"question": "¿Cuál es la mitad de la mitad de 100?", "options": ["50", "25", "12.5", "10"], "correct_answer": 1}
            }
        },
        # Verbal - Easy
        {
            "category": "verbal",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "'ELMA' kelimesinde kaç sesli harf var?", "options": ["1", "2", "3", "4"], "correct_answer": 1},
                "en": {"question": "How many vowels are in the word 'APPLE'?", "options": ["1", "2", "3", "4"], "correct_answer": 1},
                "de": {"question": "Wie viele Vokale hat das Wort 'APFEL'?", "options": ["1", "2", "3", "4"], "correct_answer": 1},
                "fr": {"question": "Combien de voyelles y a-t-il dans le mot 'POMME'?", "options": ["1", "2", "3", "4"], "correct_answer": 1},
                "es": {"question": "¿Cuántas vocales hay en la palabra 'MANZANA'?", "options": ["2", "3", "4", "5"], "correct_answer": 2}
            }
        },
        # Logic - Medium
        {
            "category": "logic",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir saatte dakika yelkovanı, saat yelkovanını kaç kez geçer?", "options": ["1", "2", "12", "60"], "correct_answer": 0},
                "en": {"question": "How many times does the minute hand pass the hour hand in one hour?", "options": ["1", "2", "12", "60"], "correct_answer": 0},
                "de": {"question": "Wie oft überholt der Minutenzeiger den Stundenzeiger in einer Stunde?", "options": ["1", "2", "12", "60"], "correct_answer": 0},
                "fr": {"question": "Combien de fois l'aiguille des minutes dépasse-t-elle l'aiguille des heures en une heure?", "options": ["1", "2", "12", "60"], "correct_answer": 0},
                "es": {"question": "¿Cuántas veces pasa la manecilla de los minutos a la manecilla de las horas en una hora?", "options": ["1", "2", "12", "60"], "correct_answer": 0}
            }
        },
        # Pattern - Easy
        {
            "category": "pattern",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Sıradaki harf nedir? A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct_answer": 1},
                "en": {"question": "What is the next letter? A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct_answer": 1},
                "de": {"question": "Welcher ist der nächste Buchstabe? A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct_answer": 1},
                "fr": {"question": "Quelle est la prochaine lettre? A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct_answer": 1},
                "es": {"question": "¿Cuál es la siguiente letra? A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct_answer": 1}
            }
        },
        # Math - Hard
        {
            "category": "math",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "2^10 kaçtır?", "options": ["512", "1024", "2048", "256"], "correct_answer": 1},
                "en": {"question": "What is 2^10?", "options": ["512", "1024", "2048", "256"], "correct_answer": 1},
                "de": {"question": "Was ist 2^10?", "options": ["512", "1024", "2048", "256"], "correct_answer": 1},
                "fr": {"question": "Combien vaut 2^10?", "options": ["512", "1024", "2048", "256"], "correct_answer": 1},
                "es": {"question": "¿Cuánto es 2^10?", "options": ["512", "1024", "2048", "256"], "correct_answer": 1}
            }
        },
        # Verbal - Hard
        {
            "category": "verbal",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "'Anagram' kelimesi başka hangi kelimeyle anagram oluşturur?", "options": ["Nağmara", "Mangara", "Gramana", "Hepsi"], "correct_answer": 3},
                "en": {"question": "Which word is NOT an anagram of 'LISTEN'?", "options": ["SILENT", "ENLIST", "TINSEL", "NESTLE"], "correct_answer": 3},
                "de": {"question": "Welches Wort ist KEIN Anagramm von 'REGAL'?", "options": ["LAGER", "LARGE", "ARGLE", "EAGLE"], "correct_answer": 3},
                "fr": {"question": "Quel mot n'est PAS un anagramme de 'CHIEN'?", "options": ["NICHE", "CHINE", "NICHE", "CHANT"], "correct_answer": 3},
                "es": {"question": "¿Qué palabra NO es un anagrama de 'AMOR'?", "options": ["ROMA", "MORA", "OMAR", "ARMA"], "correct_answer": 3}
            }
        },
        # Logic - Hard
        {
            "category": "logic",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "3 tavuk 3 günde 3 yumurta bırakırsa, 12 tavuk 12 günde kaç yumurta bırakır?", "options": ["12", "36", "48", "144"], "correct_answer": 2},
                "en": {"question": "If 3 hens lay 3 eggs in 3 days, how many eggs will 12 hens lay in 12 days?", "options": ["12", "36", "48", "144"], "correct_answer": 2},
                "de": {"question": "Wenn 3 Hühner in 3 Tagen 3 Eier legen, wie viele Eier legen 12 Hühner in 12 Tagen?", "options": ["12", "36", "48", "144"], "correct_answer": 2},
                "fr": {"question": "Si 3 poules pondent 3 œufs en 3 jours, combien d'œufs 12 poules pondront-elles en 12 jours?", "options": ["12", "36", "48", "144"], "correct_answer": 2},
                "es": {"question": "Si 3 gallinas ponen 3 huevos en 3 días, ¿cuántos huevos pondrán 12 gallinas en 12 días?", "options": ["12", "36", "48", "144"], "correct_answer": 2}
            }
        },
        # Pattern - Hard
        {
            "category": "pattern",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "Sıradaki sayı nedir? 1, 4, 9, 16, 25, ?", "options": ["30", "36", "49", "64"], "correct_answer": 1},
                "en": {"question": "What is the next number? 1, 4, 9, 16, 25, ?", "options": ["30", "36", "49", "64"], "correct_answer": 1},
                "de": {"question": "Was ist die nächste Zahl? 1, 4, 9, 16, 25, ?", "options": ["30", "36", "49", "64"], "correct_answer": 1},
                "fr": {"question": "Quel est le prochain nombre? 1, 4, 9, 16, 25, ?", "options": ["30", "36", "49", "64"], "correct_answer": 1},
                "es": {"question": "¿Cuál es el siguiente número? 1, 4, 9, 16, 25, ?", "options": ["30", "36", "49", "64"], "correct_answer": 1}
            }
        },
        # Additional questions
        {
            "category": "logic",
            "difficulty": "easy",
            "translations": {
                "tr": {"question": "Hangi ay 28 gün çeker?", "options": ["Şubat", "Hepsi", "Hiçbiri", "Sadece artık yıllarda"], "correct_answer": 1},
                "en": {"question": "Which month has 28 days?", "options": ["February", "All of them", "None", "Only in leap years"], "correct_answer": 1},
                "de": {"question": "Welcher Monat hat 28 Tage?", "options": ["Februar", "Alle", "Keiner", "Nur in Schaltjahren"], "correct_answer": 1},
                "fr": {"question": "Quel mois a 28 jours?", "options": ["Février", "Tous", "Aucun", "Seulement les années bissextiles"], "correct_answer": 1},
                "es": {"question": "¿Qué mes tiene 28 días?", "options": ["Febrero", "Todos", "Ninguno", "Solo en años bisiestos"], "correct_answer": 1}
            }
        },
        {
            "category": "math",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir eşkenar üçgenin her iç açısı kaç derecedir?", "options": ["45°", "60°", "90°", "120°"], "correct_answer": 1},
                "en": {"question": "What is each interior angle of an equilateral triangle?", "options": ["45°", "60°", "90°", "120°"], "correct_answer": 1},
                "de": {"question": "Wie groß ist jeder Innenwinkel eines gleichseitigen Dreiecks?", "options": ["45°", "60°", "90°", "120°"], "correct_answer": 1},
                "fr": {"question": "Quelle est la mesure de chaque angle intérieur d'un triangle équilatéral?", "options": ["45°", "60°", "90°", "120°"], "correct_answer": 1},
                "es": {"question": "¿Cuánto mide cada ángulo interior de un triángulo equilátero?", "options": ["45°", "60°", "90°", "120°"], "correct_answer": 1}
            }
        },
        {
            "category": "verbal",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "'Kitap' kelimesinin zıt anlamlısı nedir?", "options": ["Defter", "Kalem", "Yoktur", "Sayfa"], "correct_answer": 2},
                "en": {"question": "Which word is the opposite of 'HAPPY'?", "options": ["Sad", "Angry", "Excited", "Calm"], "correct_answer": 0},
                "de": {"question": "Was ist das Gegenteil von 'GLÜCKLICH'?", "options": ["Traurig", "Wütend", "Aufgeregt", "Ruhig"], "correct_answer": 0},
                "fr": {"question": "Quel est le contraire de 'HEUREUX'?", "options": ["Triste", "En colère", "Excité", "Calme"], "correct_answer": 0},
                "es": {"question": "¿Cuál es el opuesto de 'FELIZ'?", "options": ["Triste", "Enojado", "Emocionado", "Tranquilo"], "correct_answer": 0}
            }
        },
        {
            "category": "spatial",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Bir piramit tabanı kare ise kaç kenarı vardır?", "options": ["4", "6", "8", "5"], "correct_answer": 2},
                "en": {"question": "How many edges does a square-based pyramid have?", "options": ["4", "6", "8", "5"], "correct_answer": 2},
                "de": {"question": "Wie viele Kanten hat eine quadratische Pyramide?", "options": ["4", "6", "8", "5"], "correct_answer": 2},
                "fr": {"question": "Combien d'arêtes a une pyramide à base carrée?", "options": ["4", "6", "8", "5"], "correct_answer": 2},
                "es": {"question": "¿Cuántas aristas tiene una pirámide de base cuadrada?", "options": ["4", "6", "8", "5"], "correct_answer": 2}
            }
        },
        {
            "category": "logic",
            "difficulty": "medium",
            "translations": {
                "tr": {"question": "Tom, Jerry'den büyük. Jerry, Spike'tan büyük. Spike, Tom'dan büyük olabilir mi?", "options": ["Evet", "Hayır", "Belki", "Bilgi yetersiz"], "correct_answer": 1},
                "en": {"question": "Tom is older than Jerry. Jerry is older than Spike. Can Spike be older than Tom?", "options": ["Yes", "No", "Maybe", "Insufficient info"], "correct_answer": 1},
                "de": {"question": "Tom ist älter als Jerry. Jerry ist älter als Spike. Kann Spike älter als Tom sein?", "options": ["Ja", "Nein", "Vielleicht", "Nicht genug Info"], "correct_answer": 1},
                "fr": {"question": "Tom est plus vieux que Jerry. Jerry est plus vieux que Spike. Spike peut-il être plus vieux que Tom?", "options": ["Oui", "Non", "Peut-être", "Info insuffisante"], "correct_answer": 1},
                "es": {"question": "Tom es mayor que Jerry. Jerry es mayor que Spike. ¿Puede Spike ser mayor que Tom?", "options": ["Sí", "No", "Quizás", "Info insuficiente"], "correct_answer": 1}
            }
        },
        {
            "category": "math",
            "difficulty": "hard",
            "translations": {
                "tr": {"question": "5! (5 faktöriyel) kaçtır?", "options": ["25", "60", "120", "720"], "correct_answer": 2},
                "en": {"question": "What is 5! (5 factorial)?", "options": ["25", "60", "120", "720"], "correct_answer": 2},
                "de": {"question": "Was ist 5! (5 Fakultät)?", "options": ["25", "60", "120", "720"], "correct_answer": 2},
                "fr": {"question": "Combien vaut 5! (factorielle de 5)?", "options": ["25", "60", "120", "720"], "correct_answer": 2},
                "es": {"question": "¿Cuánto es 5! (factorial de 5)?", "options": ["25", "60", "120", "720"], "correct_answer": 2}
            }
        }
    ]
    
    for q in sample_questions:
        q['id'] = str(uuid.uuid4())
        q['created_at'] = datetime.utcnow()
        await db.questions.insert_one(q)
    
    return {"message": f"Created {len(sample_questions)} sample questions"}

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
