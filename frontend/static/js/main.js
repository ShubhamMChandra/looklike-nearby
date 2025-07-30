/**
 * Main JavaScript for LookLike Nearby Lead Generation Platform
 * 
 * WHAT: Frontend JavaScript handling authentication, API calls, UI interactions,
 *       and data management for the lead generation platform.
 * 
 * WHY: Provides interactive user interface for sales teams to search for prospects,
 *      manage campaigns, and organize reference clients without requiring
 *      technical knowledge.
 * 
 * HOW: Uses vanilla JavaScript with fetch API for backend communication,
 *      Bootstrap for UI components, and localStorage for session management.
 * 
 * DEPENDENCIES:
 * - Bootstrap 5.3: UI components and styling
 * - Font Awesome 6: Icons
 * - Browser APIs: fetch, localStorage, sessionStorage
 */

// Configuration
const API_BASE_URL = '/api';
const SESSION_KEY = 'looklike_session';

// Global state
let currentSession = null;
let referenceClients = [];
let campaigns = [];
let searchResults = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application and check authentication
 */
async function initializeApp() {
    // Check for existing session
    const savedSession = localStorage.getItem(SESSION_KEY);
    if (savedSession) {
        currentSession = savedSession;
        try {
            await loadInitialData();
            hideLoginModal();
        } catch (error) {
            console.error('Session validation failed:', error);
            showLoginModal();
        }
    } else {
        showLoginModal();
    }
    
    // Setup event listeners
    setupEventListeners();
}

/**
 * Setup event listeners for forms and interactions
 */
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Search form
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    
    // Reference client selection
    document.getElementById('referenceClient').addEventListener('change', handleReferenceClientChange);
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const password = document.getElementById('password').value;
    const loginButton = event.target.querySelector('button[type="submit"]');
    
    // Show loading state
    loginButton.disabled = true;
    loginButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Authenticating...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentSession = data.session_token;
            localStorage.setItem(SESSION_KEY, currentSession);
            
            await loadInitialData();
            hideLoginModal();
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Authentication failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('error', 'Connection error. Please try again.');
    } finally {
        // Reset button state
        loginButton.disabled = false;
        loginButton.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Access Platform';
        document.getElementById('password').value = '';
    }
}

/**
 * Handle search form submission
 */
async function handleSearch(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const searchParams = {
        reference_client_id: document.getElementById('referenceClient').value || null,
        business_name: document.getElementById('businessName').value,
        address: document.getElementById('address').value,
        business_type: document.getElementById('businessType').value,
        radius_miles: parseInt(document.getElementById('radius').value)
    };
    
    // Validate required fields
    if (!searchParams.reference_client_id && (!searchParams.business_name || !searchParams.address)) {
        showAlert('warning', 'Please select a reference client or enter business name and address.');
        return;
    }
    
    const searchButton = event.target.querySelector('button[type="submit"]');
    searchButton.disabled = true;
    searchButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
    
    try {
        const response = await apiCall('/search/prospects', 'POST', searchParams);
        searchResults = response.results || [];
        
        displaySearchResults(searchResults);
        showAlert('success', `Found ${searchResults.length} similar businesses`);
    } catch (error) {
        console.error('Search error:', error);
        showAlert('error', 'Search failed. Please try again.');
    } finally {
        searchButton.disabled = false;
        searchButton.innerHTML = '<i class="fas fa-search me-2"></i>Find Similar Businesses';
    }
}

/**
 * Handle reference client selection change
 */
function handleReferenceClientChange(event) {
    const clientId = event.target.value;
    if (clientId) {
        const client = referenceClients.find(c => c.id == clientId);
        if (client) {
            // Auto-fill form with client data
            document.getElementById('businessName').value = client.name;
            document.getElementById('address').value = client.address;
            document.getElementById('businessType').value = client.business_type || '';
        }
    } else {
        // Clear form when no client selected
        document.getElementById('businessName').value = '';
        document.getElementById('address').value = '';
        document.getElementById('businessType').value = '';
    }
}

