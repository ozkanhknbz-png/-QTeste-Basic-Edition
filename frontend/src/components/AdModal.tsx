import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useGameStore } from '../store/gameStore';
import { translations } from '../i18n/translations';

const { width, height } = Dimensions.get('window');

const AD_DURATION = 5; // seconds

export const AdModal: React.FC = () => {
  const { showAd, closeAd, language } = useGameStore();
  const [countdown, setCountdown] = useState(AD_DURATION);
  const [canSkip, setCanSkip] = useState(false);
  const t = translations[language];

  useEffect(() => {
    if (showAd) {
      setCountdown(AD_DURATION);
      setCanSkip(false);
      
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            setCanSkip(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [showAd]);

  if (!showAd) return null;

  return (
    <Modal
      visible={showAd}
      animationType="fade"
      transparent={true}
      onRequestClose={() => canSkip && closeAd()}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          {/* Ad Header */}
          <View style={styles.header}>
            <Text style={styles.adLabel}>{t.ad}</Text>
            {canSkip ? (
              <TouchableOpacity style={styles.skipButton} onPress={closeAd}>
                <Text style={styles.skipText}>{t.skip}</Text>
                <Ionicons name="close" size={20} color="#fff" />
              </TouchableOpacity>
            ) : (
              <View style={styles.countdown}>
                <Text style={styles.countdownText}>{countdown}</Text>
              </View>
            )}
          </View>

          {/* Mock Ad Content */}
          <View style={styles.adContent}>
            <View style={styles.mockAd}>
              <Ionicons name="game-controller" size={80} color="#4ECDC4" />
              <Text style={styles.mockAdTitle}>Premium IQ Games</Text>
              <Text style={styles.mockAdSubtitle}>
                Unlock your brain's potential!
              </Text>
              <View style={styles.mockAdBadge}>
                <Text style={styles.mockAdBadgeText}>SPONSORED</Text>
              </View>
            </View>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>{t.adMessage}</Text>
            {canSkip && (
              <TouchableOpacity style={styles.continueButton} onPress={closeAd}>
                <Text style={styles.continueText}>{t.continue}</Text>
                <Ionicons name="arrow-forward" size={20} color="#fff" />
              </TouchableOpacity>
            )}
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    width: width * 0.9,
    maxWidth: 400,
    backgroundColor: '#1a1a2e',
    borderRadius: 20,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#16213e',
  },
  adLabel: {
    color: '#FFD93D',
    fontSize: 14,
    fontWeight: '600',
  },
  skipButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4ECDC4',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 4,
  },
  skipText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  countdown: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FF6B6B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  countdownText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  adContent: {
    padding: 24,
    minHeight: 280,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mockAd: {
    alignItems: 'center',
    gap: 16,
  },
  mockAdTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  mockAdSubtitle: {
    color: '#a0a0a0',
    fontSize: 16,
  },
  mockAdBadge: {
    backgroundColor: '#FFD93D',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 4,
  },
  mockAdBadgeText: {
    color: '#1a1a2e',
    fontSize: 10,
    fontWeight: 'bold',
  },
  footer: {
    padding: 16,
    backgroundColor: '#16213e',
    alignItems: 'center',
    gap: 12,
  },
  footerText: {
    color: '#a0a0a0',
    fontSize: 12,
  },
  continueButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4ECDC4',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
    gap: 8,
  },
  continueText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
