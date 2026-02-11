import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore } from '../src/store/gameStore';
import { translations } from '../src/i18n/translations';
import { apiService } from '../src/services/api';

const { width } = Dimensions.get('window');

export default function ResultScreen() {
  const router = useRouter();
  const {
    language,
    playerName,
    currentScore,
    correctAnswers,
    totalQuestions,
    difficulty,
    gameMode,
    timeBonus,
    resetGame,
  } = useGameStore();

  const t = translations[language];

  // Calculate IQ
  const calculateIQ = () => {
    if (totalQuestions === 0) return 100;
    
    const accuracy = correctAnswers / totalQuestions;
    let baseIQ = 85 + accuracy * 30;
    
    const difficultyBonus = { easy: 0, medium: 10, hard: 20 }[difficulty];
    const timeBonusIQ = Math.min(timeBonus / 10, 15);
    
    return Math.round(Math.max(70, Math.min(160, baseIQ + difficultyBonus + timeBonusIQ)));
  };

  const estimatedIQ = calculateIQ();

  // Submit score to backend
  useEffect(() => {
    const submitScore = async () => {
      try {
        await apiService.submitScore({
          user_name: playerName,
          score: currentScore,
          total_questions: totalQuestions,
          correct_answers: correctAnswers,
          difficulty,
          mode: gameMode,
          language,
        });
      } catch (error) {
        console.error('Failed to submit score:', error);
      }
    };

    submitScore();
  }, []);

  const getIQCategory = () => {
    if (estimatedIQ >= 140) return { label: 'Genius', color: '#FFD93D', icon: 'trophy' };
    if (estimatedIQ >= 120) return { label: 'Superior', color: '#4ECDC4', icon: 'star' };
    if (estimatedIQ >= 110) return { label: 'Above Average', color: '#4ECDC4', icon: 'trending-up' };
    if (estimatedIQ >= 90) return { label: 'Average', color: '#a0a0a0', icon: 'remove' };
    if (estimatedIQ >= 80) return { label: 'Below Average', color: '#FF6B6B', icon: 'trending-down' };
    return { label: 'Low', color: '#FF6B6B', icon: 'arrow-down' };
  };

  const iqCategory = getIQCategory();
  const accuracy = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;

  const handlePlayAgain = () => {
    resetGame();
    router.replace('/difficulty');
  };

  const handleMainMenu = () => {
    resetGame();
    router.replace('/');
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="ribbon" size={60} color="#FFD93D" />
        <Text style={styles.title}>{t.gameOver}</Text>
      </View>

      {/* IQ Display */}
      <View style={styles.iqContainer}>
        <View style={styles.iqCircle}>
          <Text style={styles.iqNumber}>{estimatedIQ}</Text>
          <Text style={styles.iqLabel}>{t.estimatedIQ}</Text>
        </View>
        <View style={[styles.categoryBadge, { backgroundColor: `${iqCategory.color}30` }]}>
          <Ionicons name={iqCategory.icon as any} size={20} color={iqCategory.color} />
          <Text style={[styles.categoryText, { color: iqCategory.color }]}>
            {iqCategory.label}
          </Text>
        </View>
      </View>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Ionicons name="star" size={32} color="#FFD93D" />
          <Text style={styles.statValue}>{currentScore}</Text>
          <Text style={styles.statLabel}>{t.score}</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="checkmark-circle" size={32} color="#4ECDC4" />
          <Text style={styles.statValue}>
            {correctAnswers}/{totalQuestions}
          </Text>
          <Text style={styles.statLabel}>{accuracy}%</Text>
        </View>
        {gameMode === 'time_race' && timeBonus > 0 && (
          <View style={styles.statCard}>
            <Ionicons name="timer" size={32} color="#9B59B6" />
            <Text style={styles.statValue}>+{timeBonus}s</Text>
            <Text style={styles.statLabel}>{t.timeBonus}</Text>
          </View>
        )}
      </View>

      {/* Difficulty Badge */}
      <View style={styles.difficultyContainer}>
        <Text style={styles.difficultyLabel}>
          {t[difficulty]} - {t[gameMode === 'time_race' ? 'timeRace' : gameMode === 'multiplayer' ? 'multiplayer' : 'classic']}
        </Text>
      </View>

      {/* Buttons */}
      <View style={styles.buttonsContainer}>
        <TouchableOpacity style={styles.primaryButton} onPress={handlePlayAgain}>
          <Ionicons name="refresh" size={24} color="#fff" />
          <Text style={styles.primaryButtonText}>{t.playAgain}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={handleMainMenu}>
          <Ionicons name="home" size={24} color="#fff" />
          <Text style={styles.secondaryButtonText}>{t.mainMenu}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.leaderboardButton}
          onPress={() => router.push('/leaderboard')}
        >
          <Ionicons name="podium" size={24} color="#FFD93D" />
          <Text style={styles.leaderboardButtonText}>{t.leaderboard}</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 10,
  },
  iqContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  iqCircle: {
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: '#16213e',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#4ECDC4',
  },
  iqNumber: {
    fontSize: 56,
    fontWeight: 'bold',
    color: '#fff',
  },
  iqLabel: {
    fontSize: 14,
    color: '#a0a0a0',
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginTop: 16,
    gap: 8,
  },
  categoryText: {
    fontSize: 16,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    marginBottom: 20,
  },
  statCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    minWidth: 100,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#a0a0a0',
    marginTop: 4,
  },
  difficultyContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  difficultyLabel: {
    fontSize: 14,
    color: '#666',
    backgroundColor: '#16213e',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  buttonsContainer: {
    gap: 12,
    marginTop: 'auto',
  },
  primaryButton: {
    flexDirection: 'row',
    backgroundColor: '#4ECDC4',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  primaryButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  secondaryButton: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  secondaryButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  leaderboardButton: {
    flexDirection: 'row',
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#FFD93D',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  leaderboardButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFD93D',
  },
});