/**
 * Load initial data (reference clients, campaigns, stats)
 */
async function loadInitialData() {
    try {
        // Load reference clients
        const clientsResponse = await apiCall('/reference-clients');
        referenceClients = clientsResponse.clients || [];
        updateReferenceClientsDropdown();
        updateReferenceClientsList();
        
        // Load campaigns
        const campaignsResponse = await apiCall('/campaigns');
        campaigns = campaignsResponse.campaigns || [];
        updateCampaignsList();
        
        // Update stats
        updateStats();
    } catch (error) {
        console.error('Failed to load initial data:', error);
        throw error;
    }
}

/**
 * Display search results in the UI
 */
function displaySearchResults(results) {
    const container = document.getElementById('searchResultsList');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-search fa-3x mb-3"></i>
                <p>No similar businesses found. Try adjusting your search criteria.</p>
            </div>
        `;
        return;
    }
    
    const resultsHTML = results.map(prospect => `
        <div class="prospect-card animate-slide-in">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h6 class="mb-1">${prospect.name}</h6>
                    <div class="prospect-rating mb-1">
                        ${generateStarRating(prospect.rating)}
                        <span class="ms-1">${prospect.rating || 'N/A'}</span>
                    </div>
                    <div class="prospect-distance">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        ${prospect.distance || 'N/A'} • ${prospect.address}
                    </div>
                </div>
                <div class="prospect-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="addToCampaign('${prospect.place_id}')">
                        <i class="fas fa-plus me-1"></i>Add to Campaign
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="viewProspectDetails('${prospect.place_id}')">
                        <i class="fas fa-eye me-1"></i>Details
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <small class="text-muted">
                        <i class="fas fa-tag me-1"></i>
                        ${prospect.business_type || 'Unknown type'}
                    </small>
                </div>
                <div class="col-md-6 text-end">
                    ${prospect.phone ? `<small><i class="fas fa-phone me-1"></i>${prospect.phone}</small>` : ''}
                    ${prospect.website ? `<br><small><i class="fas fa-globe me-1"></i><a href="${prospect.website}" target="_blank">Website</a></small>` : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = resultsHTML;
}

/**
 * Generate star rating HTML
 */
function generateStarRating(rating) {
    if (!rating) return '<span class="text-muted">No rating</span>';
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star prospect-rating"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt prospect-rating"></i>';
    }
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star prospect-rating"></i>';
    }
    
    return stars;
}

/**
 * Update reference clients dropdown
 */
