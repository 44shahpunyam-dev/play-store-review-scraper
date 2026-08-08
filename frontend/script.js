// Configuration
const API_BASE_URL = '';

// DOM Elements
const playStoreUrlInput = document.getElementById('playStoreUrl');
const fromDateInput = document.getElementById('fromDate');
const toDateInput = document.getElementById('toDate');
const hintInput = document.getElementById('hint');
const ratingInputs = document.querySelectorAll('input[name="rating"]');
const scrapeBtn = document.getElementById('scrapeBtn');
const loadingState = document.getElementById('loadingState');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');
const resultMessage = document.getElementById('resultMessage');
const previewContainer = document.getElementById('previewContainer');
const previewTable = document.getElementById('previewTable');
const previewBody = document.getElementById('previewBody');
const downloadBtn = document.getElementById('downloadBtn');

// State
let currentFilename = null;
let scrapeInProgress = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    fromDateInput.value = today;
    toDateInput.value = today;

    // Event listeners
    scrapeBtn.addEventListener('click', handleScrape);
    downloadBtn.addEventListener('click', handleDownload);
    playStoreUrlInput.addEventListener('blur', validateUrl);
});

/**
 * Validate Play Store URL format
 */
function validateUrl() {
    const url = playStoreUrlInput.value.trim();
    const errorEl = document.getElementById('urlError');

    if (!url) {
        errorEl.textContent = '';
        return true;
    }

    const pattern = /play\.google\.com\/store\/apps\/details\?id=([a-zA-Z0-9._]+)/;
    if (pattern.test(url)) {
        errorEl.textContent = '';
        return true;
    } else {
        errorEl.textContent = 'Invalid Google Play Store URL format';
        return false;
    }
}

/**
 * Validate all form inputs
 */
function validateForm() {
    const url = playStoreUrlInput.value.trim();
    const fromDate = fromDateInput.value;
    const toDate = toDateInput.value;
    const dateError = document.getElementById('dateError');

    // Validate URL
    if (!url) {
        document.getElementById('urlError').textContent = 'Please enter a Play Store URL';
        return false;
    }

    if (!validateUrl()) {
        return false;
    }

    // Validate dates
    if (!fromDate) {
        dateError.textContent = 'Please select a From Date';
        return false;
    }

    if (!toDate) {
        dateError.textContent = 'Please select a To Date';
        return false;
    }

    if (fromDate > toDate) {
        dateError.textContent = 'From date cannot be later than To date';
        return false;
    }

    dateError.textContent = '';
    return true;
}

/**
 * Get selected rating
 */
function getSelectedRating() {
    for (let radio of ratingInputs) {
        if (radio.checked) {
            return parseInt(radio.value);
        }
    }
    return 0;
}

/**
 * Update status message with animation
 */
function updateStatus(message) {
    statusMessage.textContent = message;
    statusMessage.style.animation = 'none';
    setTimeout(() => {
        statusMessage.style.animation = 'fadeIn 0.3s ease-in';
    }, 10);
}

/**
 * Handle scrape button click
 */
async function handleScrape() {
    // Validate form
    if (!validateForm()) {
        return;
    }

    // Prevent duplicate submissions
    if (scrapeInProgress) {
        return;
    }

    scrapeInProgress = true;
    scrapeBtn.disabled = true;

    // Show loading state
    loadingState.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    updateStatus('Connecting to Google Play Store...');

    try {
        const url = playStoreUrlInput.value.trim();
        const fromDate = fromDateInput.value;
        const toDate = toDateInput.value;
        const hint = hintInput.value.trim();
        const rating = getSelectedRating();

        // Simulate progress updates
        setTimeout(() => updateStatus('Fetching reviews...'), 500);
        setTimeout(() => updateStatus('Processing reviews...'), 2000);
        setTimeout(() => updateStatus('Generating Excel file...'), 4000);

        // Make API request
        const response = await fetch(`${API_BASE_URL}/api/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                from_date: fromDate,
                to_date: toDate,
                hint: hint,
                rating: rating
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Scraping failed');
        }

        const data = await response.json();

        // Hide loading
        loadingState.classList.add('hidden');

        // Show results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        loadingState.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        resultMessage.className = 'result-message error';
        resultMessage.textContent = error.message || 'An error occurred during scraping';
        previewContainer.classList.add('hidden');
        downloadBtn.classList.add('hidden');
    } finally {
        scrapeInProgress = false;
        scrapeBtn.disabled = false;
    }
}

/**
 * Display results
 */
function displayResults(data) {
    resultsSection.classList.remove('hidden');

    if (!data.success) {
        resultMessage.className = 'result-message error';
        resultMessage.textContent = data.message;
        previewContainer.classList.add('hidden');
        downloadBtn.classList.add('hidden');
        currentFilename = null;
        return;
    }

    // Show success message
    resultMessage.className = 'result-message success';
    resultMessage.textContent = `✓ ${data.message}`;
    currentFilename = data.filename;

    // Show preview if available
    if (data.preview && data.preview.length > 0) {
        previewContainer.classList.remove('hidden');
        populatePreviewTable(data.preview);
    } else {
        previewContainer.classList.add('hidden');
    }

    // Show download button
    downloadBtn.classList.remove('hidden');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Populate preview table
 */
function populatePreviewTable(preview) {
    previewBody.innerHTML = '';

    preview.forEach(review => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(review.User)}</td>
            <td>${escapeHtml(review.Review)}</td>
            <td>${escapeHtml(review.Rating)}</td>
            <td>${escapeHtml(review.Date)}</td>
        `;
        previewBody.appendChild(row);
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle download
 */
function handleDownload() {
    if (!currentFilename) {
        alert('No file to download');
        return;
    }

    // Create download link
    const downloadUrl = `${API_BASE_URL}/api/download/${encodeURIComponent(currentFilename)}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = currentFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Handle API connection check on page load
 */
async function checkApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            console.log('API connection successful');
        } else {
            console.warn('API connection issue');
        }
    } catch (error) {
        console.warn('Cannot connect to backend API:', error);
    }
}

// Check API connection
setTimeout(checkApiConnection, 500);
