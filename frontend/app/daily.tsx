import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore, Question } from '../src/store/gameStore';
import { translations } from '../src/i18n/translations';
import { apiService } from '../src/services/api';
import { AdModal } from '../src/components/AdModal';

const { width } = Dimensions.get('window');

export default function DailyScreen() {
  const router = useRouter();
  const {
    language,
    playerName,
    setPlayerName,
    setQuestions,
    setGameMode,
    setDifficulty,
    resetGame,
  } = useGameStore();
  
  const t = translations[language];
  const [loading, setLoading] = useState(true);
  const [dailyData, setDailyData] = useState<{
    date: string;
    completions: number;
    questions: Question[];
  } | null>(null);
  const [name, setName] = useState(playerName);

  useEffect(() => {
    fetchDailyChallenge();
  }, []);

  const fetchDailyChallenge = async () => {
    try {
      setLoading(true);
      const data = await apiService.getDailyChallenge(language);
      setDailyData(data);
    } catch (error) {
      console.error('Failed to fetch daily challenge:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = () => {
    if (!dailyData || !name.trim()) return;
    
    resetGame();
    setPlayerName(name.trim());
    setQuestions(dailyData.questions);
    setGameMode('daily');
    setDifficulty('medium'); // Daily challenges are mixed difficulty
    
    router.push('/game');
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(language === 'tr' ? 'tr-TR' : language === 'de' ? 'de-DE' : language === 'fr' ? 'fr-FR' : language === 'es' ? 'es-ES' : 'en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>{t.dailyChallenge}</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={fetchDailyChallenge}
        >
          <Ionicons name="refresh" size={24} color="#4ECDC4" />
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
          <Text style={styles.loadingText}>{t.loading}</Text>
        </View>
      ) : dailyData ? (
        <ScrollView
          style={styles.content}
          contentContainerStyle={styles.contentContainer}
        >
          {/* Challenge Card */}
          <View style={styles.challengeCard}>
            <View style={styles.dateContainer}>
              <Ionicons name="calendar" size={32} color="#FFD93D" />
              <Text style={styles.dateText}>{formatDate(dailyData.date)}</Text>
            </View>

            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Ionicons name="help-circle" size={28} color="#4ECDC4" />
                <Text style={styles.statValue}>{dailyData.questions.length}</Text>
                <Text style={styles.statLabel}>{t.question}</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Ionicons name="people" size={28} color="#9B59B6" />
                <Text style={styles.statValue}>{dailyData.completions}</Text>
                <Text style={styles.statLabel}>{t.completions}</Text>
              </View>
            </View>
          </View>

          {/* Question Preview */}
          <View style={styles.previewCard}>
            <Text style={styles.previewTitle}>{t.todayChallenge}</Text>
            <View style={styles.categoriesContainer}>
              {Array.from(new Set(dailyData.questions.map(q => q.category))).map((cat, i) => (
                <View key={i} style={styles.categoryBadge}>
                  <Text style={styles.categoryText}>{cat}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Name Input */}
          <View style={styles.nameSection}>
            <Text style={styles.nameLabel}>{t.enterName}</Text>
            <View style={styles.nameInputContainer}>
              <Ionicons name="person" size={20} color="#666" />
              <TextInput
                style={styles.nameInput}
                value={name}
                onChangeText={setName}
                placeholder="Player"
                placeholderTextColor="#666"
                maxLength={20}
              />
            </View>
          </View>

          {/* Start Button */}
          <TouchableOpacity
            style={[
              styles.startButton,
              !name.trim() && styles.startButtonDisabled,
            ]}
            onPress={handleStart}
            disabled={!name.trim()}
          >
            <Ionicons name="play" size={24} color="#fff" />
            <Text style={styles.startButtonText}>{t.start}</Text>
          </TouchableOpacity>
        </ScrollView>
      ) : (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={60} color="#FF6B6B" />
          <Text style={styles.errorText}>{t.noQuestions}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={fetchDailyChallenge}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

// Import TextInput
import { TextInput } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#16213e',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  refreshButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#16213e',
    justifyContent: 'center',
    alignItems: 'center',
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
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
    gap: 20,
  },
  challengeCard: {
    backgroundColor: '#16213e',
    borderRadius: 20,
    padding: 24,
    borderWidth: 2,
    borderColor: '#FFD93D30',
  },
  dateContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  dateText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 12,
    textAlign: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    color: '#a0a0a0',
    fontSize: 12,
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 60,
    backgroundColor: '#333',
  },
  previewCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
  },
  previewTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoryBadge: {
    backgroundColor: '#0f3460',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  categoryText: {
    color: '#4ECDC4',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  nameSection: {
    gap: 8,
  },
  nameLabel: {
    color: '#a0a0a0',
    fontSize: 14,
    fontWeight: '600',
  },
  nameInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#16213e',
    borderRadius: 12,
    paddingHorizontal: 16,
    gap: 12,
  },
  nameInput: {
    flex: 1,
    paddingVertical: 16,
    fontSize: 16,
    color: '#fff',
  },
  startButton: {
    flexDirection: 'row',
    backgroundColor: '#4ECDC4',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginTop: 10,
  },
  startButtonDisabled: {
    backgroundColor: '#333',
  },
  startButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  errorText: {
    color: '#FF6B6B',
    fontSize: 18,
  },
  retryButton: {
    backgroundColor: '#4ECDC4',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
  },
  retryText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
