import type {StackScreenProps} from '@react-navigation/stack';
import type {BottomTabScreenProps} from '@react-navigation/bottom-tabs';
import type {CompositeScreenProps} from '@react-navigation/native';
import type {Book, Recommendation} from './api';

// Auth Stack
export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type AuthStackScreenProps<T extends keyof AuthStackParamList> =
  StackScreenProps<AuthStackParamList, T>;

// Home Stack
export type HomeStackParamList = {
  HomeScreen: undefined;
  BookDetails: {book: Book};
  RecommendationResults: {recommendation: Recommendation};
};

export type HomeStackScreenProps<T extends keyof HomeStackParamList> =
  CompositeScreenProps<
    StackScreenProps<HomeStackParamList, T>,
    BottomTabScreenProps<MainTabParamList>
  >;

// Library Stack
export type LibraryStackParamList = {
  LibraryScreen: undefined;
};

export type LibraryStackScreenProps<T extends keyof LibraryStackParamList> =
  CompositeScreenProps<
    StackScreenProps<LibraryStackParamList, T>,
    BottomTabScreenProps<MainTabParamList>
  >;

// Profile Stack
export type ProfileStackParamList = {
  ProfileScreen: undefined;
  EditProfile: undefined;
};

export type ProfileStackScreenProps<T extends keyof ProfileStackParamList> =
  CompositeScreenProps<
    StackScreenProps<ProfileStackParamList, T>,
    BottomTabScreenProps<MainTabParamList>
  >;

// Main Tab Navigator
export type MainTabParamList = {
  Home: undefined;
  Library: undefined;
  Profile: undefined;
};

export type MainTabScreenProps<T extends keyof MainTabParamList> =
  BottomTabScreenProps<MainTabParamList, T>;

// Root Stack
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
