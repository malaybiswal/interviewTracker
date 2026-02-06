let currentInterviews = [];

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Set username from localStorage
    const username = localStorage.getItem('username') || 'User';
    document.getElementById('username').textContent = username;

    // Load dashboard data
    loadDashboardData();
});

// Load dashboard data
async function loadDashboardData() {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch('/api/interviews', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const interviews = await response.json();
            currentInterviews = interviews; // Store globally
            displayInterviews(interviews);
            updateStats(interviews);
        } else if (response.status === 401) {
            // Token expired, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            window.location.href = '/login';
        } else {
            // For now, show empty state if API fails
            displayInterviews([]);
            updateStats([]);
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show empty state on error
        displayInterviews([]);
        updateStats([]);
    }
}

// Display interviews
function displayInterviews(interviews) {
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('emptyState');
    const interviewsList = document.getElementById('interviewsList');
    
    loading.style.display = 'none';
    
    if (interviews.length === 0) {
        emptyState.style.display = 'block';
        interviewsList.style.display = 'none';
    } else {
        emptyState.style.display = 'none';
        interviewsList.style.display = 'block';
        
        const upcomingList = document.getElementById('upcomingList');
        const pastList = document.getElementById('pastList');
        
        // Clear existing content
        upcomingList.innerHTML = '';
        pastList.innerHTML = '';
        
        interviews.forEach(interview => {
            const card = createInterviewCard(interview);
            
            // Categorize based on status
            // Active: Applied, Interviewing, On Hold
            // Completed: Awaiting Decision, Offer Received, Rejected, Withdrawn
            const activeStatuses = ['Applied', 'Interviewing', 'On Hold'];
            const status = interview.status || 'Applied';
            
            if (activeStatuses.includes(status)) {
                upcomingList.appendChild(card);
            } else {
                pastList.appendChild(card);
            }
        });
        
        // Hide categories if empty
        const upcomingCategory = upcomingList.parentElement;
        const pastCategory = pastList.parentElement;
        
        upcomingCategory.style.display = upcomingList.children.length > 0 ? 'block' : 'none';
        pastCategory.style.display = pastList.children.length > 0 ? 'block' : 'none';
    }
}

// Create interview card
function createInterviewCard(interview) {
    const card = document.createElement('div');
    card.className = 'interview-card';
    card.onclick = () => viewInterviewDetails(interview.id);
    
    const statusClass = `status-${(interview.status || 'applied').toLowerCase().replace(' ', '-')}`;
    const interviewDate = interview.interview_date ? new Date(interview.interview_date).toLocaleDateString() : 'Not scheduled';
    
    card.innerHTML = `
        <div class="interview-header">
            <div>
                <div class="company-name">${interview.company_name}</div>
                <div class="job-title">${interview.job_title}</div>
            </div>
            <div class="status-badge ${statusClass}">${interview.status || 'Applied'}</div>
        </div>
        <div class="interview-details">
            <div class="detail-item">
                <i class="fas fa-calendar"></i>
                <span class="interview-date">${interviewDate}</span>
            </div>
            ${interview.recruiter_name ? `
                <div class="detail-item">
                    <i class="fas fa-user"></i>
                    <span>${interview.recruiter_name}</span>
                </div>
            ` : ''}
            ${interview.job_url ? `
                <div class="detail-item">
                    <i class="fas fa-link"></i>
                    <span>Job Posting</span>
                </div>
            ` : ''}
            ${interview.comments ? `
                <div class="detail-item">
                    <i class="fas fa-comment"></i>
                    <span>${interview.comments.substring(0, 50)}${interview.comments.length > 50 ? '...' : ''}</span>
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// Update stats
function updateStats(interviews) {
    const total = interviews.length;
    
    // Upcoming: Applied, Interviewing, On Hold
    const upcoming = interviews.filter(i => 
        ['Applied', 'Interviewing', 'On Hold'].includes(i.status || 'Applied')
    ).length;
    
    // Completed: Awaiting Decision, Offer Received, Rejected, Withdrawn
    const completed = interviews.filter(i => 
        ['Awaiting Decision', 'Offer Received', 'Rejected', 'Withdrawn'].includes(i.status || '')
    ).length;
    
    const pending = upcoming; // Pending is same as upcoming (active interviews)
    
    document.getElementById('totalInterviews').textContent = total;
    document.getElementById('upcomingInterviews').textContent = upcoming;
    document.getElementById('completedInterviews').textContent = completed;
    document.getElementById('pendingInterviews').textContent = pending;
}

// Add new interview
function addNewInterview() {
    window.location.href = '/interview-details';
}

// View table view
function viewTableView() {
    window.location.href = '/interview-table';
}

// View interviewers
function viewInterviewers() {
    window.location.href = '/interviewers';
}

// View interview details
function viewInterviewDetails(interviewId) {
    // Always go to rounds page for managing interview rounds
    // Users can still edit basic details from the rounds page or details page
    window.location.href = `/interview-rounds?id=${interviewId}`;
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    window.location.href = '/login';
}

// Show error message
function showError(message) {
    // You can implement a toast notification here
    alert(message);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}