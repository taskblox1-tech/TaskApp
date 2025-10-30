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
      { name: 'Star', emoji: '⭐', color: '#FFD700', imageUrl: '/static/images/characters/default/star.png', unlockRequirement: null, description: 'Classic star champion' },
      { name: 'Rocket', emoji: '🚀', color: '#4F46E5', imageUrl: '/static/images/characters/default/rocket.png', unlockRequirement: null, description: 'Ready for liftoff!' },
      { name: 'Rainbow', emoji: '🌈', color: '#7C3AED', imageUrl: '/static/images/characters/default/rainbow.png', unlockRequirement: 'streak_3', description: 'Unlocked with 3-day streak' },
      { name: 'Lightning', emoji: '⚡', color: '#F59E0B', imageUrl: '/static/images/characters/default/lightning.png', unlockRequirement: 'points_250', description: 'Unlocked with 250 points' }
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
      { name: 'Steve', emoji: '🧑‍🦰', color: '#00BFFF', imageUrl: '/static/images/characters/minecraft/Steve.jpg', unlockRequirement: null, description: 'The classic miner' },
      { name: 'Alex', emoji: '👩‍🦰', color: '#FF6347', imageUrl: '/static/images/characters/minecraft/150 Pixel Alex.png', unlockRequirement: null, description: 'Ready to explore!' },
      { name: 'Ari', emoji: '💜', color: '#9D4EDD', imageUrl: '/static/images/characters/minecraft/150 Pixel Ari.png', unlockRequirement: 'streak_3', description: 'New friend! (3-day streak)' }
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
      { name: 'Bacon Hair', emoji: '🟥', color: '#E31937', imageUrl: '/static/images/characters/roblox/Bacon Hair.png', unlockRequirement: null, description: 'Classic starter avatar' },
      { name: 'Guest 666', emoji: '👻', color: '#666666', imageUrl: '/static/images/characters/roblox/Guest 666.png', unlockRequirement: null, description: 'Mysterious guest' },
      { name: 'Noob', emoji: '🟨', color: '#FFC90E', imageUrl: '/static/images/characters/roblox/Noob.png', unlockRequirement: null, description: 'Everyone starts here!' },
      { name: 'Cool Kid', emoji: '😎', color: '#00A2FF', imageUrl: '/static/images/characters/roblox/Cool Kid.jpg', unlockRequirement: 'streak_3', description: 'Maintain 3-day streak' },
      { name: 'Builder', emoji: '👷', color: '#FF6600', imageUrl: '/static/images/characters/roblox/Builder.jpg', unlockRequirement: 'tasks_25', description: 'Complete 25 tasks' },
      { name: 'Ninja', emoji: '🥷', color: '#000000', imageUrl: '/static/images/characters/roblox/Ninja.jpg', unlockRequirement: 'streak_7', description: 'Master 7-day streak' },
      { name: 'Superhero', emoji: '🦸', color: '#DC143C', imageUrl: '/static/images/characters/roblox/Roblox Superhero.jpg', unlockRequirement: 'tasks_50', description: 'Complete 50 tasks' },
      { name: 'Pro Gamer', emoji: '🎮', color: '#9B59B6', imageUrl: '/static/images/characters/roblox/Pro Gamer.jpg', unlockRequirement: 'points_500', description: 'Earn 500 points' },
      { name: 'Adventurer', emoji: '🗺️', color: '#228B22', imageUrl: '/static/images/characters/roblox/Adventurer.png', unlockRequirement: 'kindness_3', description: '3 acts of kindness' },
      { name: 'Robux King', emoji: '👑', color: '#FFD700', imageUrl: '/static/images/characters/roblox/Robux King.jpg', unlockRequirement: 'points_1000', description: 'Elite status (1000 points)' }
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
      { name: 'Classic Barbie', emoji: '👱‍♀️', color: '#FF69B4', imageUrl: '/static/images/characters/barbie/Classic Barbie.jpeg', unlockRequirement: null, description: 'Iconic and fabulous!' },
      { name: 'Princess', emoji: '👸', color: '#FFD700', imageUrl: '/static/images/characters/barbie/Princess Barbie.jpg', unlockRequirement: 'streak_3', description: 'Royal 3-day streak' },
      { name: 'Mermaid', emoji: '🧜‍♀️', color: '#00CED1', imageUrl: '/static/images/characters/barbie/Mermaid Barbie.png', unlockRequirement: 'tasks_25', description: 'Dive into 25 tasks' },
      { name: 'Astronaut', emoji: '👩‍🚀', color: '#4169E1', imageUrl: '/static/images/characters/barbie/Astronaut Barbie.jpg', unlockRequirement: 'points_500', description: 'Reach for the stars (500 points)' },
      { name: 'Pink Dress', emoji: '💃', color: '#FFB6C1', imageUrl: '/static/images/characters/barbie/Pink Dress Barbie.jpg', unlockRequirement: 'kindness_3', description: 'Sparkle with 3 acts of kindness' }
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
      { name: 'Pikachu', emoji: '⚡', color: '#FFDE00', imageUrl: '/static/images/characters/pokemon/Pikachu.png', unlockRequirement: null, description: 'Electric starter!' },
      { name: 'Squirtle', emoji: '💧', color: '#1E90FF', imageUrl: '/static/images/characters/pokemon/Squirtle.png', unlockRequirement: null, description: 'Water type hero' },
      { name: 'Bulbasaur', emoji: '🌿', color: '#32CD32', imageUrl: '/static/images/characters/pokemon/Bulbasaur.jpg', unlockRequirement: 'streak_3', description: 'Grass power (3-day streak)' },
      { name: 'Charizard', emoji: '🔥', color: '#FF4500', imageUrl: '/static/images/characters/pokemon/Charizard.png', unlockRequirement: 'points_500', description: 'Legendary fire power (500 points)' }
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
      { name: 'Leonardo', emoji: '🔵', color: '#0000FF', weapon: '⚔️', imageUrl: '/static/images/characters/ninjaturtles/Leonardo.jpg', unlockRequirement: null, description: 'Leader in blue' },
      { name: 'Michelangelo', emoji: '🟠', color: '#FF8C00', weapon: '🥢', imageUrl: '/static/images/characters/ninjaturtles/Michelangelo.png', unlockRequirement: null, description: 'Party dude!' },
      { name: 'Donatello', emoji: '🟣', color: '#800080', weapon: '🥍', imageUrl: '/static/images/characters/ninjaturtles/Donatello.jpg', unlockRequirement: 'tasks_25', description: 'Tech genius (25 tasks)' },
      { name: 'Raphael', emoji: '🔴', color: '#FF0000', weapon: '🗡️', imageUrl: '/static/images/characters/ninjaturtles/Rafael.jpg', unlockRequirement: 'streak_5', description: 'Cool but rude (5-day streak)' }
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
      { name: 'Mario', emoji: '🔴', color: '#E52521', hat: '🧢', imageUrl: '/static/images/characters/mario/Baby Mario.jpg', unlockRequirement: null, description: "It's-a me, Mario!" },
      { name: 'Luigi', emoji: '🟢', color: '#00A550', hat: '🧢', imageUrl: '/static/images/characters/mario/Luigi.jpg', unlockRequirement: null, description: 'Player 2 ready!' },
      { name: 'Princess Peach', emoji: '👸', color: '#FFB7C5', hat: '👑', imageUrl: '/static/images/characters/mario/Princess Peach.png', unlockRequirement: 'streak_3', description: 'Royal rescue (3-day streak)' },
      { name: 'Yoshi', emoji: '🦖', color: '#00A550', hat: '', imageUrl: '/static/images/characters/mario/Yoshi.jpg', unlockRequirement: 'tasks_25', description: 'Loyal companion (25 tasks)' },
      { name: 'Toad', emoji: '🍄', color: '#FF0000', hat: '', imageUrl: '/static/images/characters/mario/Toad.png', unlockRequirement: 'kindness_3', description: 'Helpful friend (3 acts of kindness)' },
      { name: 'Bowser', emoji: '🐲', color: '#228B22', hat: '', imageUrl: '/static/images/characters/mario/Bowser.jpg', unlockRequirement: 'tasks_50', description: 'Conquer 50 tasks' },
      { name: 'Wario', emoji: '🟡', color: '#FFD700', hat: '🧢', imageUrl: '/static/images/characters/mario/Wario.png', unlockRequirement: 'points_500', description: 'Greedy for points (500)' },
      { name: 'Princess Daisy', emoji: '🌼', color: '#FFA500', hat: '👑', imageUrl: '/static/images/characters/mario/Princess Daisy.png', unlockRequirement: 'streak_7', description: 'Week-long champion' },
      { name: 'Waluigi', emoji: '🟣', color: '#800080', hat: '🧢', imageUrl: '/static/images/characters/mario/Waluigi.png', unlockRequirement: 'tasks_75', description: 'Wicked skills (75 tasks)' },
      { name: 'Donkey Kong', emoji: '🦍', color: '#8B4513', hat: '', imageUrl: '/static/images/characters/mario/Donkey Kong.png', unlockRequirement: 'points_1000', description: 'Jungle legend (1000 points)' }
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
