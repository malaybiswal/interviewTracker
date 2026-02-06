let currentInterview = null;
let currentRounds = [];

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Get interview ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const interviewId = urlParams.get('id');
    
    if (!interviewId) {
        showAlert('No interview ID provided', 'error');
        setTimeout(() => window.location.href = '/dashboard', 2000);
        return;
    }

    loadInterviewData(interviewId);
});

// Load interview data and rounds
async function loadInterviewData(interviewId) {
    const token = localStorage.getItem('access_token');
    
    try {
        // Load interview details
        const interviewResponse = await fetch(`/api/interviews/${interviewId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (interviewResponse.ok) {
            currentInterview = await interviewResponse.json();
            displayInterviewOverview();
        } else {
            throw new Error('Failed to load interview');
        }

        // Load interview rounds
        const roundsResponse = await fetch(`/api/interviews/${interviewId}/rounds`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (roundsResponse.ok) {
            currentRounds = await roundsResponse.json();
            displayRounds();
        } else {
            // No rounds yet, show empty state
            currentRounds = [];
            displayRounds();
        }

    } catch (error) {
        console.error('Error loading data:', error);
        showAlert('Failed to load interview data', 'error');
    }
}

// Display interview overview
function displayInterviewOverview() {
    document.getElementById('companyJobTitle').textContent = 
        `${currentInterview.company_name} - ${currentInterview.job_title}`;
    
    document.getElementById('recruiterName').textContent = 
        currentInterview.recruiter_name || 'Not specified';
    
    const jobUrlElement = document.getElementById('jobUrl');
    if (currentInterview.job_url) {
        jobUrlElement.href = currentInterview.job_url;
        jobUrlElement.style.display = 'inline';
    } else {
        jobUrlElement.parentElement.style.display = 'none';
    }
    
    const statusElement = document.getElementById('overallStatus');
    statusElement.textContent = currentInterview.status || 'Applied';
    statusElement.className = `status-badge status-${(currentInterview.status || 'applied').toLowerCase().replace(' ', '-')}`;
    
    // Display initial interview details if they exist
    displayInitialInterviewDetails();
}

// Display initial interview details
function displayInitialInterviewDetails() {
    const hasInitialData = currentInterview.interview_date || 
                          currentInterview.interviewer_name || 
                          currentInterview.interview_type || 
                          currentInterview.comments || 
                          currentInterview.notes;
    
    if (!hasInitialData) {
        document.getElementById('initialInterviewSection').style.display = 'none';
        return;
    }
    
    document.getElementById('initialInterviewSection').style.display = 'block';
    
    // Interview Date & Time
    const dateElement = document.getElementById('initialDate');
    if (currentInterview.interview_date && currentInterview.interview_time) {
        const dateStr = `${currentInterview.interview_date}T${currentInterview.interview_time}`;
        const date = new Date(dateStr);
        dateElement.textContent = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } else if (currentInterview.interview_date) {
        const date = new Date(currentInterview.interview_date);
        dateElement.textContent = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } else {
        dateElement.textContent = 'Not scheduled';
    }
    
    // Interviewer
    document.getElementById('initialInterviewer').textContent = 
        currentInterview.interviewer_name || 'Not specified';
    
    // Interview Type
    const typeText = currentInterview.custom_interview_type || 
                    currentInterview.interview_type || 
                    'Not specified';
    document.getElementById('initialType').textContent = typeText;
    
    // Status (use the same as overall status for now)
    const initialStatusElement = document.getElementById('initialStatus');
    const status = currentInterview.status || 'Applied';
    initialStatusElement.textContent = status;
    initialStatusElement.className = `status-badge status-${status.toLowerCase().replace(' ', '-')}`;
    
    // Comments and Notes
    const hasCommentsOrNotes = currentInterview.comments || currentInterview.notes;
    const commentsNotesSection = document.getElementById('commentsNotesSection');
    
    if (hasCommentsOrNotes) {
        commentsNotesSection.style.display = 'block';
        
        // Comments
        if (currentInterview.comments && currentInterview.comments.trim()) {
            document.getElementById('initialCommentsGroup').style.display = 'block';
            document.getElementById('initialComments').textContent = currentInterview.comments;
        } else {
            document.getElementById('initialCommentsGroup').style.display = 'none';
        }
        
        // Notes
        if (currentInterview.notes && currentInterview.notes.trim()) {
            document.getElementById('initialNotesGroup').style.display = 'block';
            document.getElementById('initialNotes').textContent = currentInterview.notes;
        } else {
            document.getElementById('initialNotesGroup').style.display = 'none';
        }
    } else {
        commentsNotesSection.style.display = 'none';
    }
}

// Display rounds
function displayRounds() {
    const roundsList = document.getElementById('roundsList');
    const emptyRounds = document.getElementById('emptyRounds');
    
    if (currentRounds.length === 0) {
        roundsList.style.display = 'none';
        emptyRounds.style.display = 'block';
        return;
    }
    
    roundsList.style.display = 'block';
    emptyRounds.style.display = 'none';
    
    roundsList.innerHTML = '';
    
    currentRounds.forEach(round => {
        const roundCard = createRoundCard(round);
        roundsList.appendChild(roundCard);
    });
}

// Create round card
function createRoundCard(round) {
    const card = document.createElement('div');
    card.className = 'round-card';
    
    const statusClass = `status-${(round.status || 'scheduled').toLowerCase().replace(' ', '-')}`;
    const roundDate = round.interview_date ? 
        new Date(round.interview_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'Not scheduled';
    
    const interviewType = round.custom_interview_type || round.interview_type || 'Not specified';
    
    // Format interview type for display
    const formattedType = formatInterviewType(interviewType);
    
    card.innerHTML = `
        <div class="round-header">
            <div class="round-title">
                <i class="fas fa-circle"></i>
                Round ${round.round_number} - ${formattedType}
            </div>
            <div class="status-badge ${statusClass}">${round.status}</div>
        </div>
        <div class="round-details">
            <div class="round-detail-item">
                <i class="fas fa-calendar"></i>
                <span><strong>Date:</strong> ${roundDate}</span>
            </div>
            <div class="round-detail-item">
                <i class="fas fa-user"></i>
                <span><strong>Interviewer:</strong> ${round.interviewer_name || 'Not specified'}</span>
            </div>
            <div class="round-detail-item">
                <i class="fas fa-clock"></i>
                <span><strong>Added:</strong> ${new Date(round.created_at).toLocaleDateString()}</span>
            </div>
        </div>
        ${round.comments || round.notes ? `
            <div class="round-comments">
                ${round.comments ? `
                    <div class="comment-section">
                        <h4><i class="fas fa-comment"></i> Comments</h4>
                        <div class="comment-text">${round.comments}</div>
                    </div>
                ` : ''}
                ${round.notes ? `
                    <div class="notes-section">
                        <h4><i class="fas fa-sticky-note"></i> Notes</h4>
                        <div class="notes-text">${round.notes}</div>
                    </div>
                ` : ''}
            </div>
        ` : ''}
    `;
    
    return card;
}

// Format interview type for display
function formatInterviewType(type) {
    if (!type || type === 'Not specified') return 'Not specified';
    
    // Convert kebab-case to Title Case
    return type
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Show add rounds modal
function showAddRoundsModal() {
    document.getElementById('addRoundsModal').classList.add('show');
    generateRoundForms();
}

// Close add rounds modal
function closeAddRoundsModal() {
    document.getElementById('addRoundsModal').classList.remove('show');
    document.getElementById('roundCount').value = 1;
    document.getElementById('roundForms').innerHTML = '';
}

// Generate round forms based on count
function generateRoundForms() {
    const count = parseInt(document.getElementById('roundCount').value) || 1;
    const container = document.getElementById('roundForms');
    
    container.innerHTML = '';
    
    for (let i = 1; i <= count; i++) {
        // Start from round 2 since round 1 is the initial interview
        const roundNumber = currentRounds.length + i + 1;
        const form = createRoundForm(roundNumber);
        container.appendChild(form);
    }
}

// Create individual round form
function createRoundForm(roundNumber) {
    const form = document.createElement('div');
    form.className = 'round-form';
    
    form.innerHTML = `
        <h4><i class="fas fa-circle"></i> Round ${roundNumber}</h4>
        
        <div class="form-row">
            <div class="form-group">
                <label>Interview Type</label>
                <div class="input-wrapper">
                    <i class="fas fa-video"></i>
                    <select class="interview-type" onchange="handleRoundTypeChange(this, ${roundNumber})">
                        <option value="">Select interview type</option>
                        <option value="recruiter">Recruiter</option>
                        <option value="coding-phone-screen">Coding Phone Screen</option>
                        <option value="systems-phone-screen">Systems Phone Screen</option>
                        <option value="hiring-mgr-phone-screen">Hiring Mgr Phone Screen</option>
                        <option value="onsite-coding">Onsite Coding</option>
                        <option value="onsite-behavioral">Onsite Behavioral</option>
                        <option value="onsite-x-functional">Onsite X-Functional</option>
                        <option value="onsite-system-design">Onsite System Design</option>
                        <option value="onsite-systems">Onsite Systems</option>
                        <option value="onsite-recruiter-debrief">Onsite Recruiter Debrief</option>
                        <option value="others">Others</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>Status</label>
                <div class="input-wrapper">
                    <i class="fas fa-flag"></i>
                    <select class="status">
                        <option value="Scheduled">Scheduled</option>
                        <option value="Completed">Completed</option>
                        <option value="Failed">Failed</option>
                        <option value="Cancelled">Cancelled</option>
                        <option value="No Show">No Show</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="form-group custom-type-group" id="customType${roundNumber}" style="display: none;">
            <label>Custom Interview Type</label>
            <div class="input-wrapper">
                <i class="fas fa-edit"></i>
                <input type="text" class="custom-interview-type" placeholder="Enter custom interview type">
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label>Interview Date</label>
                <div class="input-wrapper">
                    <i class="fas fa-calendar"></i>
                    <input type="date" class="interview-date">
                </div>
            </div>
            
            <div class="form-group">
                <label>Interview Time</label>
                <div class="input-wrapper">
                    <i class="fas fa-clock"></i>
                    <input type="time" class="interview-time">
                </div>
            </div>
        </div>
        
        <div class="form-group">
            <label>Interviewer Name</label>
            <div class="input-wrapper">
                <i class="fas fa-user"></i>
                <input type="text" class="interviewer-name" placeholder="Enter interviewer name">
            </div>
        </div>
        
        <div class="form-group">
            <label>Comments</label>
            <div class="input-wrapper">
                <i class="fas fa-comment"></i>
                <textarea class="comments" placeholder="Comments about this round..."></textarea>
            </div>
        </div>
        
        <div class="form-group">
            <label>Notes</label>
            <div class="input-wrapper">
                <i class="fas fa-sticky-note"></i>
                <textarea class="notes" placeholder="Personal notes for this round..."></textarea>
            </div>
        </div>
    `;
    
    return form;
}

// Handle round type change
function handleRoundTypeChange(select, roundNumber) {
    const customTypeGroup = document.getElementById(`customType${roundNumber}`);
    const customTypeInput = customTypeGroup.querySelector('.custom-interview-type');
    
    if (select.value === 'others') {
        customTypeGroup.style.display = 'block';
        customTypeInput.required = true;
    } else {
        customTypeGroup.style.display = 'none';
        customTypeInput.required = false;
        customTypeInput.value = '';
    }
}

// Save rounds
async function saveRounds() {
    const token = localStorage.getItem('access_token');
    const saveBtn = document.querySelector('.save-btn');
    const spinner = document.getElementById('saveSpinner');
    const btnText = document.querySelector('.btn-text');
    
    // Show loading state
    saveBtn.disabled = true;
    spinner.style.display = 'block';
    btnText.textContent = 'Saving...';
    
    try {
        const roundForms = document.querySelectorAll('.round-form');
        const rounds = [];
        
        roundForms.forEach((form, index) => {
            // Start from round 2 since round 1 is the initial interview
            const roundNumber = currentRounds.length + index + 2;
            
            const interviewType = form.querySelector('.interview-type').value;
            const customType = form.querySelector('.custom-interview-type').value;
            const date = form.querySelector('.interview-date').value;
            const time = form.querySelector('.interview-time').value;
            
            let interviewDate = null;
            if (date && time) {
                interviewDate = `${date}T${time}`;
            }
            
            rounds.push({
                round_number: roundNumber,
                interview_type: interviewType,
                custom_interview_type: interviewType === 'others' ? customType : null,
                interview_date: interviewDate,
                interviewer_name: form.querySelector('.interviewer-name').value,
                status: form.querySelector('.status').value,
                comments: form.querySelector('.comments').value,
                notes: form.querySelector('.notes').value
            });
        });
        
        const response = await fetch(`/api/interviews/${currentInterview.id}/rounds`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rounds })
        });
        
        if (response.ok) {
            showAlert('Rounds added successfully!', 'success');
            closeAddRoundsModal();
            loadInterviewData(currentInterview.id); // Reload data
        } else {
            const error = await response.json();
            showAlert(error.message || 'Failed to save rounds', 'error');
        }
        
    } catch (error) {
        console.error('Error saving rounds:', error);
        showAlert('Network error. Please try again.', 'error');
    } finally {
        // Reset loading state
        saveBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Save Rounds';
    }
}

// Go back to dashboard
function goBack() {
    window.location.href = '/dashboard';
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