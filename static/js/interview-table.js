let allInterviews = [];
let allRounds = {};

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    loadAllData();
});

// Load all interviews and their rounds
async function loadAllData() {
    const token = localStorage.getItem('access_token');
    
    try {
        // Load all interviews
        const interviewsResponse = await fetch('/api/interviews', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (interviewsResponse.ok) {
            allInterviews = await interviewsResponse.json();
            
            // Load rounds for each interview
            for (const interview of allInterviews) {
                const roundsResponse = await fetch(`/api/interviews/${interview.id}/rounds`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (roundsResponse.ok) {
                    allRounds[interview.id] = await roundsResponse.json();
                } else {
                    allRounds[interview.id] = [];
                }
            }
            
            displayTable();
        } else if (interviewsResponse.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            window.location.href = '/login';
        } else {
            showEmptyState();
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
        showAlert('Failed to load interview data', 'error');
        showEmptyState();
    }
}

// Display the table
function displayTable() {
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('emptyState');
    const tableBody = document.getElementById('tableBody');
    
    loading.style.display = 'none';
    
    if (allInterviews.length === 0) {
        showEmptyState();
        return;
    }
    
    emptyState.style.display = 'none';
    tableBody.innerHTML = '';
    
    allInterviews.forEach(interview => {
        const row = createTableRow(interview);
        tableBody.appendChild(row);
    });
}

// Create table row for an interview
function createTableRow(interview) {
    const row = document.createElement('tr');
    
    // Determine row color based on dates
    const rowClass = getRowClass(interview);
    row.className = rowClass;
    
    // Get rounds for this interview
    const rounds = allRounds[interview.id] || [];
    
    // Company
    const companyCell = document.createElement('td');
    companyCell.className = 'company-cell';
    companyCell.textContent = interview.company_name;
    row.appendChild(companyCell);
    
    // Recruiter
    const recruiterCell = document.createElement('td');
    recruiterCell.className = 'recruiter-cell';
    recruiterCell.textContent = interview.recruiter_name || '-';
    row.appendChild(recruiterCell);
    
    // JD (Job Description Link)
    const jdCell = document.createElement('td');
    jdCell.className = 'jd-cell';
    if (interview.job_url) {
        const link = document.createElement('a');
        link.href = interview.job_url;
        link.target = '_blank';
        link.innerHTML = '<i class="fas fa-link"></i> Link';
        jdCell.appendChild(link);
    } else {
        jdCell.innerHTML = '<span class="empty-cell">-</span>';
    }
    row.appendChild(jdCell);
    
    // Extract interview rounds by type
    const phoneScreens = [];
    const onlineAssessments = [];
    const onsites = [];
    
    // Add initial interview if it exists
    if (interview.interview_date || interview.interview_type) {
        const initialRound = {
            date: interview.interview_date,
            type: interview.interview_type || interview.custom_interview_type
        };
        
        if (isPhoneScreen(initialRound.type)) {
            phoneScreens.push(initialRound);
        } else if (isOnlineAssessment(initialRound.type)) {
            onlineAssessments.push(initialRound);
        } else if (isOnsite(initialRound.type)) {
            onsites.push(initialRound);
        }
    }
    
    // Add rounds
    rounds.forEach(round => {
        const roundData = {
            date: round.interview_date,
            type: round.interview_type || round.custom_interview_type
        };
        
        if (isPhoneScreen(roundData.type)) {
            phoneScreens.push(roundData);
        } else if (isOnlineAssessment(roundData.type)) {
            onlineAssessments.push(roundData);
        } else if (isOnsite(roundData.type)) {
            onsites.push(roundData);
        }
    });
    
    // Phone Screen 1
    const phoneScreen1Cell = document.createElement('td');
    phoneScreen1Cell.className = 'date-cell';
    phoneScreen1Cell.innerHTML = phoneScreens[0] ? formatDate(phoneScreens[0].date) : '<span class="empty-cell">-</span>';
    row.appendChild(phoneScreen1Cell);
    
    // Online Assessment
    const onlineAssessmentCell = document.createElement('td');
    onlineAssessmentCell.className = 'date-cell';
    onlineAssessmentCell.innerHTML = onlineAssessments[0] ? formatDate(onlineAssessments[0].date) : '<span class="empty-cell">-</span>';
    row.appendChild(onlineAssessmentCell);
    
    // Phone Screen 2
    const phoneScreen2Cell = document.createElement('td');
    phoneScreen2Cell.className = 'date-cell';
    phoneScreen2Cell.innerHTML = phoneScreens[1] ? formatDate(phoneScreens[1].date) : '<span class="empty-cell">-</span>';
    row.appendChild(phoneScreen2Cell);
    
    // Onsite
    const onsiteCell = document.createElement('td');
    onsiteCell.className = 'date-cell';
    onsiteCell.innerHTML = onsites[0] ? formatDate(onsites[0].date) : '<span class="empty-cell">-</span>';
    row.appendChild(onsiteCell);
    
    // Notes
    const notesCell = document.createElement('td');
    notesCell.className = 'notes-cell';
    notesCell.textContent = interview.notes || '-';
    row.appendChild(notesCell);
    
    // Comments
    const commentCell = document.createElement('td');
    commentCell.className = 'comment-cell';
    commentCell.textContent = interview.comments || '-';
    row.appendChild(commentCell);
    
    return row;
}

// Determine row class based on interview dates
function getRowClass(interview) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const rounds = allRounds[interview.id] || [];
    const allDates = [];
    
    // Collect all dates
    if (interview.interview_date) {
        allDates.push(new Date(interview.interview_date));
    }
    
    rounds.forEach(round => {
        if (round.interview_date) {
            allDates.push(new Date(round.interview_date));
        }
    });
    
    if (allDates.length === 0) {
        return 'row-upcoming';
    }
    
    // Check if any date is today
    const hasToday = allDates.some(date => {
        const d = new Date(date);
        d.setHours(0, 0, 0, 0);
        return d.getTime() === today.getTime();
    });
    
    if (hasToday) {
        return 'row-today';
    }
    
    // Check if all dates are in the past and status is completed
    const latestDate = new Date(Math.max(...allDates));
    latestDate.setHours(0, 0, 0, 0);
    
    const status = (interview.status || '').toLowerCase();
    if (latestDate < today && (status.includes('completed') || status.includes('done'))) {
        return 'row-completed';
    }
    
    return 'row-upcoming';
}

// Helper functions to categorize interview types
function isPhoneScreen(type) {
    if (!type) return false;
    const t = type.toLowerCase();
    return t.includes('phone') || t.includes('recruiter') || t === 'hiring-mgr-phone-screen';
}

function isOnlineAssessment(type) {
    if (!type) return false;
    const t = type.toLowerCase();
    return t.includes('online') || t.includes('assessment') || t.includes('hacker') || t.includes('coding') && !t.includes('onsite');
}

function isOnsite(type) {
    if (!type) return false;
    const t = type.toLowerCase();
    return t.includes('onsite');
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '<span class="empty-cell">-</span>';
    
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const year = date.getFullYear().toString().slice(-2);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    
    let formatted = `${month}/${day}/${year}`;
    
    // Add time if it's not midnight
    if (hours !== 0 || minutes !== 0) {
        const timeStr = date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
        formatted += ` ${timeStr}`;
    }
    
    return formatted;
}

// Show empty state
function showEmptyState() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('emptyState').style.display = 'block';
    document.querySelector('.interview-table').style.display = 'none';
}

// Navigation functions
function goBack() {
    window.location.href = '/dashboard';
}

function addNewInterview() {
    window.location.href = '/interview-details';
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    window.location.href = '/login';
}

// Show alert message
function showAlert(message, type) {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert ${type} show`;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}
