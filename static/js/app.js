// ====================================================================
// FILE: static/js/app.js
// Main JavaScript utilities and helpers
// ====================================================================

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };
    
    const toast = document.createElement('div');
    toast.className = `${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg mb-2 animate-slide-in`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container');
    if (container) {
        container.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    }
}

// API Helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// Format numbers with commas
function formatPoints(points) {
    return points.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Confetti celebration animation
function celebrate() {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        
        // Create emoji confetti
        for (let i = 0; i < particleCount; i++) {
            const emoji = ['⭐', '🎉', '✨', '🏆', '💫'][Math.floor(Math.random() * 5)];
            createFloatingEmoji(emoji);
        }
    }, 250);
}

function createFloatingEmoji(emoji) {
    const element = document.createElement('div');
    element.textContent = emoji;
    element.style.cssText = `
        position: fixed;
        font-size: 2rem;
        left: ${Math.random() * window.innerWidth}px;
        top: ${window.innerHeight}px;
        z-index: 9999;
        pointer-events: none;
        transition: all 3s ease-out;
    `;
    
    document.body.appendChild(element);
    
    setTimeout(() => {
        element.style.top = '-100px';
        element.style.opacity = '0';
        element.style.transform = `rotate(${Math.random() * 360}deg)`;
    }, 10);
    
    setTimeout(() => element.remove(), 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏡 Family Task Tracker loaded!');
});


// ====================================================================
// PARENT DASHBOARD HTML
// FILE: templates/parent/dashboard.html
// ====================================================================

/*
{% extends "base.html" %}

{% block title %}Parent Dashboard{% endblock %}

{% block content %}
<div class="space-y-6">
    
    <!-- Header -->
    <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex justify-between items-center flex-wrap gap-4">
            <div>
                <h1 class="text-3xl font-bold text-gray-800">Family Dashboard</h1>
                <p class="text-gray-600">Manage tasks and track progress</p>
            </div>
            <div class="flex gap-3">
                <a href="/parent/task-library" class="btn-primary">
                    📚 Task Library
                </a>
                {% if pending_approvals > 0 %}
                <a href="/parent/approval-queue" class="btn-primary relative">
                    🔔 Approvals
                    <span class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                        {{ pending_approvals }}
                    </span>
                </a>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Family Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl shadow-lg p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-600 text-sm">Total Children</p>
                    <p class="text-3xl font-bold text-gray-800">{{ children|length }}</p>
                </div>
                <div class="text-4xl">👨‍👩‍👧</div>
            </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-600 text-sm">Pending Approvals</p>
                    <p class="text-3xl font-bold text-yellow-600">{{ pending_approvals }}</p>
                </div>
                <div class="text-4xl">🔔</div>
            </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-gray-600 text-sm">Join Code</p>
                    <p class="text-2xl font-mono font-bold text-blue-600">{{ user.family.join_code }}</p>
                </div>
                <div class="text-4xl">🔑</div>
            </div>
        </div>
    </div>
    
    <!-- Children Progress -->
    <div class="bg-white rounded-xl shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Children Progress</h2>
        
        {% if children %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for child in children %}
            <div class="border-2 border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-16 h-16 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center text-3xl">
                        {{ child.theme_emoji if child.theme_emoji else '👤' }}
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">{{ child.first_name }}</h3>
                        <p class="text-sm text-gray-600 capitalize">Theme: {{ child.theme }}</p>
                    </div>
                </div>
                
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Lifetime Points:</span>
                        <span class="font-bold text-blue-600">{{ child.total_lifetime_points | format_points }}</span>
                    </div>
                    
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Today's Tasks:</span>
                        <span class="font-bold text-green-600">
                            {{ child.today_completed if child.today_completed else 0 }} / {{ child.today_total if child.today_total else 0 }}
                        </span>
                    </div>
                </div>
                
                <div class="mt-4 pt-4 border-t border-gray-200">
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="bg-gradient-to-r from-blue-400 to-purple-500 h-3 rounded-full" 
                             style="width: {{ (child.today_completed / child.today_total * 100) if child.today_total > 0 else 0 }}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1 text-center">
                        {{ ((child.today_completed / child.today_total * 100) if child.today_total > 0 else 0) | round }}% Complete
                    </p>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-12">
            <p class="text-gray-500 mb-4">No children added yet</p>
            <p class="text-sm text-gray-400">Share your join code: <span class="font-mono font-bold text-blue-600">{{ user.family.join_code }}</span></p>
        </div>
        {% endif %}
    </div>
    
    <!-- Quick Actions -->
    <div class="bg-white rounded-xl shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Quick Actions</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a href="/parent/task-library" class="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all text-center">
                <div class="text-4xl mb-2">📚</div>
                <p class="font-medium text-gray-800">Manage Tasks</p>
                <p class="text-xs text-gray-500">Add or edit family tasks</p>
            </a>
            
            <a href="/parent/approval-queue" class="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all text-center relative">
                <div class="text-4xl mb-2">🔔</div>
                <p class="font-medium text-gray-800">Approvals</p>
                <p class="text-xs text-gray-500">Review requests</p>
                {% if pending_approvals > 0 %}
                <span class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                    {{ pending_approvals }}
                </span>
                {% endif %}
            </a>
            
            <button class="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all text-center">
                <div class="text-4xl mb-2">🎁</div>
                <p class="font-medium text-gray-800">Rewards</p>
                <p class="text-xs text-gray-500">Manage rewards</p>
            </button>
            
            <button class="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all text-center">
                <div class="text-4xl mb-2">📊</div>
                <p class="font-medium text-gray-800">Reports</p>
                <p class="text-xs text-gray-500">View analytics</p>
            </button>
        </div>
    </div>
    
</div>
{% endblock %}
*/