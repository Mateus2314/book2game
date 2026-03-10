const React = require('react');
const { render } = require('@testing-library/react-native');
const { QueryClient, QueryClientProvider } = require('@tanstack/react-query');
const { PaperProvider } = require('react-native-paper');
const { NavigationContainer } = require('@react-navigation/native');

// Create a new QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

const AllProviders = ({ children, queryClient }) => {
  return React.createElement(
    NavigationContainer,
    null,
    React.createElement(
      QueryClientProvider,
      { client: queryClient },
      React.createElement(
        PaperProvider,
        null,
        children
      )
    )
  );
};

function renderWithProviders(ui, { queryClient = createTestQueryClient(), ...renderOptions } = {}) {
  function Wrapper({ children }) {
    return React.createElement(AllProviders, { queryClient }, children);
  }
  return { ...render(ui, { wrapper: Wrapper, ...renderOptions }), queryClient };
}

module.exports = { renderWithProviders };