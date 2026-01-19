export const gameGenreIcons: Record<string, string> = {
  // Main genres
  action: 'gamepad-variant',
  adventure: 'map-marker-path',
  rpg: 'sword-cross',
  strategy: 'chess-knight',
  puzzle: 'puzzle',
  simulation: 'creation',
  sports: 'soccer',
  racing: 'car-sport',
  shooter: 'pistol',
  platformer: 'run',
  fighting: 'karate',
  mmo: 'account-group',
  mmorpg: 'account-group',

  // Sub-genres
  horror: 'ghost',
  'survival-horror': 'skull',
  stealth: 'eye-off',
  fantasy: 'wizard-hat',
  'sci-fi': 'robot',
  cyberpunk: 'microsoft-xbox-controller',
  medieval: 'castle',

  // Gameplay styles
  casual: 'controller',
  indie: 'star-four-points',
  arcade: 'ghost-outline',
  sandbox: 'cube-outline',
  roguelike: 'dice-multiple',

  // Special
  multiplayer: 'account-multiple',
  singleplayer: 'account',
  vr: 'virtual-reality',
};

export function getGameIcon(genres?: string[]): string {
  if (!genres || genres.length === 0) {
    return 'gamepad';
  }

  // Try to match exact genre
  for (const genre of genres) {
    const lowerGenre = genre.toLowerCase().trim();
    if (gameGenreIcons[lowerGenre]) {
      return gameGenreIcons[lowerGenre];
    }
  }

  // Try partial match
  for (const genre of genres) {
    const lowerGenre = genre.toLowerCase().trim();
    for (const [key, icon] of Object.entries(gameGenreIcons)) {
      if (lowerGenre.includes(key) || key.includes(lowerGenre)) {
        return icon;
      }
    }
  }

  // Default fallback
  return 'gamepad';
}
