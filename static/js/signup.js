document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordMatch = document.getElementById('passwordMatch');
    const strengthFill = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');
    const signupBtn = document.getElementById('signupBtn');
    const spinner = document.getElementById('spinner');
    const btnText = document.querySelector('.btn-text');
    const alert = document.getElementById('alert');

    // Password strength checker
    function checkPasswordStrength(password) {
        let strength = 0;
        let feedback = [];

        if (password.length >= 8) strength += 1;
        else feedback.push('At least 8 characters');

        if (/[a-z]/.test(password)) strength += 1;
        else feedback.push('Lowercase letter');

        if (/[A-Z]/.test(password)) strength += 1;
        else feedback.push('Uppercase letter');

        if (/[0-9]/.test(password)) strength += 1;
        else feedback.push('Number');

        if (/[^A-Za-z0-9]/.test(password)) strength += 1;
        else feedback.push('Special character');

        return { strength, feedback };
    }

    // Update password strength indicator
    function updatePasswordStrength() {
        const password = passwordInput.value;
        const { strength, feedback } = checkPasswordStrength(password);
        
        const percentage = (strength / 5) * 100;
        strengthFill.style.width = percentage + '%';
        
        // Remove existing strength classes
        strengthFill.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
        
        if (strength <= 2) {
            strengthFill.classList.add('strength-weak');
            strengthText.textContent = 'Weak password';
        } else if (strength === 3) {
            strengthFill.classList.add('strength-fair');
            strengthText.textContent = 'Fair password';
        } else if (strength === 4) {
            strengthFill.classList.add('strength-good');
            strengthText.textContent = 'Good password';
        } else {
            strengthFill.classList.add('strength-strong');
            strengthText.textContent = 'Strong password';
        }

        if (password === '') {
            strengthFill.style.width = '0%';
            strengthText.textContent = 'Password strength';
            strengthFill.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
        }
    }

    // Check password match
    function checkPasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword === '') {
            passwordMatch.textContent = '';
            passwordMatch.classList.remove('match', 'no-match');
            return null;
        }
        
        if (password === confirmPassword) {
            passwordMatch.textContent = '✓ Passwords match';
            passwordMatch.classList.remove('no-match');
            passwordMatch.classList.add('match');
            return true;
        } else {
            passwordMatch.textContent = '✗ Passwords do not match';
            passwordMatch.classList.remove('match');
            passwordMatch.classList.add('no-match');
            return false;
        }
    }

    // Toggle password visibility
    window.togglePassword = function(inputId) {
        const input = document.getElementById(inputId);
        const button = input.parentElement.querySelector('.toggle-password i');
        
        if (input.type === 'password') {
            input.type = 'text';
            button.classList.remove('fa-eye');
            button.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            button.classList.remove('fa-eye-slash');
            button.classList.add('fa-eye');
        }
    };

    // Show alert message
    function showAlert(message, type) {
        alert.textContent = message;
        alert.className = `alert ${type} show`;
        
        setTimeout(() => {
            alert.classList.remove('show');
        }, 5000);
    }

    // Form validation
    function validateForm() {
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const terms = document.getElementById('terms').checked;

        if (!username) {
            showAlert('Please enter a username', 'error');
            return false;
        }

        if (username.length < 3) {
            showAlert('Username must be at least 3 characters long', 'error');
            return false;
        }

        if (!email) {
            showAlert('Please enter an email address', 'error');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showAlert('Please enter a valid email address', 'error');
            return false;
        }

        if (!password) {
            showAlert('Please enter a password', 'error');
            return false;
        }

        const { strength } = checkPasswordStrength(password);
        if (strength < 3) {
            showAlert('Password is too weak. Please choose a stronger password.', 'error');
            return false;
        }

        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            return false;
        }

        if (!terms) {
            showAlert('Please accept the terms and conditions', 'error');
            return false;
        }

        return true;
    }

    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        // Show loading state
        signupBtn.disabled = true;
        spinner.style.display = 'block';
        btnText.textContent = 'Creating Account...';

        const formData = {
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: passwordInput.value
        };

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                showAlert('Account created successfully! Redirecting to login...', 'success');
                
                // Store the username for potential auto-fill on login
                localStorage.setItem('signup_username', formData.username);
                
                // Reset form
                form.reset();
                updatePasswordStrength();
                checkPasswordMatch();
                
                // Redirect to login page after 2 seconds
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showAlert(data.msg || 'An error occurred during signup', 'error');
            }
        } catch (error) {
            console.error('Signup error:', error);
            showAlert('Network error. Please check your connection and try again.', 'error');
        } finally {
            // Reset loading state
            signupBtn.disabled = false;
            spinner.style.display = 'none';
            btnText.textContent = 'Create Account';
        }
    }

    // Event listeners
    passwordInput.addEventListener('input', updatePasswordStrength);
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    passwordInput.addEventListener('input', checkPasswordMatch);
    form.addEventListener('submit', handleSubmit);

    // Real-time validation feedback
    document.getElementById('username').addEventListener('blur', function() {
        const username = this.value.trim();
        if (username && username.length < 3) {
            this.style.borderColor = '#e53e3e';
        } else {
            this.style.borderColor = '#e2e8f0';
        }
    });

    document.getElementById('email').addEventListener('blur', function() {
        const email = this.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email && !emailRegex.test(email)) {
            this.style.borderColor = '#e53e3e';
        } else {
            this.style.borderColor = '#e2e8f0';
        }
    });
});