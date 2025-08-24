// DOM Elements
const resultsContainer = document.getElementById('resultsContainer');
const resultsGrid = document.getElementById('resultsGrid');
const resultsInfo = document.getElementById('resultsInfo');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Form Submissions
document.getElementById('nameSearchForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const applicant = document.getElementById('applicantName').value;
    const status = document.getElementById('nameStatus').value;
    
    searchFoodTrucks({
        query_type: 'name',
        applicant: applicant,
        status: status || undefined
    });
});

document.getElementById('streetSearchForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const street = document.getElementById('streetName').value;
    const status = document.getElementById('streetStatus').value;
    
    searchFoodTrucks({
        query_type: 'street',
        street: street,
        status: status || undefined
    });
});

document.getElementById('proximitySearchForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    const status = document.getElementById('proximityStatus').value;
    
    searchFoodTrucks({
        query_type: 'proximity',
        latitude: latitude,
        longitude: longitude,
        status: status || undefined
    });
});

// Main Search Function
async function searchFoodTrucks(searchParams) {
    try {
        showLoading();
        clearResults();
        hideError();
        
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchParams)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Search failed');
        }
        
        if (data.success) {
            displayResults(data);
        } else {
            throw new Error(data.message || 'Search failed');
        }
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(data) {
    console.log('Displaying results with data:', data);
    console.log('Data.data:', data.data);
    console.log('First truck:', data.data[0]);
    
    resultsInfo.innerHTML = `
        <span>Found ${data.metadata.total_results} results</span>
        <span>•</span>
        <span>${data.metadata.query_type} search</span>
        ${data.metadata.status_filter ? `<span>•</span><span>Status: ${data.metadata.status_filter}</span>` : ''}
    `;
    
    if (data.data.length === 0) {
        resultsGrid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">No food trucks found matching your criteria.</p>';
    } else {
        resultsGrid.innerHTML = data.data.map(truck => createTruckCard(truck)).join('');
    }
    
    resultsContainer.style.display = 'block';
}

// Create Truck Card
function createTruckCard(truck) {
    console.log('Creating card for truck:', truck);
    console.log('Truck Status:', truck.Status);
    console.log('Truck Status type:', typeof truck.Status);
    
    // Extra safety check for Status field
    let statusClass = 'unknown';
    if (truck && truck.Status && typeof truck.Status === 'string') {
        statusClass = truck.Status.toLowerCase();
    }
    
    console.log('Status class:', statusClass);
    
    return `
        <div class="food-truck-card">
            <h3>${escapeHtml(truck.Applicant || 'N/A')}</h3>
            <div class="food-truck-info">
                <strong>Type:</strong> ${escapeHtml(truck.FacilityType || 'N/A')}
            </div>
            <div class="food-truck-info">
                <strong>Address:</strong> ${escapeHtml(truck.Address || 'N/A')}
            </div>
            <div class="food-truck-info">
                <strong>Status:</strong> <span class="status ${statusClass}">${truck.Status || 'N/A'}</span>
            </div>
            <div class="food-truck-info">
                <strong>Food Items:</strong> ${escapeHtml(truck.FoodItems || 'N/A')}
            </div>
            <div class="food-truck-info">
                <strong>Location:</strong> ${truck.Latitude && truck.Longitude ? `${truck.Latitude.toFixed(6)}, ${truck.Longitude.toFixed(6)}` : 'N/A'}
            </div>
            ${truck.LocationDescription ? `<div class="food-truck-info"><strong>Description:</strong> ${escapeHtml(truck.LocationDescription)}</div>` : ''}
            ${truck.Schedule ? `<div class="food-truck-info"><strong>Schedule:</strong> <a href="${truck.Schedule}" target="_blank">View Schedule</a></div>` : ''}
        </div>
    `;
}

// Utility Functions
function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function clearResults() {
    resultsContainer.style.display = 'none';
    resultsGrid.innerHTML = '';
    resultsInfo.innerHTML = '';
}

function escapeHtml(text) {
    if (text === null || text === undefined) return 'N/A';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Location Functions
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById('latitude').value = position.coords.latitude.toFixed(6);
                document.getElementById('longitude').value = position.coords.longitude.toFixed(6);
            },
            (error) => {
                showError('Unable to get your location: ' + error.message);
            }
        );
    } else {
        showError('Geolocation is not supported by this browser.');
    }
}

function showRandomLocation() {
    const sfLocations = [
        { lat: 37.7749, lng: -122.4194, name: 'Downtown SF' },
        { lat: 37.7849, lng: -122.4094, name: 'Financial District' },
        { lat: 37.7649, lng: -122.4294, name: 'Mission District' },
        { lat: 37.7949, lng: -122.3994, name: 'North Beach' },
        { lat: 37.7549, lng: -122.4394, name: 'Potrero Hill' }
    ];
    
    const randomLocation = sfLocations[Math.floor(Math.random() * sfLocations.length)];
    
    document.getElementById('latitude').value = randomLocation.lat;
    document.getElementById('longitude').value = randomLocation.lng;
    
    // Show notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = `Using ${randomLocation.name} coordinates`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('SF Food Truck Finder loaded successfully!');
});


