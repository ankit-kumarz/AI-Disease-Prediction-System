/**
 * AI Disease Predictor - Enhanced UI Features
 * Animations, Dark Mode, Loading States, and Interactive Elements
 */

// =====================================================
// 1. DARK MODE TOGGLE
// =====================================================
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Check saved preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        body.classList.add('dark-mode');
    }
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            
            // Update icon
            const icon = darkModeToggle.querySelector('i');
            icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        });
    }
}

// =====================================================
// 2. LOADING OVERLAY
// =====================================================
function showLoading() {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(overlay);
    }
    setTimeout(() => overlay.classList.add('active'), 10);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Add loading to form submissions
function attachLoadingToForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            showLoading();
        });
    });
}

// =====================================================
// 3. ANIMATED STATISTICS (CountUp)
// =====================================================
function animateNumber(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = Math.round(target);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

function initAnimatedStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.value || entry.target.textContent);
                animateNumber(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => observer.observe(stat));
}

// =====================================================
// 4. SMOOTH PAGE TRANSITIONS
// =====================================================
function initPageTransitions() {
    // Add transition class to main content
    const mainContent = document.querySelector('.container, .container-fluid');
    if (mainContent) {
        mainContent.classList.add('page-transition');
    }
    
    // Animate cards on scroll
    const cards = document.querySelectorAll('.card, .glass-card');
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.animation = `fadeInUp 0.6s ease-out forwards`;
                }, index * 100);
                cardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        cardObserver.observe(card);
    });
}

// =====================================================
// 5. ENHANCED FORM INPUTS with Live Feedback
// =====================================================
function initEnhancedForms() {
    // Range sliders with live value display
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        // Create value display
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'range-value';
        valueDisplay.textContent = input.value;
        input.parentNode.appendChild(valueDisplay);
        
        // Update on input
        input.addEventListener('input', (e) => {
            valueDisplay.textContent = e.target.value;
        });
    });
    
    // Add validation feedback
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (input.checkValidity()) {
                input.style.borderColor = '#28a745';
            } else {
                input.style.borderColor = '#dc3545';
            }
        });
        
        input.addEventListener('focus', () => {
            input.style.borderColor = 'var(--accent3)';
        });
    });
}

// =====================================================
// 6. INTERACTIVE CHARTS
// =====================================================
function createRiskChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 175, 123, 0.8)',
                    'rgba(215, 109, 119, 0.8)',
                    'rgba(58, 28, 113, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#fff',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 2000
            }
        }
    });
}

function createTrendChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Risk Level',
                data: data,
                borderColor: '#D76D77',
                backgroundColor: 'rgba(215, 109, 119, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#FFAF7B',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// =====================================================
// 7. PARALLAX EFFECT
// =====================================================
function initParallax() {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax-section');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

// =====================================================
// 8. PULSE ANIMATION FOR HIGH RISK
// =====================================================
function initPulseAlerts() {
    const highRiskElements = document.querySelectorAll('.badge.bg-danger, .text-danger');
    highRiskElements.forEach(element => {
        if (element.textContent.toLowerCase().includes('high')) {
            element.classList.add('pulse-alert');
        }
    });
}

// =====================================================
// 9. PROGRESS BAR ANIMATION
// =====================================================
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = width;
                    bar.classList.add('progress-bar-animated');
                }, 100);
                observer.unobserve(bar);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// =====================================================
// 10. TOOLTIP INITIALIZATION
// =====================================================
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// =====================================================
// INITIALIZATION
// =====================================================
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    attachLoadingToForms();
    initAnimatedStats();
    initPageTransitions();
    initEnhancedForms();
    initParallax();
    initPulseAlerts();
    animateProgressBars();
    initTooltips();
    
    // Hide loading if it's showing
    setTimeout(hideLoading, 500);
});

// Export functions for use in other scripts
window.aiPredictor = {
    showLoading,
    hideLoading,
    createRiskChart,
    createTrendChart,
    animateNumber
};
