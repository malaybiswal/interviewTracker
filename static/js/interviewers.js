// Get DOM elements
const searchInput = document.getElementById('searchInput');
const addInterviewerBtn = document.getElementById('addInterviewerBtn');
const importBtn = document.getElementById('importBtn');
const interviewersBody = document.getElementById('interviewersBody');
const emptyState = document.getElementById('emptyState');
const interviewersTable = document.getElementById('interviewersTable');
const addModal = document.getElementById('addModal');
const closeModal = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');
const addInterviewerForm = document.getElementById('addInterviewerForm');
const formMessage = document.getElementById('formMessage');
const logoutBtn = document.getElementById('logoutBtn');

let allInterviewers = [];

// Load interviewers on page load
document.addEventListener('DOMContentLoaded', () => {
    loadInterviewers();
});

// Search functionality
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    filterInterviewers(searchTerm);
});

// Add interviewer button
addInterviewerBtn.addEventListener('click', () => {
    addModal.style.display = 'block';
    formMessage.style.display = 'none';
    addInterviewerForm.reset();
});

// Import button
importBtn.addEventListener('click', async () => {
    if (!confirm('This will import all interviewer names from your existing interviews. Continue?')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        importBtn.disabled = true;
        importBtn.textContent = 'Importing...';
        
        const response = await fetch('/api/interviewers/import-from-interviews', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Import successful!\nImported: ${data.imported}\nSkipped (already exist): ${data.skipped}\nTotal: ${data.total}`);
            loadInterviewers();
        } else {
            alert(data.message || 'Failed to import interviewers');
        }
    } catch (error) {
        console.error('Error importing interviewers:', error);
        alert('An error occurred during import. Please try again.');
    } finally {
        importBtn.disabled = false;
        importBtn.textContent = 'Import from Interviews';
    }
});

// Close modal
closeModal.addEventListener('click', () => {
    addModal.style.display = 'none';
});

cancelBtn.addEventListener('click', () => {
    addModal.style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === addModal) {
        addModal.style.display = 'none';
    }
});

// Handle form submission
addInterviewerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('interviewerName').value.trim();
    const company = document.getElementById('interviewerCompany').value.trim();
    
    if (!name || !company) {
        showMessage('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/interviewers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, company })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Interviewer added successfully!', 'success');
            addInterviewerForm.reset();
            setTimeout(() => {
                addModal.style.display = 'none';
                loadInterviewers();
            }, 1500);
        } else {
            showMessage(data.message || 'Failed to add interviewer', 'error');
        }
    } catch (error) {
        console.error('Error adding interviewer:', error);
        showMessage('An error occurred. Please try again.', 'error');
    }
});

// Logout functionality
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login';
});

// Load interviewers from API
async function loadInterviewers() {
    try {
        // Include suggestions from existing interviews
        const response = await fetch('/api/interviewers?include_suggestions=true');
        
        if (response.ok) {
            allInterviewers = await response.json();
            displayInterviewers(allInterviewers);
        } else {
            console.error('Failed to load interviewers');
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading interviewers:', error);
        showEmptyState();
    }
}

// Display interviewers in table
function displayInterviewers(interviewers) {
    if (interviewers.length === 0) {
        showEmptyState();
        return;
    }
    
    interviewersTable.style.display = 'block';
    emptyState.style.display = 'none';
    
    interviewersBody.innerHTML = '';
    
    interviewers.forEach(interviewer => {
        const row = document.createElement('tr');
        row.onclick = () => {
            if (interviewer.in_database) {
                viewInterviewer(interviewer.id);
            } else {
                // Suggestion - prompt to add
                addSuggestion(interviewer.name, interviewer.company);
            }
        };
        
        const difficultyClass = getDifficultyClass(interviewer.average_difficulty);
        const isSuggestion = interviewer.suggestion || !interviewer.in_database;
        
        row.innerHTML = `
            <td>
                ${interviewer.name}
                ${isSuggestion ? '<span class="suggestion-badge">From Interviews</span>' : ''}
            </td>
            <td>${interviewer.company}</td>
            <td class="${difficultyClass}">
                ${interviewer.average_difficulty.toFixed(2)} / 5.0
                ${interviewer.total_reviews === 0 ? '(No ratings)' : ''}
            </td>
            <td>${interviewer.total_reviews}</td>
            <td>
                ${isSuggestion ? 
                    `<button class="btn-add" onclick="event.stopPropagation(); addSuggestion('${interviewer.name}', '${interviewer.company}')">Add to Database</button>` :
                    `<button class="btn-rate" onclick="event.stopPropagation(); viewInterviewer(${interviewer.id})">View/Rate</button>`
                }
            </td>
        `;
        
        if (isSuggestion) {
            row.classList.add('suggestion-row');
        }
        
        interviewersBody.appendChild(row);
    });
}

// Add a suggested interviewer to the database
async function addSuggestion(name, company) {
    if (!confirm(`Add ${name} from ${company} to the interviewer database?`)) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/interviewers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, company })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Interviewer added successfully!');
            loadInterviewers();
        } else {
            alert(data.message || 'Failed to add interviewer');
        }
    } catch (error) {
        console.error('Error adding interviewer:', error);
        alert('An error occurred. Please try again.');
    }
}

// Filter interviewers based on search term
function filterInterviewers(searchTerm) {
    const filtered = allInterviewers.filter(interviewer => 
        interviewer.name.toLowerCase().includes(searchTerm) ||
        interviewer.company.toLowerCase().includes(searchTerm)
    );
    displayInterviewers(filtered);
}

// Get difficulty class based on rating
function getDifficultyClass(rating) {
    if (rating >= 4.0) return 'difficulty-hard';
    if (rating >= 2.0) return 'difficulty-medium';
    return 'difficulty-easy';
}

// Navigate to interviewer detail page
function viewInterviewer(interviewerId) {
    window.location.href = `/interviewer-detail?id=${interviewerId}`;
}

// Show empty state
function showEmptyState() {
    interviewersTable.style.display = 'none';
    emptyState.style.display = 'block';
}

// Show form message
function showMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = `message ${type}`;
    formMessage.style.display = 'block';
}
