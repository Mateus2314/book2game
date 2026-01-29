import React from 'react';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {useAuthStore} from '../stores/authStore';
import {Icon} from 'react-native-paper';
import type {
  RootStackParamList,
  AuthStackParamList,
  MainTabParamList,
  HomeStackParamList,
  LibraryStackParamList,
  ProfileStackParamList,
} from '../types/navigation';

// Placeholder screens (will be created next)
import {LoginScreen} from '../screens/auth/LoginScreen';
import {RegisterScreen} from '../screens/auth/RegisterScreen';
import {HomeScreen} from '../screens/home/HomeScreen';
import {BookDetailsScreen} from '../screens/books/BookDetailsScreen';
import {RecommendationResultsScreen} from '../screens/recommendations/RecommendationResultsScreen';
import {LibraryScreen} from '../screens/library/LibraryScreen';
import {ProfileScreen} from '../screens/profile/ProfileScreen';
import {EditProfileScreen} from '../screens/profile/EditProfileScreen';

const RootStack = createStackNavigator<RootStackParamList>();
const AuthStack = createStackNavigator<AuthStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const HomeStack = createStackNavigator<HomeStackParamList>();
const LibraryStack = createStackNavigator<LibraryStackParamList>();
const ProfileStack = createStackNavigator<ProfileStackParamList>();

function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{headerShown: false}}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
    </AuthStack.Navigator>
  );
}

function HomeNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen
        name="HomeScreen"
        component={HomeScreen}
        options={{title: 'Buscar Livros'}}
      />
      <HomeStack.Screen
        name="BookDetails"
        component={BookDetailsScreen}
        options={{title: 'Detalhes do Livro'}}
      />
      <HomeStack.Screen
        name="RecommendationResults"
        component={RecommendationResultsScreen}
        options={{title: 'Jogos Recomendados'}}
      />
    </HomeStack.Navigator>
  );
}

function LibraryNavigator() {
  return (
    <LibraryStack.Navigator>
      <LibraryStack.Screen
        name="LibraryScreen"
        component={LibraryScreen}
        options={{title: 'Minha Biblioteca'}}
      />
      <LibraryStack.Screen
        name="BookDetails"
        component={BookDetailsScreen}
        options={{title: 'Detalhes do Livro'}}
      />
      <LibraryStack.Screen
        name="RecommendationResults"
        component={RecommendationResultsScreen}
        options={{title: 'Jogos Recomendados'}}
      />
    </LibraryStack.Navigator>
  );
}

function ProfileNavigator() {
  return (
    <ProfileStack.Navigator>
      <ProfileStack.Screen
        name="ProfileScreen"
        component={ProfileScreen}
        options={{title: 'Perfil'}}
      />
      <ProfileStack.Screen
        name="EditProfile"
        component={EditProfileScreen}
        options={{title: 'Editar Perfil'}}
      />
    </ProfileStack.Navigator>
  );
}

const HomeIcon = ({color, size}: {color: string; size: number}) => (
  <Icon source="magnify" size={size} color={color} />
);

const LibraryIcon = ({color, size}: {color: string; size: number}) => (
  <Icon source="book-multiple" size={size} color={color} />
);

const ProfileIcon = ({color, size}: {color: string; size: number}) => (
  <Icon source="account" size={size} color={color} />
);

function MainNavigator() {
  return (
    <MainTab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#6750A4',
        tabBarInactiveTintColor: '#79747E',
      }}>
      <MainTab.Screen
        name="Home"
        component={HomeNavigator}
        options={{
          tabBarLabel: 'Buscar',
          tabBarIcon: HomeIcon,
        }}
      />
      <MainTab.Screen
        name="Library"
        component={LibraryNavigator}
        options={{
          tabBarLabel: 'Biblioteca',
          tabBarIcon: LibraryIcon,
        }}
      />
      <MainTab.Screen
        name="Profile"
        component={ProfileNavigator}
        options={{
          tabBarLabel: 'Perfil',
          tabBarIcon: ProfileIcon,
        }}
      />
    </MainTab.Navigator>
  );
}

export function AppNavigator() {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  return (
    <RootStack.Navigator screenOptions={{headerShown: false}}>
      {!isAuthenticated ? (
        <RootStack.Screen name="Auth" component={AuthNavigator} />
      ) : (
        <RootStack.Screen name="Main" component={MainNavigator} />
      )}
    </RootStack.Navigator>
  );
}
