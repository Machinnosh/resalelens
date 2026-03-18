import React from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';

interface Props {
  value: string;
  onChangeText: (text: string) => void;
  onSubmit?: () => void;
}

export function SearchBar({ value, onChangeText, onSubmit }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>🔍</Text>
      <TextInput
        style={styles.input}
        placeholder="ブランド名・モデル名で検索..."
        placeholderTextColor="#9CA3AF"
        value={value}
        onChangeText={onChangeText}
        onSubmitEditing={onSubmit}
        returnKeyType="search"
        autoCapitalize="none"
        autoCorrect={false}
      />
      {value.length > 0 && (
        <TouchableOpacity onPress={() => onChangeText('')} style={styles.clearBtn}>
          <Text style={styles.clearText}>✕</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#F3F4F6', borderRadius: 12, paddingHorizontal: 14, height: 48, gap: 8,
  },
  icon: { fontSize: 16 },
  input: { flex: 1, fontSize: 15, color: '#111827' },
  clearBtn: {
    width: 24, height: 24, borderRadius: 12, backgroundColor: '#D1D5DB',
    justifyContent: 'center', alignItems: 'center',
  },
  clearText: { fontSize: 12, color: '#6B7280', fontWeight: '700' },
});
