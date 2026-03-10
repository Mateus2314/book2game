import '@testing-library/jest-native/extend-expect';
import { server } from '../mocks/server';

// Setup MSW server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
});

// Suppress console warnings in tests
const originalWarn = console.warn;
const originalError = console.error;

beforeAll(() => {
  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
        args[0].includes('Non-serializable values') ||
        args[0].includes('Animated:') ||
        args[0].includes('ViewPropTypes will be removed') ||
        args[0].includes('Tried to use the icon') ||
        args[0].includes('react-native-paper'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };

  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Animated:') ||
        args[0].includes('An update to TestComponent inside a test was not wrapped in act'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.warn = originalWarn;
  console.error = originalError;
});

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(),
  getItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  multiSet: jest.fn(),
  multiGet: jest.fn(),
  getAllKeys: jest.fn(),
}));

// Mock react-native-config
jest.mock('react-native-config', () => ({
  API_URL: 'http://localhost:3000',
  ENV: 'test',
}));

// Mock react-native-worklets
jest.mock('react-native-worklets', () => ({
  __esModule: true,
  default: {},
}));

// Mock react-native-reanimated to prevent initialization issues
jest.mock('react-native-reanimated', () => ({
  __esModule: true,
  default: {},
  useAnimatedStyle: () => ({}),
  useSharedValue: (val: any) => ({ value: val }),
  withTiming: (val: any) => val,
  FadeIn: {},
  FadeOut: {},
  BounceIn: {},
}));

// Mock @react-navigation/native
jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }: any) => children,
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
  }),
}));

// Mock @react-navigation/stack
jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));

// Mock @react-navigation/bottom-tabs
jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));

// Mock react-native-gesture-handler
jest.mock('react-native-gesture-handler', () => ({
  __esModule: true,
  Swipeable: ({ children }: any) => children,
  GestureHandlerRootView: ({ children }: any) => children,
  TouchableOpacity: ({ children }: any) => children,
  TouchableHighlight: ({ children }: any) => children,
  TouchableWithoutFeedback: ({ children }: any) => children,
}));

// Mock react-native-sound
jest.mock('react-native-sound', () => {
  return jest.fn().mockImplementation(() => ({
    play: jest.fn((callback) => callback(true)),
    stop: jest.fn(),
    release: jest.fn(),
    setVolume: jest.fn(),
  }));
});