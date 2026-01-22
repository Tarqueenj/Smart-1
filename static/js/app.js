// SmartTriage AI - Main JavaScript Application

// Global variables
let currentUser = null;
let socket = null;
let notifications = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeRealTimeUpdates();
});

// Initialize app
function initializeApp() {
    // Set current user based on page
    const path = window.location.pathname;
    if (path.includes('nurse')) {
        currentUser = { type: 'nurse', name: 'Nurse Staff' };
    } else if (path.includes('clinician')) {
        currentUser = { type: 'clinician', name: 'Dr. Sarah Johnson' };
    } else if (path.includes('admin')) {
        currentUser = { type: 'admin', name: 'Administrator' };
    } else {
        currentUser = { type: 'patient', name: 'Patient' };
    }
    
    console.log('SmartTriage AI initialized for:', currentUser.type);
}

// Setup event listeners
function setupEventListeners() {
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Voice input (if available)
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', handleVoiceInput);
    }
    
    // Quick symptom buttons
    const symptomBtns = document.querySelectorAll('.symptom-btn');
    symptomBtns.forEach(btn => {
        btn.addEventListener('click', handleQuickSymptom);
    });
    
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }
    
    // Notification bell
    const notificationBell = document.querySelector('.fa-bell').parentElement;
    if (notificationBell) {
        notificationBell.addEventListener('click', showNotifications);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Handle form submissions
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    }
    
    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Form submitted successfully', 'success');
            handleFormSuccess(result, form);
        } else {
            throw new Error(result.message || 'Form submission failed');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    } finally {
        // Reset button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
        }
    }
}

// Handle form success
function handleFormSuccess(result, form) {
    const path = window.location.pathname;
    
    if (path.includes('patient')) {
        // Show triage results
        showTriageResults(result);
    } else if (path.includes('nurse')) {
        // Refresh patient queue
        loadPatients();
    } else if (path.includes('clinician')) {
        // Update clinical summary
        updateClinicalSummary(result);
    } else if (path.includes('admin')) {
        // Refresh analytics
        loadAnalytics();
    }
}

// Handle voice input
function handleVoiceInput() {
    const voiceBtn = document.getElementById('voice-btn');
    const symptomsTextarea = document.getElementById('symptoms');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showNotification('Voice input not supported in your browser', 'warning');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = function() {
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceBtn.classList.add('bg-red-600', 'hover:bg-red-700');
        showNotification('Listening... Speak clearly', 'info');
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        symptomsTextarea.value = transcript;
        showNotification('Voice input captured', 'success');
    };
    
    recognition.onerror = function(event) {
        showNotification('Voice input error: ' + event.error, 'error');
        resetVoiceButton();
    };
    
    recognition.onend = function() {
        resetVoiceButton();
    };
    
    recognition.start();
    
    function resetVoiceButton() {
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
    }
}

