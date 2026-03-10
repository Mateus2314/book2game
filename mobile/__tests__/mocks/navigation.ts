import { jest } from '@jest/globals';

// Mock react-navigation hooks
export const mockNavigationProp = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  push: jest.fn(),
  replace: jest.fn(),
  dispatch: jest.fn(),
  setOptions: jest.fn(),
  setParams: jest.fn(),
} as any;

export const mockRouteProp = {
  key: 'test-key',
  name: 'Test',
  params: {},
} as any;

// Mock useNavigation hook
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => mockNavigationProp,
  useRoute: () => mockRouteProp,
  NavigationContainer: ({ children }: any) => children,
}));

// Mock navigation stack hooks
jest.mock('@react-navigation/native-stack', () => ({
  createNativeStackNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));

// Mock bottom-tabs navigation
jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));