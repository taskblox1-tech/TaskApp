/**
 * Theme Configuration System
 * Defines all available themes with colors, icons, sounds, and avatars
 */

const THEMES = {
  minecraft: {
    name: 'Minecraft',
    colors: {
      primary: '#8B4513',
      secondary: '#228B22',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #7CB342, #558B2F)'
    },
    icons: {
      points: '💎',
      task: '⛏️',
      reward: '🪓',
      complete: '✅',
      pending: '⏳',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/minecraft-ding.mp3',
      pointsEarn: '/static/sounds/minecraft-collect.mp3'
    },
    avatars: ['Steve', 'Alex', 'Creeper', 'Enderman']
  },

  roblox: {
    name: 'Roblox',
    colors: {
      primary: '#E31937',
      secondary: '#00A2FF',
      accent: '#FFC90E',
      background: 'linear-gradient(135deg, #E31937, #00A2FF)'
    },
    icons: {
      points: '🪙',
      task: '🎮',
      reward: '🎁',
      complete: '✅',
      pending: '⏰',
      streak: '⚡'
    },
    sounds: {
      taskComplete: '/static/sounds/roblox-oof.mp3',
      pointsEarn: '/static/sounds/roblox-coin.mp3'
    },
    avatars: [
      'Bacon Hair',
      'Guest 666',
      'Noob',
      'Cool Kid',
      'Builder',
      'Ninja',
      'Superhero',
      'Pro Gamer',
      'Adventurer',
      'Robux King'
    ]
  },

  barbie: {
    name: 'Barbie',
    colors: {
      primary: '#FF69B4',
      secondary: '#DDA0DD',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #FF69B4, #DDA0DD)'
    },
    icons: {
      points: '💖',
      task: '✨',
      reward: '👗',
      complete: '💕',
      pending: '🎀',
      streak: '👑'
    },
    sounds: {
      taskComplete: '/static/sounds/barbie-sparkle.mp3',
      pointsEarn: '/static/sounds/barbie-yay.mp3'
    },
    avatars: ['Classic Barbie', 'Princess', 'Mermaid', 'Astronaut']
  },

  pokemon: {
    name: 'Pokémon',
    colors: {
      primary: '#FF0000',
      secondary: '#FFDE00',
      accent: '#3B4CCA',
      background: 'linear-gradient(135deg, #FF0000, #FFDE00)'
    },
    icons: {
      points: '⚡',
      task: '🎯',
      reward: '🏆',
      complete: '✅',
      pending: '⏳',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/pokemon-caught.mp3',
      pointsEarn: '/static/sounds/pokemon-level.mp3'
    },
    avatars: ['Pikachu', 'Charizard', 'Squirtle', 'Bulbasaur']
  },

  ninjaturtles: {
    name: 'Ninja Turtles',
    colors: {
      primary: '#00A000',
      secondary: '#FF8C00',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #00A000, #228B22)'
    },
    icons: {
      points: '🍕',
      task: '🥋',
      reward: '🗡️',
      complete: '✅',
      pending: '⏱️',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/turtle-cowabunga.mp3',
      pointsEarn: '/static/sounds/turtle-ding.mp3'
    },
    avatars: ['Leonardo', 'Michelangelo', 'Donatello', 'Raphael']
  },

  mario: {
    name: 'Super Mario',
    colors: {
      primary: '#E52521',
      secondary: '#FEDE00',
      accent: '#049CD8',
      background: 'linear-gradient(135deg, #E52521, #FEDE00)'
    },
    icons: {
      points: '⭐',
      task: '🍄',
      reward: '👑',
      complete: '✅',
      pending: '⏰',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/mario-coin.mp3',
      pointsEarn: '/static/sounds/mario-powerup.mp3'
    },
    avatars: [
      'Mario',
      'Luigi',
      'Princess Peach',
      'Yoshi',
      'Toad',
      'Bowser',
      'Wario',
      'Princess Daisy',
      'Waluigi',
      'Donkey Kong'
    ]
  },

  default: {
    name: 'Classic',
    colors: {
      primary: '#4F46E5',
      secondary: '#7C3AED',
      accent: '#F59E0B',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    icons: {
      points: '⭐',
      task: '📋',
      reward: '🎁',
      complete: '✅',
      pending: '⏳',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/complete.mp3',
      pointsEarn: '/static/sounds/points.mp3'
    },
    avatars: ['Star', 'Moon', 'Sun', 'Cloud']
  }
};

/**
 * Get theme configuration by name
 * @param {string} themeName - Name of the theme
 * @returns {object} Theme configuration object
 */
function getTheme(themeName) {
  return THEMES[themeName] || THEMES.default;
}

/**
 * Get all available theme names
 * @returns {array} Array of theme names
 */
function getAllThemeNames() {
  return Object.keys(THEMES);
}

/**
 * Apply theme colors to CSS variables
 * @param {string} themeName - Name of the theme to apply
 */
function applyTheme(themeName) {
  const theme = getTheme(themeName);
  const root = document.documentElement;

  root.style.setProperty('--theme-primary', theme.colors.primary);
  root.style.setProperty('--theme-secondary', theme.colors.secondary);
  root.style.setProperty('--theme-accent', theme.colors.accent);
  root.style.setProperty('--theme-background', theme.colors.background);
}
