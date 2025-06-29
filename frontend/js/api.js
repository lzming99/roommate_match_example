// API wrapper for backend communication
const API = {
    baseURL: 'http://localhost:5100', // base URL for backend API server.
    authToken: null,
    
    // Set authentication token
    setAuthToken(token) { // store auth token in memory and local storage
        this.authToken = token;
        localStorage.setItem('auth_token', token);
    },
    
    // Clear authentication
    clearAuth() {
        this.authToken = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
    },
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add auth token if available
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },
    
    // Authentication endpoints
    auth: {
        async register(userData) {
            const data = await API.request('/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            
            if (data.access_token) {
                API.setAuthToken(data.access_token);
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }
            
            return data;
        },
        
        async login(credentials) {
            const data = await API.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify(credentials)
            });
            
            if (data.access_token) {
                API.setAuthToken(data.access_token);
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }
            
            return data;
        }
    },
    
    // Profile endpoints
    profile: {
        async get() {
            return API.request('/profiles/me');
        },
        
        async update(profileData) {
            return API.request('/profiles/me', {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });
        }
    },
    
    // Preferences endpoints
    preferences: {
        async get() {
            return API.request('/preferences/');
        },
        
        async save(preferencesData) {
            return API.request('/preferences/', {
                method: 'POST',
                body: JSON.stringify(preferencesData)
            });
        },
        
        async estimate(preferencesData) {
            return API.request('/preferences/estimate', {
                method: 'POST',
                body: JSON.stringify(preferencesData)
            });
        }
    },
    
    // Matches endpoints
    matches: {},
    
    // Chat endpoints
    chats: {}
};

// Helper function to handle API errors globally
window.handleAPIError = function(error) {
    console.error('API Error:', error);
    
    // Handle common errors
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        // Token expired or invalid
        API.clearAuth();
        showView('auth');
        showNotification('Session expired. Please login again.', 'error');
    } else if (error.message.includes('Network')) {
        showNotification('Network error. Please check your connection.', 'error');
    } else {
        showNotification(error.message || 'An error occurred', 'error');
    }
};