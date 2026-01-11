/**
 * predict.js
 * Frontend logic for AI Disease Prediction System
 * 
 * Handles:
 * - Form validation before submission
 * - AJAX API calls to /api/predict endpoint
 * - Chart.js visualization rendering
 * - Loading states and error handling
 * 
 * IMPORTANT: All displayed prediction values come from backend API responses.
 * No hardcoded or computed values on the client side.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Disease Predictor - Client-side script loaded');
    
    // Client-side form validation (optional enhancement)
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Basic validation
            const inputs = form.querySelectorAll('input[type="number"], input[type="text"], select');
            let isValid = true;
            
            inputs.forEach(input => {
                if (input.hasAttribute('required') && !input.value) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                showError('Please fill in all required fields.');
            }
        });
    });
});

/**
 * Make AJAX prediction request to API endpoint
 * This function can be used for programmatic predictions without form submission
 * 
 * @param {string} disease - Disease type ('diabetes', 'heart', 'breast')
 * @param {object} inputs - Dictionary of input features
 * @returns {Promise} - Promise resolving to API response
 */
async function makePrediction(disease, inputs) {
    const apiUrl = '/api/predict/';
    
    try {
        showLoading();
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                disease: disease,
                inputs: inputs
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (!response.ok) {
            throw new Error(data.error || 'Prediction failed');
        }
        
        return data;
        
    } catch (error) {
        hideLoading();
        showError(`Prediction error: ${error.message}`);
        throw error;
    }
}

/**
 * Display prediction results (for AJAX-based workflows)
 * All values displayed come directly from the API response
 * 
 * @param {object} result - API response object
 */
function displayPredictionResult(result) {
    // Redirect to result page using record_id
    if (result.record_id) {
        window.location.href = `/result/${result.record_id}/`;
    } else {
        console.error('No record_id in prediction result');
        showError('Prediction completed but could not retrieve results.');
    }
}

/**
 * Render probability chart using Chart.js
 * Values come from backend API response only
 * 
 * @param {string} canvasId - ID of canvas element
 * @param {object} probabilities - Probability dictionary from API
 */
function renderProbabilityChart(canvasId, probabilities) {
    const canvas = document.getElementById(canvasId);
    
    if (!canvas) {
        console.warn(`Canvas element ${canvasId} not found`);
        return;
    }
    
    const labels = Object.keys(probabilities);
    const data = Object.values(probabilities);
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(58, 28, 113, 0.8)',
                    'rgba(215, 109, 119, 0.8)',
                    'rgba(255, 175, 123, 0.8)'
                ],
                borderColor: [
                    'rgba(58, 28, 113, 1)',
                    'rgba(215, 109, 119, 1)',
                    'rgba(255, 175, 123, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#fff',
                        font: {
                            size: 14,
                            family: 'Inter, system-ui, Arial'
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const percentage = (value * 100).toFixed(2);
                            return `${label}: ${percentage}%`;
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 175, 123, 0.8)',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Show loading spinner
 */
function showLoading() {
    // Create and show loading overlay
    let loadingDiv = document.getElementById('loading-overlay');
    
    if (!loadingDiv) {
        loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        loadingDiv.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loadingDiv);
    }
    
    loadingDiv.style.display = 'flex';
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const loadingDiv = document.getElementById('loading-overlay');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

/**
 * Show error message
 * 
 * @param {string} message - Error message to display
 */
function showError(message) {
    // Create toast-style error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger position-fixed top-0 start-50 translate-middle-x mt-3';
    errorDiv.style.cssText = 'z-index: 10000; max-width: 500px;';
    errorDiv.innerHTML = `
        <strong>Error:</strong> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Show success message
 * 
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
    successDiv.style.cssText = 'z-index: 10000; max-width: 500px;';
    successDiv.innerHTML = `
        <strong>Success:</strong> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

/**
 * Validate numeric input range
 * 
 * @param {number} value - Value to validate
 * @param {number} min - Minimum allowed value
 * @param {number} max - Maximum allowed value
 * @returns {boolean} - True if valid
 */
function validateRange(value, min, max) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min && num <= max;
}

/**
 * Format probability as percentage
 * 
 * @param {number} probability - Probability value (0-1)
 * @returns {string} - Formatted percentage string
 */
function formatProbability(probability) {
    return (probability * 100).toFixed(2) + '%';
}

// Export functions for use in templates
window.PredictorAPI = {
    makePrediction,
    displayPredictionResult,
    renderProbabilityChart,
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    validateRange,
    formatProbability
};
