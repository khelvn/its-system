// Utility functions for the entire application

// Format number to 2 decimal places
function formatNumber(num) {
    return Math.round(num * 100) / 100;
}

// Show loading spinner
function showLoading(element) {
    element.classList.add('loading');
}

// Hide loading spinner
function hideLoading(element) {
    element.classList.remove('loading');
}

// Display error message
function showError(message, element) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    element.appendChild(errorDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Add loading spinners to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function() {
        if (!this.classList.contains('loading')) {
            showLoading(this);
        }
    });
});