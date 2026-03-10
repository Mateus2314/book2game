# Testing Guide - Book2Game Mobile App

## Overview

This guide covers the comprehensive testing strategy for the Book2Game mobile app including:
- **Unit Tests**: Hooks, utilities, and state management
- **Integration Tests**: API services, forms, and complex components
- **E2E Tests**: User workflows using Detox + Robot Framework

## Project Structure

```
__tests__/
├── helpers/
│   ├── setupTests.ts              # Global test setup with MSW
│   ├── renderWithProviders.tsx    # Test wrapper with all providers
│   └── mockData.ts                # Test fixtures and mock data
├── mocks/
│   ├── server.ts                  # MSW request handlers
│   └── navigation.ts              # React Navigation mocks
├── unit/
│   ├── hooks/                     # useDebounce, useErrorHandler tests
│   ├── stores/                    # authStore tests
│   └── components/                # Simple component tests
├── integration/
│   ├── services/                  # API endpoints tests
│   ├── screens/                   # Complex screen tests
│   └── components/                # Complex component tests (with mutations)
└── e2e/
    ├── auth.robot                 # Authentication flow tests
    ├── library.robot              # Library management tests
    └── recommendations.robot      # Recommendations flow tests
```

## Running Tests

### Install Dependencies
```bash
cd mobile
npm install
```

### Unit Tests
```bash
# Run all unit tests
npm run test:unit

# Watch mode for development
npm run test:unit -- --watch

# With coverage
npm run test:unit -- --coverage
```

### Integration Tests
```bash
# Run all integration tests
npm run test:integration

# Watch mode
npm run test:integration -- --watch
```

### All Tests with Coverage
```bash
npm run test:coverage
```

This will generate a coverage report in `./htmlcov/` directory.

### E2E Tests with Detox

#### Setup Detox
```bash
# Install Detox globally
npm install -g detox-cli

# Build the app for testing (iOS)
npm run build:e2e

# Or for a specific configuration
detox build-framework-cache
```

#### Run E2E Tests
```bash
# Run iOS tests
npm run test:e2e

# Run Android tests
detox test __tests__/e2e --configuration android.emu.debug --cleanup

# Run specific test file
detox test __tests__/e2e/auth.robot --configuration ios.sim.debug
```

## Writing Tests

### Unit Test Example

```typescript
import { renderHook, act } from '@testing-library/react-native';
import { useMyHook } from '@/hooks/useMyHook';

describe('useMyHook', () => {
  it('should do something', () => {
    const { result } = renderHook(() => useMyHook());
    
    act(() => {
      result.current.myFunction();
    });
    
    expect(result.current.value).toBe('expected');
  });
});
```

### Component Test Example

```typescript
import { renderWithProviders } from '__tests__/helpers/renderWithProviders';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    renderWithProviders(<MyComponent prop="value" />);
    expect(true).toBe(true); // Component renders without error
  });
});
```

### Integration Test Example

```typescript
import { server } from '__tests__/mocks/server';
import { HttpResponse, http } from 'msw';

describe('API Integration', () => {
  it('should fetch data from API', async () => {
    server.use(
      http.get('http://localhost:3000/books', () => {
        return HttpResponse.json({ books: [] });
      })
    );

    // Test code here
  });
});
```

### E2E Test Example (Robot Framework)

```robot
*** Settings ***
Library    AppiumLibrary

*** Test Cases ***
User Can Login
    [Documentation]    User should be able to login with valid credentials
    Open Application    ...
    Input Text    id=email    user@example.com
    Input Text    id=password    password123
    Click Button    id=login
    Wait Until Page Contains Element    id=home-screen
```

## Mock Data

Use `mockData.ts` to access predefined mock objects:

```typescript
import {
  mockUsers,
  mockBooks,
  mockGames,
  mockRecommendations,
  createMockBook,
  createMockGame,
} from '__tests__/helpers/mockData';

// Use existing mocks
const user = mockUsers.user1;

// Create custom mocks with overrides
const customBook = createMockBook({ title: 'Custom Title' });
```

## MSW (Mock Service Worker)

MSW intercepts API requests at the network level. To add new mock endpoints:

1. Edit `__tests__/mocks/server.ts`
2. Add new handler to `handlers` array:

```typescript
http.get(`${API_URL}/new-endpoint`, async () => {
  return HttpResponse.json({ data: 'value' }, { status: 200 });
}),
```

## Coverage Goals

We aim for the following coverage thresholds:

- **Lines**: 70%
- **Branches**: 65%
- **Functions**: 70%
- **Statements**: 70%

Check coverage report:
```bash
npm run test:coverage
# Open htmlcov/index.html in browser
```

## Common Issues

### "Module not found" errors
- Make sure imports use `@/` alias (e.g., `@/hooks/useMyHook`)
- Check that all files have proper exports

### "Cannot find module 'react-native-paper'"
- Ensure all dependencies are installed: `npm install`
- Clear Jest cache: `npx jest --clearCache`

### Timeout errors in E2E tests
- Increase timeout in detox.config.js
- Check that the app is properly built

### MockedProvider not working
- Ensure `renderWithProviders` is used instead of standard `render`
- Check that QueryClient is properly initialized

## Continuous Integration

Tests are designed to run in CI/CD pipelines (GitHub Actions, etc.):

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: npm run test:coverage

- name: Run E2E Tests
  run: npm run test:e2e
```

## Debugging Tests

### VSCode Debugging

`.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Tests",
  "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand", "--no-coverage"],
  "console": "integratedTerminal"
}
```

### Test Filtering

```bash
# Run tests in a specific file
npm test -- useErrorHandler.test.ts

# Run tests matching a pattern
npm test -- --testNamePattern="should.*error"

# Run a specific describe block
npm test -- --testNamePattern="useErrorHandler"
```

## Best Practices

1. **Keep tests focused**: One assertion per test when possible
2. **Use meaningful names**: Test names should describe what is being tested
3. **Mock external dependencies**: Don't call real APIs
4. **Cleanup after tests**: Use `afterEach` hooks
5. **Test behavior, not implementation**: Focus on what users see
6. **Use test utils**: Use `renderWithProviders` for consistent setup
7. **Avoid hardcoding**: Use mock data helpers

## Useful Commands

```bash
# Run tests and watch for changes
npm run test:watch

# Run specific test file
npm test -- hooks/useDebounce.test.ts

# Update snapshots
npm test -- -u

# Clear Jest cache
npm test -- --clearCache

# Show coverage for specific file
npm run test:coverage -- --collectCoverageFrom="src/hooks/**"
```

## Resources

- [React Testing Library](https://testing-library.com/react-native)
- [Jest Documentation](https://jestjs.io/)
- [Detox E2E Testing](https://wix.github.io/Detox/)
- [Robot Framework](https://robotframework.org/)
- [MSW Documentation](https://mswjs.io/)

## Questions or Issues?

Refer to the individual test files for examples, or check the documentation links above.