// Handle quick symptom buttons
function handleQuickSymptom(e) {
    const btn = e.target;
    const symptomsTextarea = document.getElementById('symptoms');
    const symptom = btn.textContent.trim();
    
    if (symptomsTextarea) {
        const currentValue = symptomsTextarea.value.trim();
        if (currentValue) {
            symptomsTextarea.value = currentValue + ', ' + symptom;
        } else {
            symptomsTextarea.value = symptom;
        }
        
        // Visual feedback
        btn.classList.add('bg-blue-100', 'text-blue-700');
        setTimeout(() => {
            btn.classList.remove('bg-blue-100', 'text-blue-700');
        }, 300);
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.querySelector('.mobile-menu-overlay');
    
    if (mobileMenu && overlay) {
        mobileMenu.classList.toggle('active');
        overlay.classList.toggle('active');
    }
}

// Show notifications
function showNotifications() {
    // Create notification dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'absolute top-12 right-4 w-80 bg-white rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto';
    
    dropdown.innerHTML = `
        <div class="p-4 border-b">
            <h3 class="font-semibold text-gray-900">Notifications</h3>
        </div>
        <div class="divide-y">
            ${notifications.length > 0 ? notifications.map(notif => `
                <div class="p-4 hover:bg-gray-50">
                    <div class="flex items-start">
                        <i class="fas fa-${getNotificationIcon(notif.type)} text-${getNotificationColor(notif.type)}-600 mt-1 mr-3"></i>
                        <div class="flex-1">
                            <p class="text-sm text-gray-900">${notif.message}</p>
                            <p class="text-xs text-gray-500 mt-1">${formatTime(notif.timestamp)}</p>
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="p-4 text-center text-gray-500">No notifications</div>'}
        </div>
    `;
    
    document.body.appendChild(dropdown);
    
    // Close on outside click
    setTimeout(() => {
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target)) {
                document.body.removeChild(dropdown);
                document.removeEventListener('click', closeDropdown);
            }
        });
    }, 100);
}

// Handle keyboard shortcuts
function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K for quick search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        showQuickSearch();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeAllModals();
    }
    
    // Ctrl/Cmd + R for refresh (override browser refresh)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshCurrentView();
    }
}

// Show quick search
function showQuickSearch() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
            <div class="p-4 border-b">
                <input type="text" id="quick-search-input" placeholder="Search patients, symptoms, or actions..." 
                       class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                       autofocus>
            </div>
            <div id="quick-search-results" class="max-h-96 overflow-y-auto">
                <!-- Results will be loaded here -->
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const input = modal.querySelector('#quick-search-input');
    input.addEventListener('input', handleQuickSearch);
    
    // Close on escape
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Handle quick search
async function handleQuickSearch(e) {
    const query = e.target.value.toLowerCase();
    const resultsContainer = document.getElementById('quick-search-results');
    
    if (query.length < 2) {
        resultsContainer.innerHTML = '<div class="p-4 text-center text-gray-500">Type at least 2 characters to search</div>';
        return;
    }
    
    try {
        const response = await fetch('/api/search?q=' + encodeURIComponent(query));
        const results = await response.json();
        
        if (results.length > 0) {
            resultsContainer.innerHTML = results.map(result => `
                <div class="p-4 hover:bg-gray-50 cursor-pointer border-b" onclick="handleSearchResult('${result.type}', '${result.id}')">
                    <div class="flex items-center">
                        <i class="fas fa-${getResultIcon(result.type)} text-gray-600 mr-3"></i>
                        <div>
                            <p class="font-medium text-gray-900">${result.title}</p>
                            <p class="text-sm text-gray-600">${result.description}</p>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            resultsContainer.innerHTML = '<div class="p-4 text-center text-gray-500">No results found</div>';
        }
    } catch (error) {
        resultsContainer.innerHTML = '<div class="p-4 text-center text-red-500">Search error</div>';
    }
}

// Initialize real-time updates
function initializeRealTimeUpdates() {
    // Simulate WebSocket connection for real-time updates
    setInterval(() => {
        if (currentUser.type === 'nurse' || currentUser.type === 'clinician') {
            checkForUpdates();
        }
    }, 30000); // Check every 30 seconds
}

// Check for updates
async function checkForUpdates() {
    try {
        const response = await fetch('/api/updates');
        const updates = await response.json();
        
        if (updates.length > 0) {
            updates.forEach(update => {
                showNotification(update.message, update.type);
                notifications.unshift({
                    message: update.message,
                    type: update.type,
                    timestamp: new Date()
                });
            });
            
            // Limit notifications to 50
            if (notifications.length > 50) {
                notifications = notifications.slice(0, 50);
            }
        }
    } catch (error) {
        console.error('Failed to check for updates:', error);
    }
}

// Refresh current view
function refreshCurrentView() {
    const path = window.location.pathname;
    
    if (path.includes('nurse')) {
        loadPatients();
    } else if (path.includes('clinician')) {
        loadPatients();
    } else if (path.includes('admin')) {
        loadAnalytics();
    }
    
    showNotification('View refreshed', 'info');
}

// Close all modals
function closeAllModals() {
    const modals = document.querySelectorAll('.fixed.inset-0');
    modals.forEach(modal => {
        if (modal.classList.contains('bg-black') || modal.classList.contains('bg-gray-600')) {
            modal.remove();
        }
    });
}

// Utility functions
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'blue'
    };
    return colors[type] || 'blue';
}

function getResultIcon(type) {
    const icons = {
        'patient': 'user',
        'symptom': 'notes-medical',
        'action': 'tasks',
        'report': 'file-medical'
    };
    return icons[type] || 'file';
}

function formatTime(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    if (diff < 60000) {
        return 'Just now';
    } else if (diff < 3600000) {
        return Math.floor(diff / 60000) + ' minutes ago';
    } else if (diff < 86400000) {
        return Math.floor(diff / 3600000) + ' hours ago';
    } else {
        return time.toLocaleDateString();
    }
}

// Export functions for global use
window.SmartTriage = {
    showNotification,
    refreshCurrentView,
    closeAllModals,
    handleVoiceInput,
    loadPatients,
    loadAnalytics
};
