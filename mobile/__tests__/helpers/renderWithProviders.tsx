import '@testing-library/jest-native/extend-expect';
import { server } from '../mocks/server';

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
});

// MSW Server setup
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Suppress console warnings in tests (optional)
const originalWarn = console.warn;
beforeAll(() => {
  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
        args[0].includes('Non-serializable values')  ||
        args[0].includes('Animated:'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.warn = originalWarn;
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