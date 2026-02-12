import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  ActivityIndicator,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore } from '../src/store/gameStore';
import { translations, LANGUAGES } from '../src/i18n/translations';
import { apiService } from '../src/services/api';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const router = useRouter();
  const { language, setLanguage, playerName } = useGameStore();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const t = translations[language];

  useEffect(() => {
    // Initialize questions on first load
    const initQuestions = async () => {
      try {
        setInitializing(true);
        await apiService.initQuestions();
      } catch (error) {
        console.log('Questions may already exist');
      } finally {
        setInitializing(false);
      }
    };
    initQuestions();
  }, []);

  const menuItems = [
    { key: 'classic', icon: 'trophy', color: '#4ECDC4', route: '/difficulty' },
    { key: 'timeRace', icon: 'timer', color: '#FF6B6B', route: '/difficulty?mode=time_race' },
    { key: 'dailyChallenge', icon: 'calendar', color: '#FFD93D', route: '/daily' },
    { key: 'multiplayer', icon: 'people', color: '#9B59B6', route: '/difficulty?mode=multiplayer' },
    { key: 'leaderboard', icon: 'podium', color: '#3498DB', route: '/leaderboard' },
  ];

  const currentLang = LANGUAGES.find((l) => l.code === language);

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.languageButton}
          onPress={() => setShowLanguageModal(true)}
        >
          <Text style={styles.flagText}>{currentLang?.flag}</Text>
          <Text style={styles.languageText}>{currentLang?.name}</Text>
          <Ionicons name="chevron-down" size={16} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Title */}
      <View style={styles.titleContainer}>
        <Image 
          source={require('../assets/images/icon-original.png')} 
          style={styles.logo}
          resizeMode="contain"
        />
        <Text style={styles.subtitle}>Challenge Your Mind</Text>
      </View>

      {/* Loading */}
      {initializing && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color="#4ECDC4" />
          <Text style={styles.loadingText}>{t.loading}</Text>
        </View>
      )}

      {/* Menu */}
      <ScrollView
        style={styles.menuContainer}
        contentContainerStyle={styles.menuContent}
        showsVerticalScrollIndicator={false}
      >
        {menuItems.map((item) => (
          <TouchableOpacity
            key={item.key}
            style={[styles.menuItem, { borderLeftColor: item.color }]}
            onPress={() => router.push(item.route as any)}
            activeOpacity={0.7}
          >
            <View style={[styles.iconContainer, { backgroundColor: item.color }]}>
              <Ionicons name={item.icon as any} size={28} color="#fff" />
            </View>
            <Text style={styles.menuText}>{t[item.key as keyof typeof t]}</Text>
            <Ionicons name="chevron-forward" size={24} color="#666" />
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Language Modal */}
      {showLanguageModal && (
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <Text style={styles.modalTitle}>{t.selectLanguage}</Text>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.languageOption,
                  language === lang.code && styles.languageOptionActive,
                ]}
                onPress={() => {
                  setLanguage(lang.code);
                  setShowLanguageModal(false);
                }}
              >
                <Text style={styles.languageOptionFlag}>{lang.flag}</Text>
                <Text style={styles.languageOptionText}>{lang.name}</Text>
                {language === lang.code && (
                  <Ionicons name="checkmark" size={24} color="#4ECDC4" />
                )}
              </TouchableOpacity>
            ))}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowLanguageModal(false)}
            >
              <Ionicons name="close" size={24} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: 16,
  },
  languageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#16213e',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 6,
  },
  flagText: {
    fontSize: 20,
  },
  languageText: {
    color: '#fff',
    fontSize: 14,
  },
  titleContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  logo: {
    width: 180,
    height: 140,
    marginBottom: 10,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#a0a0a0',
    marginTop: 5,
  },
  loadingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  loadingText: {
    color: '#a0a0a0',
    fontSize: 12,
  },
  menuContainer: {
    flex: 1,
  },
  menuContent: {
    padding: 16,
    gap: 12,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 16,
    borderLeftWidth: 4,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  menuText: {
    flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modal: {
    backgroundColor: '#16213e',
    borderRadius: 20,
    padding: 24,
    width: width * 0.85,
    maxWidth: 350,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  languageOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderRadius: 12,
    backgroundColor: '#1a1a2e',
    marginBottom: 10,
  },
  languageOptionActive: {
    backgroundColor: '#0f3460',
    borderWidth: 1,
    borderColor: '#4ECDC4',
  },
  languageOptionFlag: {
    fontSize: 28,
    marginRight: 12,
  },
  languageOptionText: {
    flex: 1,
    fontSize: 18,
    color: '#fff',
  },
  closeButton: {
    position: 'absolute',
    top: 10,
    right: 10,
    padding: 5,
  },
});
