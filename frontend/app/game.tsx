import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore, Question } from '../src/store/gameStore';
import { translations } from '../src/i18n/translations';
import { apiService } from '../src/services/api';
import { AdModal } from '../src/components/AdModal';

const { width } = Dimensions.get('window');

export default function GameScreen() {
  const router = useRouter();
  const {
    language,
    difficulty,
    gameMode,
    questions,
    currentQuestion,
    currentScore,
    correctAnswers,
    totalQuestions,
    timeLeft,
    setQuestions,
    answerQuestion,
    nextQuestion,
    addTimeBonus,
    decrementTime,
    setTimeLeft,
    startGame,
    endGame,
  } = useGameStore();

  const t = translations[language];
  const [loading, setLoading] = useState(true);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [generating, setGenerating] = useState(false);

  const scaleAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Load questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setLoading(true);
        const fetchedQuestions = await apiService.getQuestions(
          difficulty,
          undefined,
          language,
          10
        );
        setQuestions(fetchedQuestions);
        startGame();
        
        // Set initial time based on mode
        if (gameMode === 'time_race') {
          setTimeLeft(30); // Start with 30 seconds for time race
        }
      } catch (error) {
        console.error('Failed to load questions:', error);
      } finally {
        setLoading(false);
      }
    };

    loadQuestions();

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Timer for time race mode
  useEffect(() => {
    if (gameMode === 'time_race' && !loading && questions.length > 0) {
      timerRef.current = setInterval(() => {
        decrementTime();
      }, 1000);

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
      };
    }
  }, [gameMode, loading, questions]);

  // Check for game over in time race
  useEffect(() => {
    if (gameMode === 'time_race' && timeLeft <= 0 && !loading) {
      handleGameOver();
    }
  }, [timeLeft]);

  const handleGameOver = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    endGame();
    router.replace('/result');
  };

  const handleAnswer = async (answerIndex: number) => {
    if (selectedAnswer !== null || loading) return;

    setSelectedAnswer(answerIndex);
    const question = questions[currentQuestion];
    const correct = answerIndex === question.correct_answer;
    setIsCorrect(correct);
    setShowResult(true);

    // Calculate points based on difficulty
    const pointsMap = { easy: 10, medium: 20, hard: 30 };
    const points = pointsMap[difficulty];

    answerQuestion(correct, points);

    // Time bonus in time race mode
    if (gameMode === 'time_race' && correct) {
      const bonusTime = { easy: 5, medium: 7, hard: 10 }[difficulty];
      addTimeBonus(bonusTime);
    }

    // Animation
    Animated.sequence([
      Animated.spring(scaleAnim, {
        toValue: 1.05,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
      }),
    ]).start();

    // Wait and move to next question
    setTimeout(() => {
      if (currentQuestion + 1 >= totalQuestions) {
        handleGameOver();
      } else {
        setSelectedAnswer(null);
        setShowResult(false);
        nextQuestion();
      }
    }, 1500);
  };

  const generateAIQuestion = async () => {
    if (generating) return;
    
    try {
      setGenerating(true);
      const aiQuestion = await apiService.generateAIQuestion(
        language,
        difficulty
      );
      setQuestions([...questions, aiQuestion]);
    } catch (error) {
      console.error('Failed to generate AI question:', error);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
          <Text style={styles.loadingText}>{t.loading}</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (questions.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Ionicons name="alert-circle" size={60} color="#FF6B6B" />
          <Text style={styles.errorText}>{t.noQuestions}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => router.back()}
          >
            <Text style={styles.retryText}>{t.mainMenu}</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const question = questions[currentQuestion];
  const progress = (currentQuestion + 1) / totalQuestions;

  return (
    <SafeAreaView style={styles.container}>
      <AdModal />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.progressContainer}>
          <View style={[styles.progressBar, { width: `${progress * 100}%` }]} />
        </View>
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Ionicons name="help-circle" size={20} color="#4ECDC4" />
            <Text style={styles.statText}>
              {currentQuestion + 1}/{totalQuestions}
            </Text>
          </View>
          <View style={styles.stat}>
            <Ionicons name="star" size={20} color="#FFD93D" />
            <Text style={styles.statText}>{currentScore}</Text>
          </View>
          {gameMode === 'time_race' && (
            <View style={[styles.stat, timeLeft < 10 && styles.statDanger]}>
              <Ionicons
                name="timer"
                size={20}
                color={timeLeft < 10 ? '#FF6B6B' : '#4ECDC4'}
              />
              <Text
                style={[
                  styles.statText,
                  timeLeft < 10 && styles.statTextDanger,
                ]}
              >
                {timeLeft}s
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Question */}
      <Animated.View
        style={[styles.questionContainer, { transform: [{ scale: scaleAnim }] }]}
      >
        <View style={styles.categoryBadge}>
          <Text style={styles.categoryText}>
            {question.category.toUpperCase()}
          </Text>
        </View>
        <Text style={styles.questionText}>{question.question}</Text>
      </Animated.View>

      {/* Options */}
      <View style={styles.optionsContainer}>
        {question.options.map((option, index) => {
          let backgroundColor = '#16213e';
          let borderColor = 'transparent';

          if (showResult) {
            if (index === question.correct_answer) {
              backgroundColor = '#4ECDC420';
              borderColor = '#4ECDC4';
            } else if (index === selectedAnswer && !isCorrect) {
              backgroundColor = '#FF6B6B20';
              borderColor = '#FF6B6B';
            }
          } else if (selectedAnswer === index) {
            borderColor = '#4ECDC4';
          }

          return (
            <TouchableOpacity
              key={index}
              style={[
                styles.optionButton,
                { backgroundColor, borderColor },
              ]}
              onPress={() => handleAnswer(index)}
              disabled={selectedAnswer !== null}
            >
              <View style={styles.optionLetter}>
                <Text style={styles.optionLetterText}>
                  {String.fromCharCode(65 + index)}
                </Text>
              </View>
              <Text style={styles.optionText}>{option}</Text>
              {showResult && index === question.correct_answer && (
                <Ionicons name="checkmark-circle" size={24} color="#4ECDC4" />
              )}
              {showResult &&
                index === selectedAnswer &&
                !isCorrect && (
                  <Ionicons name="close-circle" size={24} color="#FF6B6B" />
                )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Result Indicator */}
      {showResult && (
        <View style={styles.resultContainer}>
          <Text
            style={[styles.resultText, { color: isCorrect ? '#4ECDC4' : '#FF6B6B' }]}
          >
            {isCorrect ? t.correct : t.incorrect}
          </Text>
          {gameMode === 'time_race' && isCorrect && (
            <Text style={styles.bonusText}>
              +{({ easy: 5, medium: 7, hard: 10 }[difficulty])}s {t.timeBonus}
            </Text>
          )}
        </View>
      )}

      {/* AI Generate Button for Multiplayer */}
      {gameMode === 'multiplayer' && (
        <TouchableOpacity
          style={styles.aiButton}
          onPress={generateAIQuestion}
          disabled={generating}
        >
          {generating ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Ionicons name="sparkles" size={20} color="#fff" />
          )}
          <Text style={styles.aiButtonText}>
            {generating ? t.generating : t.aiGenerated}
          </Text>
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    color: '#a0a0a0',
    fontSize: 16,
  },
  errorText: {
    color: '#FF6B6B',
    fontSize: 18,
    marginTop: 10,
  },
  retryButton: {
    backgroundColor: '#4ECDC4',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
  },
  retryText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    padding: 16,
  },
  progressContainer: {
    height: 6,
    backgroundColor: '#16213e',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#4ECDC4',
    borderRadius: 3,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#16213e',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  statDanger: {
    backgroundColor: '#FF6B6B20',
  },
  statText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  statTextDanger: {
    color: '#FF6B6B',
  },
  questionContainer: {
    backgroundColor: '#16213e',
    margin: 16,
    padding: 24,
    borderRadius: 20,
    minHeight: 150,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#0f3460',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 16,
  },
  categoryText: {
    color: '#4ECDC4',
    fontSize: 12,
    fontWeight: '600',
  },
  questionText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '500',
    lineHeight: 28,
  },
  optionsContainer: {
    padding: 16,
    gap: 12,
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 2,
    gap: 12,
  },
  optionLetter: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#0f3460',
    justifyContent: 'center',
    alignItems: 'center',
  },
  optionLetterText: {
    color: '#4ECDC4',
    fontSize: 16,
    fontWeight: 'bold',
  },
  optionText: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
  },
  resultContainer: {
    alignItems: 'center',
    padding: 16,
  },
  resultText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  bonusText: {
    color: '#4ECDC4',
    fontSize: 14,
    marginTop: 4,
  },
  aiButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#9B59B6',
    marginHorizontal: 16,
    padding: 12,
    borderRadius: 25,
    gap: 8,
  },
  aiButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
