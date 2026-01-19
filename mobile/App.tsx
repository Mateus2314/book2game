import React from 'react';
import {SafeAreaView, StatusBar, StyleSheet} from 'react-native';
import {PaperProvider} from 'react-native-paper';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {NavigationContainer} from '@react-navigation/native';
import {theme} from './src/theme/theme';
import {AppNavigator} from './src/navigation/AppNavigator';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
 

function App(): React.JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <SafeAreaView style={styles.container}>
            <StatusBar
              barStyle="light-content"
              backgroundColor={theme.colors.primary}
            />
            <AppNavigator />
          </SafeAreaView>
        </NavigationContainer>
      </PaperProvider>
    </QueryClientProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;