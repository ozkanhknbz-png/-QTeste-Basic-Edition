import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore, Difficulty, GameMode } from '../src/store/gameStore';
import { translations } from '../src/i18n/translations';

const { width } = Dimensions.get('window');

export default function DifficultyScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const mode = (params.mode as GameMode) || 'classic';
  
  const { 
    language, 
    playerName, 
    setPlayerName, 
    setDifficulty, 
    setGameMode,
    resetGame 
  } = useGameStore();
  
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>('easy');
  const [name, setName] = useState(playerName);
  const t = translations[language];

  const difficulties: { key: Difficulty; color: string; icon: string }[] = [
    { key: 'easy', color: '#4ECDC4', icon: 'star-outline' },
    { key: 'medium', color: '#FFD93D', icon: 'star-half' },
    { key: 'hard', color: '#FF6B6B', icon: 'star' },
  ];

  const handleStart = () => {
    if (!name.trim()) return;
    
    resetGame();
    setPlayerName(name.trim());
    setDifficulty(selectedDifficulty);
    setGameMode(mode);
    
    router.push('/game');
  };

  const getModeTitle = () => {
    switch (mode) {
      case 'time_race':
        return t.timeRace;
      case 'multiplayer':
        return t.multiplayer;
      default:
        return t.classic;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.content}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.title}>{getModeTitle()}</Text>
          <View style={{ width: 44 }} />
        </View>

        {/* Name Input */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.enterName}</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="Player"
            placeholderTextColor="#666"
            maxLength={20}
          />
        </View>

        {/* Difficulty Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t.selectDifficulty}</Text>
          <View style={styles.difficultyContainer}>
            {difficulties.map((diff) => (
              <TouchableOpacity
                key={diff.key}
                style={[
                  styles.difficultyCard,
                  selectedDifficulty === diff.key && {
                    borderColor: diff.color,
                    backgroundColor: `${diff.color}20`,
                  },
                ]}
                onPress={() => setSelectedDifficulty(diff.key)}
              >
                <Ionicons
                  name={diff.icon as any}
                  size={40}
                  color={selectedDifficulty === diff.key ? diff.color : '#666'}
                />
                <Text
                  style={[
                    styles.difficultyText,
                    selectedDifficulty === diff.key && { color: diff.color },
                  ]}
                >
                  {t[diff.key]}
                </Text>
                {selectedDifficulty === diff.key && (
                  <View style={[styles.checkmark, { backgroundColor: diff.color }]}>
                    <Ionicons name="checkmark" size={16} color="#fff" />
                  </View>
                )}
              </TouchableOpacity>
            ))}
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
          <Text style={styles.startButtonText}>{t.start}</Text>
          <Ionicons name="arrow-forward" size={24} color="#fff" />
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 30,
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#a0a0a0',
    marginBottom: 12,
  },
  input: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    fontSize: 18,
    color: '#fff',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  difficultyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  difficultyCard: {
    flex: 1,
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  difficultyText: {
    marginTop: 10,
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  checkmark: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  startButton: {
    flexDirection: 'row',
    backgroundColor: '#4ECDC4',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginTop: 'auto',
  },
  startButtonDisabled: {
    backgroundColor: '#333',
  },
  startButtonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
});
