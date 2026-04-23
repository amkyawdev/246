/**
 * Burme AI - Main JavaScript
 * Button effects and utilities
 */

document.addEventListener('DOMContentLoaded', function() {
    initRippleEffects();
    initNavigation();
});

/**
 * Ripple Button Effects
 */
function initRippleEffects() {
    const buttons = document.querySelectorAll('.ripple, .btn');
    
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Create ripple element
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                width: 0;
                height: 0;
                left: ${x}px;
                top: ${y}px;
                transform: translate(-50%, -50%);
                pointer-events: none;
                transition: width 0.4s ease, height 0.4s ease, opacity 0.4s ease;
            `;
            
            // Add ripple to button
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);
            
            // Trigger animation
            setTimeout(function() {
                ripple.style.width = '200px';
                ripple.style.height = '200px';
                ripple.style.opacity = '0';
            }, 10);
            
            // Clean up
            setTimeout(function() {
                ripple.remove();
            }, 400);
        });
    });
}

/**
 * Navigation Active States
 */
function initNavigation() {
    // Set active state for current page
    const currentPath = window.location.pathname;
    
    // Desktop sidebar links
    document.querySelectorAll('.sidebar .nav-link').forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Format timestamp to readable date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!');
        });
    } else {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        textarea.remove();
        showToast('Copied to clipboard!');
    }
}

/**
 * Show toast notification
 */
function showToast(message, duration) {
    duration = duration || 2000;
    
    // Remove existing toast
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--accent, #E94560);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 0.875rem;
        z-index: 9999;
        animation: fadeIn 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove after duration
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, duration);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}