// KOINZA Main JavaScript
// Handles UI interactions and API calls

// State management
const state = {
    stage: 'input', // input, searching, results
    results: [],
    currentFeedbackItem: null
};

// DOM Elements
const elements = {
    // Stages
    inputStage: document.getElementById('inputStage'),
    searchingStage: document.getElementById('searchingStage'),
    resultsStage: document.getElementById('resultsStage'),
    
    // Input elements
    searchInput: document.getElementById('searchInput'),
    searchBtn: document.getElementById('searchBtn'),
    priceMin: document.getElementById('priceMin'),
    priceMax: document.getElementById('priceMax'),
    brand: document.getElementById('brand'),
    country: document.getElementById('country'),
    delivery: document.getElementById('delivery'),
    
    // Results
    resultsGrid: document.getElementById('resultsGrid'),
    newSearchBtn: document.getElementById('newSearchBtn'),
    searchProgress: document.getElementById('searchProgress'),
    
    // Modals
    settingsModal: document.getElementById('settingsModal'),
    settingsBtn: document.getElementById('settingsBtn'),
    closeSettings: document.getElementById('closeSettings'),
    feedbackModal: document.getElementById('feedbackModal'),
    closeFeedback: document.getElementById('closeFeedback'),
    cancelFeedback: document.getElementById('cancelFeedback'),
    submitFeedback: document.getElementById('submitFeedback'),
    feedbackText: document.getElementById('feedbackText'),
    
    // Error
    errorAlert: document.getElementById('errorAlert'),
    errorText: document.getElementById('errorText'),
    closeError: document.getElementById('closeError'),
    
    // Settings
    topCount: document.getElementById('topCount')
};

// API Configuration
const API_BASE = window.location.origin;

// Initialize app
function init() {
    setupEventListeners();
    restoreSettings();
}

// Setup all event listeners
function setupEventListeners() {
    // Search
    elements.searchBtn.addEventListener('click', handleSearch);
    elements.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Navigation
    elements.newSearchBtn.addEventListener('click', () => switchStage('input'));
    
    // Settings modal
    elements.settingsBtn.addEventListener('click', () => showModal('settings'));
    elements.closeSettings.addEventListener('click', () => hideModal('settings'));
    elements.topCount.addEventListener('change', saveSettings);
    
    // Feedback modal
    elements.closeFeedback.addEventListener('click', () => hideModal('feedback'));
    elements.cancelFeedback.addEventListener('click', () => hideModal('feedback'));
    elements.submitFeedback.addEventListener('click', handleFeedbackSubmit);
    
    // Error alert
    elements.closeError.addEventListener('click', hideError);
    
    // Close modals on overlay click
    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal || e.target.classList.contains('modal-overlay')) {
            hideModal('settings');
        }
    });
    
    elements.feedbackModal.addEventListener('click', (e) => {
        if (e.target === elements.feedbackModal || e.target.classList.contains('modal-overlay')) {
            hideModal('feedback');
        }
    });
}