function updateReferenceClientsDropdown() {
    const select = document.getElementById('referenceClient');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">Select existing client...</option>';
    
    referenceClients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = client.name;
        if (client.id == currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

/**
 * Update reference clients list in tab
 */
function updateReferenceClientsList() {
    const container = document.getElementById('referenceClientsList');
    
    if (referenceClients.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-building fa-3x mb-3"></i>
                <p>No reference clients yet. Add your first successful client as a reference point.</p>
            </div>
        `;
        return;
    }
    
    const clientsHTML = referenceClients.map(client => `
        <div class="card reference-client-card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title mb-1">${client.name}</h6>
                        <div class="client-location">
                            <i class="fas fa-map-marker-alt me-1"></i>
                            ${client.address}
                        </div>
                        ${client.business_type ? `<span class="client-type">${client.business_type}</span>` : ''}
                        ${client.notes ? `<p class="text-muted mt-2 mb-0"><small>${client.notes}</small></p>` : ''}
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                            Actions
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="useAsReference(${client.id})">
                                <i class="fas fa-search me-2"></i>Use for Search
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="editReferenceClient(${client.id})">
                                <i class="fas fa-edit me-2"></i>Edit
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deleteReferenceClient(${client.id})">
                                <i class="fas fa-trash me-2"></i>Delete
                            </a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = clientsHTML;
}

/**
 * Update campaigns list
 */
function updateCampaignsList() {
    const container = document.getElementById('campaignsList');
    
    if (campaigns.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-list fa-3x mb-3"></i>
                <p>No campaigns yet. Create your first campaign to organize prospects.</p>
            </div>
        `;
        return;
    }
    
    const campaignsHTML = campaigns.map(campaign => `
        <div class="card campaign-card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <h6 class="card-title mb-1">${campaign.name}</h6>
                        ${campaign.description ? `<p class="text-muted mb-2">${campaign.description}</p>` : ''}
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                            Actions
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="viewCampaign(${campaign.id})">
                                <i class="fas fa-eye me-2"></i>View Details
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="exportCampaign(${campaign.id})">
                                <i class="fas fa-download me-2"></i>Export
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deleteCampaign(${campaign.id})">
                                <i class="fas fa-trash me-2"></i>Delete
                            </a></li>
                        </ul>
                    </div>
                </div>
                <div class="campaign-stats">
                    <div class="campaign-stat">
                        <div class="campaign-stat-number">${campaign.prospect_count || 0}</div>
                        <small>Prospects</small>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-number">${campaign.contacted_count || 0}</div>
                        <small>Contacted</small>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-number">${campaign.qualified_count || 0}</div>
                        <small>Qualified</small>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = campaignsHTML;
}

/**
 * Update dashboard stats
 */
function updateStats() {
    document.getElementById('totalClients').textContent = referenceClients.length;
    document.getElementById('totalCampaigns').textContent = campaigns.length;
}

/**
 * Show/hide login modal
 */
function showLoginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

function hideLoginModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (modal) {
        modal.hide();
    }
}

/**
 * Logout function
 */
async function logout() {
    try {
        await apiCall('/auth/logout', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem(SESSION_KEY);
        currentSession = null;
        showLoginModal();
        
        // Clear data
        referenceClients = [];
        campaigns = [];
        searchResults = [];
        
        // Reset UI
        updateReferenceClientsDropdown();
        updateReferenceClientsList();
        updateCampaignsList();
        updateStats();
    }
}

/**
 * Generic API call function
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (currentSession) {
        options.headers['Authorization'] = `Bearer ${currentSession}`;
    }
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    if (response.status === 401) {
        // Session expired
        localStorage.removeItem(SESSION_KEY);
        currentSession = null;
        showLoginModal();
        throw new Error('Session expired');
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API call failed');
    }
    
    return await response.json();
}

/**
 * Show alert message
 */
function showAlert(type, message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alert, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Placeholder functions for future implementation
function addToCampaign(placeId) {
    showAlert('info', 'Add to campaign functionality coming soon!');
}

function viewProspectDetails(placeId) {
    showAlert('info', 'Prospect details view coming soon!');
}

function exportResults(format) {
    showAlert('info', `${format.toUpperCase()} export functionality coming soon!`);
}

function createCampaign() {
    showAlert('info', 'Create campaign functionality coming soon!');
}

function addReferenceClient() {
    showAlert('info', 'Add reference client functionality coming soon!');
}

function useAsReference(clientId) {
    document.getElementById('referenceClient').value = clientId;
    handleReferenceClientChange({ target: { value: clientId } });
    
    // Switch to search results tab
    const searchTab = document.querySelector('[data-bs-target="#searchResults"]');
    const tab = new bootstrap.Tab(searchTab);
    tab.show();
    
    showAlert('success', 'Reference client selected for search');
}

function editReferenceClient(clientId) {
    showAlert('info', 'Edit reference client functionality coming soon!');
}

function deleteReferenceClient(clientId) {
    showAlert('info', 'Delete reference client functionality coming soon!');
}

function viewCampaign(campaignId) {
    showAlert('info', 'View campaign functionality coming soon!');
}

function exportCampaign(campaignId) {
    showAlert('info', 'Export campaign functionality coming soon!');
}

function deleteCampaign(campaignId) {
    showAlert('info', 'Delete campaign functionality coming soon!');
} 