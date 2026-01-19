import AsyncStorage from '@react-native-async-storage/async-storage';

const ACCESS_TOKEN_KEY = '@book2game:access_token';
const REFRESH_TOKEN_KEY = '@book2game:refresh_token';
const USER_KEY = '@book2game:user';

export const authStorage = {
  async getAccessToken(): Promise<string | null> {
    return await AsyncStorage.getItem(ACCESS_TOKEN_KEY);
  },

  async setAccessToken(token: string): Promise<void> {
    await AsyncStorage.setItem(ACCESS_TOKEN_KEY, token);
  },

  async getRefreshToken(): Promise<string | null> {
    return await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
  },

  async setRefreshToken(token: string): Promise<void> {
    await AsyncStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  async getUser(): Promise<any | null> {
    const user = await AsyncStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  async setUser(user: any): Promise<void> {
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  async clearTokens(): Promise<void> {
    await AsyncStorage.multiRemove([
      ACCESS_TOKEN_KEY,
      REFRESH_TOKEN_KEY,
      USER_KEY,
    ]);
  },

  async setTokens(
    accessToken: string,
    refreshToken: string,
    user: any,
  ): Promise<void> {
    await AsyncStorage.multiSet([
      [ACCESS_TOKEN_KEY, accessToken],
      [REFRESH_TOKEN_KEY, refreshToken],
      [USER_KEY, JSON.stringify(user)],
    ]);
  },
};