// Stage management
function switchStage(stage) {
    state.stage = stage;
    
    // Hide all stages
    elements.inputStage.classList.remove('active');
    elements.searchingStage.classList.remove('active');
    elements.resultsStage.classList.remove('active');
    
    // Show target stage
    switch(stage) {
        case 'input':
            elements.inputStage.classList.add('active');
            break;
        case 'searching':
            elements.searchingStage.classList.add('active');
            break;
        case 'results':
            elements.resultsStage.classList.add('active');
            break;
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Handle search
async function handleSearch() {
    const query = elements.searchInput.value.trim();
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    // Gather specs
    const specs = {
        priceMin: elements.priceMin.value,
        priceMax: elements.priceMax.value,
        brand: elements.brand.value,
        country: elements.country.value,
        delivery: elements.delivery.value
    };
    
    // Switch to searching stage
    switchStage('searching');
    hideError();
    
    try {
        // Simulate progress updates
        updateSearchProgress('🔥 Analyzing trends on social media and Google Trends...');
        
        // Make API call
        const response = await fetch(`${API_BASE}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, specs })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        updateSearchProgress('🛍️ Searching Amazon, eBay, AliExpress and other major shops...');
        await sleep(2000);
        
        updateSearchProgress('⭐ Verifying quality with trusted reviews and HTTPS sources...');
        await sleep(2000);
        
        updateSearchProgress('✨ Filtering top results and creating product cards...');
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data.results || data.results.length === 0) {
            throw new Error('No products found matching your criteria');
        }
        
        // Display results
        state.results = data.results;
        displayResults();
        switchStage('results');
        
    } catch (error) {
        console.error('Search error:', error);
        showError(error.message || 'Search failed. Please try again.');
        switchStage('input');
    }
}

// Update search progress text
function updateSearchProgress(text) {
    elements.searchProgress.textContent = text;
}

// Display results
function displayResults() {
    elements.resultsGrid.innerHTML = '';
    
    state.results.forEach(product => {
        const card = createProductCard(product);
        elements.resultsGrid.appendChild(card);
    });
}

// Create product card
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const hasDiscount = product.originalPrice && product.originalPrice > product.price;
    const hasTrending = product.trending;
    
    card.innerHTML = `
        <div class="product-content">
            <div class="product-header">
                <h3 class="product-name">${escapeHtml(product.name)}</h3>
                <p class="product-brand">${escapeHtml(product.brand)}</p>
                ${product.source ? `<p class="product-source">from ${escapeHtml(product.source)}</p>` : ''}
            </div>
            
            ${product.rating ? `
                <div class="product-rating">
                    <div class="rating-value">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                        <span>${product.rating}</span>
                    </div>
                    ${product.reviews ? `<span class="rating-count">(${formatNumber(product.reviews)})</span>` : ''}
                </div>
            ` : ''}
            
            <div class="product-price">
                <span class="price-current">$${product.price.toFixed(2)}</span>
                ${hasDiscount ? `
                    <span class="price-original">$${product.originalPrice.toFixed(2)}</span>
                    <span class="price-discount">-${product.discount}%</span>
                ` : ''}
            </div>
            
            ${product.shipping ? `
                <div class="product-info">
                    <div class="info-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="1" y="3" width="15" height="13"></rect>
                            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                            <circle cx="5.5" cy="18.5" r="2.5"></circle>
                            <circle cx="18.5" cy="18.5" r="2.5"></circle>
                        </svg>
                        ${escapeHtml(product.shipping)}
                    </div>
                </div>
            ` : ''}
            
            ${hasTrending ? `
                <div class="trending-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                    </svg>
                    Trending
                </div>
            ` : ''}
            
            <div class="product-actions">
                <button class="btn btn-primary" onclick="handleBuy('${escapeHtml(product.buyLink || '')}')">
                    View & Buy
                </button>
                <button class="btn btn-icon" onclick="handleFeedback(${product.id})" title="Not what you meant?">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Handle buy click
function handleBuy(buyLink) {
    if (buyLink && buyLink !== '') {
        window.open(buyLink, '_blank');
    } else {
        showError('Product link not available');
    }
}

// Handle feedback
function handleFeedback(itemId) {
    state.currentFeedbackItem = itemId;
    showModal('feedback');
}

// Handle feedback submit
function handleFeedbackSubmit() {
    const feedback = elements.feedbackText.value.trim();
    
    if (!feedback) {
        alert('Please enter your feedback');
        return;
    }
    
    // In a real app, send feedback to server
    console.log('Feedback submitted:', {
        itemId: state.currentFeedbackItem,
        feedback: feedback
    });
    
    alert('Thank you! Your feedback helps us improve.');
    elements.feedbackText.value = '';
    hideModal('feedback');
}

// Modal management
function showModal(type) {
    if (type === 'settings') {
        elements.settingsModal.classList.remove('hidden');
    } else if (type === 'feedback') {
        elements.feedbackModal.classList.remove('hidden');
    }
}

function hideModal(type) {
    if (type === 'settings') {
        elements.settingsModal.classList.add('hidden');
    } else if (type === 'feedback') {
        elements.feedbackModal.classList.add('hidden');
        elements.feedbackText.value = '';
    }
}

// Error handling
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorAlert.classList.remove('hidden');
}

function hideError() {
    elements.errorAlert.classList.add('hidden');
}

// Settings
function saveSettings() {
    const settings = {
        topCount: elements.topCount.value
    };
    localStorage.setItem('koinza_settings', JSON.stringify(settings));
}

function restoreSettings() {
    const saved = localStorage.getItem('koinza_settings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            if (settings.topCount) {
                elements.topCount.value = settings.topCount;
            }
        } catch (e) {
            console.error('Failed to restore settings:', e);
        }
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    return num.toLocaleString();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}