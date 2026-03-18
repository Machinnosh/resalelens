import React from 'react';
import { Tabs } from 'expo-router';
import { Text } from 'react-native';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

function TabIcon({ label, focused, color }: { label: string; focused: boolean; color: string }) {
  const icons: Record<string, string> = { '検索': '🔍', 'ランキング': '📊', 'プロフィール': '👤' };
  return <Text style={{ fontSize: focused ? 22 : 20 }}>{icons[label] ?? '?'}</Text>;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        tabBarStyle: {
          backgroundColor: colorScheme === 'dark' ? '#111827' : '#FFFFFF',
          borderTopColor: colorScheme === 'dark' ? '#1F2937' : '#F3F4F6',
        },
        headerStyle: {
          backgroundColor: colorScheme === 'dark' ? '#111827' : '#FFFFFF',
        },
        headerTintColor: colorScheme === 'dark' ? '#FFFFFF' : '#111827',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '検索',
          tabBarIcon: ({ focused, color }) => <TabIcon label="検索" focused={focused} color={color} />,
          headerTitle: 'ResaleLens',
          headerTitleStyle: { fontWeight: '800', fontSize: 20 },
        }}
      />
      <Tabs.Screen
        name="ranking"
        options={{
          title: 'ランキング',
          tabBarIcon: ({ focused, color }) => <TabIcon label="ランキング" focused={focused} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'プロフィール',
          tabBarIcon: ({ focused, color }) => <TabIcon label="プロフィール" focused={focused} color={color} />,
          headerTitle: '設定',
        }}
      />
    </Tabs>
  );
}
