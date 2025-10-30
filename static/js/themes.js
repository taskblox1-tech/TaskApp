/**
 * Complete Theme Configuration System with Proper Avatars
 * Each theme includes colors, icons, sounds, and character-specific avatars
 */

const THEMES = {
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
      task: '✓',
      reward: '🎁',
      complete: '✅',
      pending: '⏳',
      streak: '🔥'
    },
    sounds: {
      taskComplete: '/static/sounds/default-ding.mp3',
      pointsEarn: '/static/sounds/default-coin.mp3'
    },
    avatars: [
      { name: 'Star', emoji: '⭐', color: '#FFD700' },
      { name: 'Rocket', emoji: '🚀', color: '#4F46E5' },
      { name: 'Rainbow', emoji: '🌈', color: '#7C3AED' },
      { name: 'Lightning', emoji: '⚡', color: '#F59E0B' }
    ]
  },

  minecraft: {
    name: 'Minecraft',
    colors: {
      primary: '#8B4513',
      secondary: '#228B22',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #7CB342 0%, #558B2F 100%)'
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
    avatars: [
      { name: 'Steve', emoji: '🧑‍🦰', color: '#00BFFF' },
      { name: 'Alex', emoji: '👩‍🦰', color: '#FF6347' },
      { name: 'Creeper', emoji: '💚', color: '#00FF00' },
      { name: 'Enderman', emoji: '🖤', color: '#800080' },
      { name: 'Zombie', emoji: '🧟', color: '#2E8B57' },
      { name: 'Skeleton', emoji: '💀', color: '#F5F5F5' },
      { name: 'Pig', emoji: '🐷', color: '#FFB6C1' },
      { name: 'Diamond', emoji: '💎', color: '#00CED1' }
    ]
  },

  roblox: {
    name: 'Roblox',
    colors: {
      primary: '#E31937',
      secondary: '#00A2FF',
      accent: '#FFC90E',
      background: 'linear-gradient(135deg, #E31937 0%, #00A2FF 100%)'
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
      { name: 'Bacon Hair', emoji: '🟥', color: '#E31937' },
      { name: 'Guest 666', emoji: '👻', color: '#666666' },
      { name: 'Noob', emoji: '🟨', color: '#FFC90E' },
      { name: 'Cool Kid', emoji: '😎', color: '#00A2FF' },
      { name: 'Builder', emoji: '👷', color: '#FF6600' },
      { name: 'Ninja', emoji: '🥷', color: '#000000' },
      { name: 'Superhero', emoji: '🦸', color: '#DC143C' },
      { name: 'Pro Gamer', emoji: '🎮', color: '#9B59B6' },
      { name: 'Adventurer', emoji: '🗺️', color: '#228B22' },
      { name: 'Robux King', emoji: '👑', color: '#FFD700' }
    ]
  },

  barbie: {
    name: 'Barbie',
    colors: {
      primary: '#FF69B4',
      secondary: '#DDA0DD',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #FF69B4 0%, #DDA0DD 100%)'
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
    avatars: [
      { name: 'Classic Barbie', emoji: '👱‍♀️', color: '#FF69B4' },
      { name: 'Princess', emoji: '👸', color: '#FFD700' },
      { name: 'Mermaid', emoji: '🧜‍♀️', color: '#00CED1' },
      { name: 'Astronaut', emoji: '👩‍🚀', color: '#4169E1' }
    ]
  },

  pokemon: {
    name: 'Pokémon',
    colors: {
      primary: '#FF0000',
      secondary: '#FFDE00',
      accent: '#3B4CCA',
      background: 'linear-gradient(135deg, #FF0000 0%, #FFDE00 100%)'
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
    avatars: [
      { name: 'Pikachu', emoji: '⚡', color: '#FFDE00' },
      { name: 'Charizard', emoji: '🔥', color: '#FF4500' },
      { name: 'Squirtle', emoji: '💧', color: '#1E90FF' },
      { name: 'Bulbasaur', emoji: '🌿', color: '#32CD32' }
    ]
  },

  ninjaturtles: {
    name: 'Ninja Turtles',
    colors: {
      primary: '#00A000',
      secondary: '#FF8C00',
      accent: '#FFD700',
      background: 'linear-gradient(135deg, #00A000 0%, #228B22 100%)'
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
    avatars: [
      { name: 'Leonardo', emoji: '🔵', color: '#0000FF', weapon: '⚔️' },
      { name: 'Michelangelo', emoji: '🟠', color: '#FF8C00', weapon: '🥢' },
      { name: 'Donatello', emoji: '🟣', color: '#800080', weapon: '🥍' },
      { name: 'Raphael', emoji: '🔴', color: '#FF0000', weapon: '🗡️' }
    ]
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
      { name: 'Mario', emoji: '🔴', color: '#E52521', hat: '🧢' },
      { name: 'Luigi', emoji: '🟢', color: '#00A550', hat: '🧢' },
      { name: 'Princess Peach', emoji: '👸', color: '#FFB7C5', hat: '👑' },
      { name: 'Yoshi', emoji: '🦖', color: '#00A550', hat: '' },
      { name: 'Toad', emoji: '🍄', color: '#FF0000', hat: '' },
      { name: 'Bowser', emoji: '🐲', color: '#228B22', hat: '' },
      { name: 'Wario', emoji: '🟡', color: '#FFD700', hat: '🧢' },
      { name: 'Princess Daisy', emoji: '🌼', color: '#FFA500', hat: '👑' },
      { name: 'Waluigi', emoji: '🟣', color: '#800080', hat: '🧢' },
      { name: 'Donkey Kong', emoji: '🦍', color: '#8B4513', hat: '' }
    ]
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

/**
 * Get task categories (helper function for templates)
 */
function getTaskCategories() {
  return [
    'Morning Tasks',
    'Evening Tasks',
    'Academic Excellence',
    'Health & Fitness',
    'Character & Behavior',
    'Extra Household Tasks',
    'Creative & Development',
    'Bonus Challenges'
  ];
}
