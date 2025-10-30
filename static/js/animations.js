/**
 * Animation System for Family Task Tracker
 * Provides flying points, confetti, screen shake, toasts, and more
 */

/**
 * Flying points animation - points fly from task to counter
 * @param {number} amount - The number of points earned
 * @param {HTMLElement} startElement - The element where animation starts
 * @param {HTMLElement} endElement - The element where animation ends (points counter)
 */
function animatePoints(amount, startElement, endElement) {
  const flyingPoint = document.createElement('div');
  flyingPoint.className = 'flying-points';
  flyingPoint.textContent = `+${amount}`;

  const startRect = startElement.getBoundingClientRect();
  flyingPoint.style.left = `${startRect.left + startRect.width / 2}px`;
  flyingPoint.style.top = `${startRect.top + startRect.height / 2}px`;

  document.body.appendChild(flyingPoint);

  const endRect = endElement.getBoundingClientRect();

  // Animate to counter
  setTimeout(() => {
    flyingPoint.style.left = `${endRect.left + endRect.width / 2}px`;
    flyingPoint.style.top = `${endRect.top + endRect.height / 2}px`;
    flyingPoint.style.opacity = '0';
  }, 50);

  // Remove after animation and increment counter
  setTimeout(() => {
    flyingPoint.remove();
    counterIncrement(endElement, amount);
  }, 1000);
}

/**
 * Counter increment animation - smoothly counts up
 * @param {HTMLElement} element - The counter element to animate
 * @param {number} targetIncrease - Amount to increase by
 */
function counterIncrement(element, targetIncrease) {
  // Find the actual number span within the element
  const numberElement = element.querySelector('[data-points]') || element;
  const currentValue = parseInt(numberElement.textContent.replace(/[^0-9]/g, '')) || 0;
  const targetValue = currentValue + targetIncrease;
  const duration = 500;
  const steps = 20;
  const increment = targetIncrease / steps;

  let current = currentValue;
  const interval = setInterval(() => {
    current += increment;
    numberElement.textContent = Math.round(current);

    if (current >= targetValue) {
      numberElement.textContent = targetValue;
      clearInterval(interval);
      element.classList.add('pulse-once');
      setTimeout(() => element.classList.remove('pulse-once'), 600);
    }
  }, duration / steps);
}

/**
 * Confetti burst animation
 * @param {number} x - X coordinate for center of burst
 * @param {number} y - Y coordinate for center of burst
 */
function confettiBurst(x, y) {
  const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffa500', '#ff1493'];
  const particleCount = 30;

  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'confetti-particle';
    particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;

    const angle = (Math.PI * 2 * i) / particleCount;
    const velocity = 100 + Math.random() * 100;

    particle.style.setProperty('--tx', `${Math.cos(angle) * velocity}px`);
    particle.style.setProperty('--ty', `${Math.sin(angle) * velocity}px`);

    document.body.appendChild(particle);

    setTimeout(() => particle.remove(), 1000);
  }
}

/**
 * Screen shake animation
 */
function screenShake() {
  document.body.classList.add('shake');
  setTimeout(() => document.body.classList.remove('shake'), 500);
}

/**
 * Toast notification
 * @param {string} message - The message to display
 * @param {string} theme - Theme name for styling (optional)
 * @param {number} duration - How long to show toast in ms (default 3000)
 */
function showToast(message, theme = 'default', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${theme}`;
  toast.innerHTML = message;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/**
 * Celebration sequence - combines multiple animations
 * @param {HTMLElement} button - The button that was clicked
 * @param {number} points - Points earned
 * @param {string} themeName - Theme name for styling
 */
function celebrate(button, points, themeName = 'default') {
  const buttonRect = button.getBoundingClientRect();
  const centerX = buttonRect.left + buttonRect.width / 2;
  const centerY = buttonRect.top + buttonRect.height / 2;

  // Add celebrating class to button
  button.classList.add('celebrating');
  setTimeout(() => button.classList.remove('celebrating'), 600);

  // Confetti burst
  confettiBurst(centerX, centerY);

  // Screen shake for high-value tasks
  if (points >= 100) {
    screenShake();
  }

  // Play theme sound if available
  const theme = window.THEMES ? window.THEMES[themeName] : null;
  if (theme && theme.sounds && theme.sounds.taskComplete) {
    const audio = new Audio(theme.sounds.taskComplete);
    audio.volume = 0.5;
    audio.play().catch(() => {
      // Silently fail if sound can't play
      console.log('Sound playback not available');
    });
  }
}

/**
 * Streak milestone animation - shows special effects for streak milestones
 * @param {number} streakCount - Current streak count
 */
function streakMilestone(streakCount) {
  const milestones = [3, 7, 14, 30, 60, 100];

  if (milestones.includes(streakCount)) {
    // Big celebration for milestones
    confettiBurst(window.innerWidth / 2, window.innerHeight / 2);
    showToast(`🔥 ${streakCount} DAY STREAK! YOU'RE ON FIRE! 🔥`, 'default', 5000);
    screenShake();

    // Multiple confetti bursts
    setTimeout(() => confettiBurst(window.innerWidth / 3, window.innerHeight / 2), 200);
    setTimeout(() => confettiBurst(window.innerWidth * 2 / 3, window.innerHeight / 2), 400);
  }
}

/**
 * Reward claimed animation
 * @param {string} rewardName - Name of the reward
 * @param {string} icon - Icon for the reward
 */
function rewardClaimedAnimation(rewardName, icon) {
  confettiBurst(window.innerWidth / 2, window.innerHeight / 2);
  showToast(`${icon} ${rewardName} Claimed! ${icon}`, 'default', 4000);
  screenShake();
}

/**
 * Level up animation - for point milestones
 * @param {number} newTotal - New total points
 */
function levelUpAnimation(newTotal) {
  const milestones = [100, 250, 500, 1000, 2500, 5000, 10000];

  if (milestones.includes(newTotal)) {
    confettiBurst(window.innerWidth / 2, 100);
    showToast(`⭐ LEVEL UP! ${newTotal} Total Points! ⭐`, 'default', 4000);
  }
}

/**
 * Task streak animation - for completing multiple tasks in a row
 * @param {number} taskStreak - Number of tasks completed in current session
 */
function taskStreakAnimation(taskStreak) {
  if (taskStreak >= 3 && taskStreak % 3 === 0) {
    showToast(`🔥 ${taskStreak} Tasks in a Row! Keep going! 🔥`, 'default', 2500);
  }
}

/**
 * Fireworks animation for special achievements
 * @param {number} count - Number of firework bursts
 */
function fireworks(count = 5) {
  for (let i = 0; i < count; i++) {
    setTimeout(() => {
      const x = Math.random() * window.innerWidth;
      const y = Math.random() * (window.innerHeight / 2);
      confettiBurst(x, y);
    }, i * 300);
  }
}

/**
 * Initialize animation system
 */
function initAnimations() {
  console.log('Animation system initialized!');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAnimations);
} else {
  initAnimations();
}
