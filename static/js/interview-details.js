document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Check if editing existing interview
    const urlParams = new URLSearchParams(window.location.search);
    const interviewId = urlParams.get('id');
    
    if (interviewId) {
        loadInterviewData(interviewId);
        updateFormTitle('Edit Interview', 'Update the details for this interview');
    }

    // Set up form submission
    document.getElementById('interviewForm').addEventListener('submit', handleFormSubmit);
});

// Handle interview type change (show/hide custom type field)
function handleInterviewTypeChange() {
    const interviewType = document.getElementById('interviewType').value;
    const customTypeGroup = document.getElementById('customTypeGroup');
    const customTypeInput = document.getElementById('customInterviewType');
    
    if (interviewType === 'others') {
        customTypeGroup.style.display = 'block';
        customTypeInput.required = true;
    } else {
        customTypeGroup.style.display = 'none';
        customTypeInput.required = false;
        customTypeInput.value = ''; // Clear the custom input
    }
}

// Load existing interview data for editing
async function loadInterviewData(interviewId) {
    const token = localStorage.getItem('access_token');
    
    try {
        showAlert('Loading interview data...', 'success');
        
        const response = await fetch(`/api/interviews/${interviewId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const interview = await response.json();
            populateForm(interview);
            
            // Show the "Manage Rounds" button when editing
            document.getElementById('manageRoundsBtn').style.display = 'flex';
        } else if (response.status === 401) {
            // Token expired, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            window.location.href = '/login';
        } else {
            showAlert('Failed to load interview data', 'error');
        }
        
    } catch (error) {
        console.error('Error loading interview data:', error);
        showAlert('Failed to load interview data', 'error');
    }
}

// Populate form with existing data
function populateForm(data) {
    document.getElementById('companyName').value = data.company_name || '';
    document.getElementById('jobTitle').value = data.job_title || '';
    document.getElementById('recruiterName').value = data.recruiter_name || '';
    document.getElementById('interviewerName').value = data.interviewer_name || '';
    document.getElementById('jobUrl').value = data.job_url || '';
    document.getElementById('interviewDate').value = data.interview_date || '';
    document.getElementById('interviewTime').value = data.interview_time || '';
    document.getElementById('status').value = data.status || 'Applied';
    document.getElementById('comments').value = data.comments || '';
    document.getElementById('notes').value = data.notes || '';
    
    // Handle interview type and custom type
    const interviewType = data.interview_type || '';
    const customType = data.custom_interview_type || '';
    
    if (customType && interviewType === 'others') {
        document.getElementById('interviewType').value = 'others';
        document.getElementById('customInterviewType').value = customType;
        handleInterviewTypeChange(); // Show the custom field
    } else {
        document.getElementById('interviewType').value = interviewType;
    }
}

// Update form title
function updateFormTitle(title, subtitle) {
    document.getElementById('formTitle').textContent = title;
    document.getElementById('formSubtitle').textContent = subtitle;
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }

    const saveBtn = document.getElementById('saveBtn');
    const spinner = document.getElementById('spinner');
    const btnText = document.querySelector('.btn-text');
    
    // Show loading state
    saveBtn.disabled = true;
    spinner.style.display = 'block';
    btnText.style.display = 'none';

    const formData = collectFormData();
    const token = localStorage.getItem('access_token');
    
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const interviewId = urlParams.get('id');
        
        // Determine if creating or updating
        const method = interviewId ? 'PUT' : 'POST';
        const url = interviewId ? `/api/interviews/${interviewId}` : '/api/interview';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            const action = interviewId ? 'updated' : 'created';
            showAlert(`Interview ${action} successfully!`, 'success');
            
            // Redirect to dashboard after a short delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showAlert(data.message || `Failed to ${interviewId ? 'update' : 'create'} interview`, 'error');
        }
    } catch (error) {
        console.error('Error saving interview:', error);
        showAlert('Network error. Please check your connection and try again.', 'error');
    } finally {
        // Reset loading state
        saveBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.style.display = 'flex';
    }
}

// Collect form data
function collectFormData() {
    const interviewType = document.getElementById('interviewType').value;
    const customType = document.getElementById('customInterviewType').value.trim();
    
    const formData = {
        company_name: document.getElementById('companyName').value.trim(),
        job_title: document.getElementById('jobTitle').value.trim(),
        recruiter_name: document.getElementById('recruiterName').value.trim(),
        interviewer_name: document.getElementById('interviewerName').value.trim(),
        job_url: document.getElementById('jobUrl').value.trim(),
        interview_date: document.getElementById('interviewDate').value,
        interview_time: document.getElementById('interviewTime').value,
        interview_type: interviewType,
        custom_interview_type: interviewType === 'others' ? customType : null,
        status: document.getElementById('status').value,
        comments: document.getElementById('comments').value.trim(),
        notes: document.getElementById('notes').value.trim()
    };
    
    // Combine date and time if both are provided
    if (formData.interview_date && formData.interview_time) {
        formData.interview_datetime = `${formData.interview_date}T${formData.interview_time}`;
    }
    
    return formData;
}

// Validate form
function validateForm() {
    const companyName = document.getElementById('companyName').value.trim();
    const jobTitle = document.getElementById('jobTitle').value.trim();
    const interviewType = document.getElementById('interviewType').value;
    const customType = document.getElementById('customInterviewType').value.trim();
    
    if (!companyName) {
        showAlert('Please enter a company name', 'error');
        document.getElementById('companyName').focus();
        return false;
    }
    
    if (!jobTitle) {
        showAlert('Please enter a job title', 'error');
        document.getElementById('jobTitle').focus();
        return false;
    }
    
    // Validate custom interview type if "Others" is selected
    if (interviewType === 'others' && !customType) {
        showAlert('Please enter a custom interview type', 'error');
        document.getElementById('customInterviewType').focus();
        return false;
    }
    
    // Validate URL if provided
    const jobUrl = document.getElementById('jobUrl').value.trim();
    if (jobUrl && !isValidUrl(jobUrl)) {
        showAlert('Please enter a valid URL for the job description', 'error');
        document.getElementById('jobUrl').focus();
        return false;
    }
    
    return true;
}

// Validate URL
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Go back to dashboard
function goBack() {
    window.location.href = '/dashboard';
}

// Go to rounds page
function goToRounds() {
    const urlParams = new URLSearchParams(window.location.search);
    const interviewId = urlParams.get('id');
    
    if (interviewId) {
        window.location.href = `/interview-rounds?id=${interviewId}`;
    }
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

// Real-time validation
document.addEventListener('DOMContentLoaded', function() {
    // Add real-time validation for required fields
    const requiredFields = ['companyName', 'jobTitle'];
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.style.borderColor = '#e53e3e';
                } else {
                    this.style.borderColor = '#e2e8f0';
                }
            });
            
            field.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.style.borderColor = '#e2e8f0';
                }
            });
        }
    });
    
    // URL validation
    const urlField = document.getElementById('jobUrl');
    if (urlField) {
        urlField.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url && !isValidUrl(url)) {
                this.style.borderColor = '#e53e3e';
            } else {
                this.style.borderColor = '#e2e8f0';
            }
        });
    }
});