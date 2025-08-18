// Main JavaScript for Garbage Collection System

// Global variables
let notificationInterval;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize image preview
    initializeImagePreview();
    
    // Initialize geolocation if supported
    initializeGeolocation();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize real-time features
    initializeRealTimeFeatures();
}

// Image preview functionality
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, input);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function showImagePreview(src, inputElement) {
    // Remove existing preview
    const existingPreview = inputElement.parentNode.querySelector('.image-preview-container');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    // Create preview container
    const previewContainer = document.createElement('div');
    previewContainer.className = 'image-preview-container mt-3';
    
    const img = document.createElement('img');
    img.src = src;
    img.className = 'image-preview';
    img.style.maxWidth = '200px';
    img.style.maxHeight = '200px';
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger mt-2';
    removeBtn.innerHTML = '<i class="bi bi-trash"></i> Remove';
    removeBtn.onclick = function() {
        inputElement.value = '';
        previewContainer.remove();
    };
    
    previewContainer.appendChild(img);
    previewContainer.appendChild(document.createElement('br'));
    previewContainer.appendChild(removeBtn);
    
    inputElement.parentNode.appendChild(previewContainer);
}

// Geolocation functionality
function initializeGeolocation() {
    const getLocationBtn = document.getElementById('get-location-btn');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', getCurrentLocation);
    }
}

function getCurrentLocation() {
    const btn = document.getElementById('get-location-btn');
    const latInput = document.querySelector('input[name="latitude"]');
    const lngInput = document.querySelector('input[name="longitude"]');
    
    if (!navigator.geolocation) {
        showAlert('Geolocation is not supported by this browser.', 'warning');
        return;
    }
    
    btn.innerHTML = '<i class="bi bi-geo-alt"></i> Getting location...';
    btn.disabled = true;
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            if (latInput) latInput.value = position.coords.latitude;
            if (lngInput) lngInput.value = position.coords.longitude;
            
            btn.innerHTML = '<i class="bi bi-check-circle text-success"></i> Location obtained';
            showAlert('Location captured successfully!', 'success');
            
            setTimeout(() => {
                btn.innerHTML = '<i class="bi bi-geo-alt"></i> Get Current Location';
                btn.disabled = false;
            }, 2000);
        },
        function(error) {
            btn.innerHTML = '<i class="bi bi-geo-alt"></i> Get Current Location';
            btn.disabled = false;
            
            let message = 'Unable to get location. ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message += 'Please allow location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    message += 'Location request timed out.';
                    break;
                default:
                    message += 'Unknown error occurred.';
                    break;
            }
            
            showAlert(message, 'warning');
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Real-time features
function initializeRealTimeFeatures() {
    // Update timestamps
    updateTimestamps();
    setInterval(updateTimestamps, 60000); // Update every minute
    
    // Initialize notification polling for authenticated users
    if (document.querySelector('#notification-badge')) {
        startNotificationPolling();
    }
}

function updateTimestamps() {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach(element => {
        const timestamp = new Date(element.dataset.timestamp);
        element.textContent = getTimeAgo(timestamp);
    });
}

function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
    if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
    if (diffInSeconds < 604800) return Math.floor(diffInSeconds / 86400) + ' days ago';
    
    return date.toLocaleDateString();
}

function startNotificationPolling() {
    // Clear existing interval
    if (notificationInterval) {
        clearInterval(notificationInterval);
    }
    
    // Start new polling interval
    notificationInterval = setInterval(function() {
        fetch('/notifications/api/unread-count/')
            .then(response => response.json())
            .then(data => {
                updateNotificationBadge(data.unread_count);
            })
            .catch(error => {
                console.log('Notification polling error:', error);
            });
    }, 30000); // Poll every 30 seconds
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    
    let icon = 'bi-info-circle';
    if (type === 'success') icon = 'bi-check-circle';
    else if (type === 'warning') icon = 'bi-exclamation-triangle';
    else if (type === 'danger') icon = 'bi-exclamation-octagon';
    
    alertContainer.innerHTML = `
        <i class="bi ${icon}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the beginning of main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertContainer, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(alertContainer);
            alert.close();
        }, 5000);
    }
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function showLoading(element) {
    element.innerHTML = '<div class="loading-spinner"></div>';
    element.disabled = true;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// AJAX helper functions
function csrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function makeRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': csrfToken(),
            'Content-Type': 'application/json',
        },
    };
    
    return fetch(url, { ...defaultOptions, ...options });
}

// Request management functions
function assignRequest(requestId, labourId) {
    const btn = document.querySelector(`[data-request-id="${requestId}"]`);
    const originalContent = btn.innerHTML;
    
    showLoading(btn);
    
    makeRequest(`/requests/councilor/assign/${requestId}/`, {
        method: 'POST',
        body: JSON.stringify({
            labour_id: labourId
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(btn, originalContent);
        if (data.success) {
            showAlert('Request assigned successfully!', 'success');
            location.reload();
        } else {
            showAlert(data.message || 'Error assigning request', 'danger');
        }
    })
    .catch(error => {
        hideLoading(btn, originalContent);
        showAlert('Error assigning request', 'danger');
        console.error('Error:', error);
    });
}

function approveReport(reportId) {
    confirmAction('Are you sure you want to approve this report?', function() {
        const btn = document.querySelector(`[data-report-id="${reportId}"]`);
        const originalContent = btn.innerHTML;
        
        showLoading(btn);
        
        makeRequest(`/requests/councilor/report/${reportId}/approve/`, {
            method: 'POST'
        })
        .then(response => {
            if (response.ok) {
                showAlert('Report approved successfully!', 'success');
                location.reload();
            } else {
                throw new Error('Failed to approve report');
            }
        })
        .catch(error => {
            hideLoading(btn, originalContent);
            showAlert('Error approving report', 'danger');
            console.error('Error:', error);
        });
    });
}

function rejectReport(reportId) {
    const reason = prompt('Please provide a reason for rejection:');
    if (reason) {
        const btn = document.querySelector(`[data-report-id="${reportId}"]`);
        const originalContent = btn.innerHTML;
        
        showLoading(btn);
        
        makeRequest(`/requests/councilor/report/${reportId}/reject/`, {
            method: 'POST',
            body: JSON.stringify({
                rejection_reason: reason
            })
        })
        .then(response => {
            if (response.ok) {
                showAlert('Report rejected successfully!', 'success');
                location.reload();
            } else {
                throw new Error('Failed to reject report');
            }
        })
        .catch(error => {
            hideLoading(btn, originalContent);
            showAlert('Error rejecting report', 'danger');
            console.error('Error:', error);
        });
    }
}

// Export functions for global access
window.GarbageCollectionApp = {
    showAlert,
    confirmAction,
    assignRequest,
    approveReport,
    rejectReport,
    getCurrentLocation,
    updateNotificationBadge
};
