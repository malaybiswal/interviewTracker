// Get URL parameter
const urlParams = new URLSearchParams(window.location.search);
const interviewerId = urlParams.get('id');

// Get DOM elements
const interviewerName = document.getElementById('interviewerName');
const interviewerCompany = document.getElementById('interviewerCompany');
const avgDifficulty = document.getElementById('avgDifficulty');
const totalReviews = document.getElementById('totalReviews');
const ratingSection = document.getElementById('ratingSection');
const alreadyRatedSection = document.getElementById('alreadyRatedSection');
const ratingForm = document.getElementById('ratingForm');
const ratingMessage = document.getElementById('ratingMessage');
const ratingsContainer = document.getElementById('ratingsContainer');
const noRatings = document.getElementById('noRatings');
const logoutBtn = document.getElementById('logoutBtn');
const ratingInputs = document.querySelectorAll('input[name="rating"]');
const ratingValue = document.getElementById('ratingValue');

// Load interviewer details on page load
document.addEventListener('DOMContentLoaded', () => {
    if (!interviewerId) {
        window.location.href = '/interviewers';
        return;
    }
    
    loadInterviewerDetails();
    checkUserRating();
});

// Update rating value display
ratingInputs.forEach(input => {
    input.addEventListener('change', (e) => {
        const value = e.target.value;
        const labels = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard'];
        ratingValue.textContent = `${value} - ${labels[value - 1]}`;
    });
});

// Handle rating form submission
ratingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const rating = document.querySelector('input[name="rating"]:checked')?.value;
    const comments = document.getElementById('comments').value.trim();
    
    if (!rating) {
        showMessage('Please select a rating', 'error');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/interviewers/${interviewerId}/ratings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                rating: parseInt(rating),
                comments: comments || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Rating submitted successfully!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMessage(data.message || 'Failed to submit rating', 'error');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
        showMessage('An error occurred. Please try again.', 'error');
    }
});

// Logout functionality
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login';
});

// Load interviewer details
async function loadInterviewerDetails() {
    try {
        const response = await fetch(`/api/interviewers/${interviewerId}`);
        
        if (response.ok) {
            const interviewer = await response.json();
            displayInterviewerDetails(interviewer);
            displayRatings(interviewer.ratings);
        } else {
            console.error('Failed to load interviewer details');
            window.location.href = '/interviewers';
        }
    } catch (error) {
        console.error('Error loading interviewer details:', error);
        window.location.href = '/interviewers';
    }
}

// Check if user has already rated
async function checkUserRating() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            // User not logged in, show rating form anyway
            return;
        }
        
        const response = await fetch(`/api/interviewers/${interviewerId}/user-rating`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            // User has already rated
            ratingSection.style.display = 'none';
            alreadyRatedSection.style.display = 'block';
        } else {
            // User hasn't rated yet
            ratingSection.style.display = 'block';
            alreadyRatedSection.style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking user rating:', error);
        // Show rating form by default on error
        ratingSection.style.display = 'block';
    }
}

// Display interviewer details
function displayInterviewerDetails(interviewer) {
    interviewerName.textContent = interviewer.name;
    interviewerCompany.textContent = interviewer.company;
    
    const difficultyClass = getDifficultyClass(interviewer.average_difficulty);
    avgDifficulty.textContent = interviewer.average_difficulty.toFixed(2) + ' / 5.0';
    avgDifficulty.className = `stat-value ${difficultyClass}`;
    
    totalReviews.textContent = interviewer.total_reviews;
}

// Display ratings
function displayRatings(ratings) {
    if (!ratings || ratings.length === 0) {
        ratingsContainer.style.display = 'none';
        noRatings.style.display = 'block';
        return;
    }
    
    ratingsContainer.style.display = 'block';
    noRatings.style.display = 'none';
    ratingsContainer.innerHTML = '';
    
    ratings.forEach(rating => {
        const card = document.createElement('div');
        card.className = 'rating-card';
        
        const stars = '★'.repeat(rating.rating) + '☆'.repeat(5 - rating.rating);
        const date = new Date(rating.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        card.innerHTML = `
            <div class="rating-header">
                <div class="rating-stars">${stars}</div>
                <div class="rating-meta">by ${rating.username} on ${date}</div>
            </div>
            ${rating.comments ? `<div class="rating-comments">${rating.comments}</div>` : ''}
        `;
        
        ratingsContainer.appendChild(card);
    });
}

// Get difficulty class
function getDifficultyClass(rating) {
    if (rating >= 4.0) return 'difficulty-hard';
    if (rating >= 2.0) return 'difficulty-medium';
    return 'difficulty-easy';
}

// Show message
function showMessage(message, type) {
    ratingMessage.textContent = message;
    ratingMessage.className = `message ${type}`;
    ratingMessage.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            ratingMessage.style.display = 'none';
        }, 3000);
    }
}
