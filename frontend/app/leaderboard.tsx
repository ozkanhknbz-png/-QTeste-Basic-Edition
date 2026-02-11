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
import { useGameStore } from '../src/store/gameStore';
import { translations } from '../src/i18n/translations';
import { apiService, LeaderboardEntry } from '../src/services/api';

const { width } = Dimensions.get('window');

export default function LeaderboardScreen() {
  const router = useRouter();
  const { language } = useGameStore();
  const t = translations[language];

  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [filter, setFilter] = useState<'all' | 'classic' | 'time_race' | 'multiplayer'>('all');

  useEffect(() => {
    fetchLeaderboard();
  }, [filter]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const mode = filter === 'all' ? undefined : filter;
      const data = await apiService.getLeaderboard(mode, undefined, 50);
      setLeaderboard(data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const filters = [
    { key: 'all', label: 'All' },
    { key: 'classic', label: t.classic },
    { key: 'time_race', label: t.timeRace },
    { key: 'multiplayer', label: t.multiplayer },
  ];

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return { icon: 'trophy', color: '#FFD93D' };
      case 2:
        return { icon: 'medal', color: '#C0C0C0' };
      case 3:
        return { icon: 'medal', color: '#CD7F32' };
      default:
        return null;
    }
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
        <Text style={styles.title}>{t.leaderboard}</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={fetchLeaderboard}
        >
          <Ionicons name="refresh" size={24} color="#4ECDC4" />
        </TouchableOpacity>
      </View>

      {/* Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterContainer}
        contentContainerStyle={styles.filterContent}
      >
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[
              styles.filterButton,
              filter === f.key && styles.filterButtonActive,
            ]}
            onPress={() => setFilter(f.key as any)}
          >
            <Text
              style={[
                styles.filterText,
                filter === f.key && styles.filterTextActive,
              ]}
            >
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Leaderboard */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4ECDC4" />
          <Text style={styles.loadingText}>{t.loading}</Text>
        </View>
      ) : leaderboard.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="podium-outline" size={60} color="#666" />
          <Text style={styles.emptyText}>No scores yet</Text>
        </View>
      ) : (
        <ScrollView
          style={styles.listContainer}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header Row */}
          <View style={styles.tableHeader}>
            <Text style={[styles.tableHeaderText, { width: 50 }]}>{t.rank}</Text>
            <Text style={[styles.tableHeaderText, { flex: 1 }]}>{t.player}</Text>
            <Text style={[styles.tableHeaderText, { width: 60 }]}>{t.iq}</Text>
            <Text style={[styles.tableHeaderText, { width: 60 }]}>{t.score}</Text>
          </View>

          {/* Rows */}
          {leaderboard.map((entry, index) => {
            const rankIcon = getRankIcon(entry.rank);
            return (
              <View
                key={index}
                style={[
                  styles.tableRow,
                  entry.rank <= 3 && styles.tableRowTop,
                ]}
              >
                <View style={styles.rankContainer}>
                  {rankIcon ? (
                    <Ionicons
                      name={rankIcon.icon as any}
                      size={24}
                      color={rankIcon.color}
                    />
                  ) : (
                    <Text style={styles.rankText}>{entry.rank}</Text>
                  )}
                </View>
                <View style={styles.playerInfo}>
                  <Text style={styles.playerName} numberOfLines={1}>
                    {entry.user_name}
                  </Text>
                  <Text style={styles.playerMode}>
                    {entry.difficulty} • {entry.mode}
                  </Text>
                </View>
                <View style={styles.iqContainer}>
                  <Text style={styles.iqText}>{entry.estimated_iq}</Text>
                </View>
                <View style={styles.scoreContainer}>
                  <Text style={styles.scoreText}>{entry.score}</Text>
                </View>
              </View>
            );
          })}
        </ScrollView>
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
    fontSize: 24,
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
  filterContainer: {
    maxHeight: 50,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 10,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#16213e',
    marginRight: 10,
  },
  filterButtonActive: {
    backgroundColor: '#4ECDC4',
  },
  filterText: {
    color: '#a0a0a0',
    fontSize: 14,
    fontWeight: '600',
  },
  filterTextActive: {
    color: '#fff',
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  emptyText: {
    color: '#666',
    fontSize: 18,
  },
  listContainer: {
    flex: 1,
    marginTop: 16,
  },
  listContent: {
    padding: 16,
  },
  tableHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  tableHeaderText: {
    color: '#666',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  tableRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 12,
    marginTop: 8,
  },
  tableRowTop: {
    borderWidth: 1,
    borderColor: '#FFD93D30',
  },
  rankContainer: {
    width: 50,
    alignItems: 'center',
  },
  rankText: {
    color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  playerInfo: {
    flex: 1,
    paddingHorizontal: 8,
  },
  playerName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  playerMode: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
  iqContainer: {
    width: 60,
    alignItems: 'center',
  },
  iqText: {
    color: '#4ECDC4',
    fontSize: 18,
    fontWeight: 'bold',
  },
  scoreContainer: {
    width: 60,
    alignItems: 'center',
  },
  scoreText: {
    color: '#FFD93D',
    fontSize: 16,
    fontWeight: '600',
  },
});
