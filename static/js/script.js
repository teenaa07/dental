document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Close mobile menu when a link is clicked
    const links = document.querySelectorAll('.nav-links a');
    links.forEach(link => {
        link.addEventListener('click', () => {
            if (navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
            }
        });
    });

    // Appointment Booking Form Submission
    const appointmentForm = document.getElementById('appointment-form');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submit-btn');
            const formMessage = document.getElementById('form-message');
            
            // Disable button
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
            
            const formData = new FormData(appointmentForm);
            
            fetch('/book', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                formMessage.style.display = 'block';
                if (data.success) {
                    formMessage.className = 'alert alert-success';
                    formMessage.innerHTML = '<i class="fa-solid fa-check-circle"></i> ' + data.message;
                    appointmentForm.reset();
                } else {
                    formMessage.className = 'alert alert-error';
                    formMessage.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> ' + data.message;
                }
            })
            .catch(error => {
                formMessage.style.display = 'block';
                formMessage.className = 'alert alert-error';
                formMessage.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> An error occurred. Please try again.';
                console.error('Error:', error);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit Request';
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    formMessage.style.display = 'none';
                }, 5000);
            });
        });
    }

    // Feedback Form Submission
    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = feedbackForm.querySelector('button[type="submit"]');
            const feedbackMessage = document.getElementById('feedback-message');
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
            
            const formData = new FormData(feedbackForm);
            
            fetch('/feedback', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                feedbackMessage.style.display = 'block';
                if (data.success) {
                    feedbackMessage.className = 'alert alert-success';
                    feedbackMessage.innerHTML = '<i class="fa-solid fa-check-circle"></i> ' + data.message;
                    feedbackForm.reset();
                    // Reload page after successful feedback to see it in the list
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    feedbackMessage.className = 'alert alert-error';
                    feedbackMessage.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> ' + data.message;
                }
            })
            .catch(error => {
                feedbackMessage.style.display = 'block';
                feedbackMessage.className = 'alert alert-error';
                feedbackMessage.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> An error occurred. Please try again.';
                console.error('Error:', error);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit Feedback';
            });
        });
    }
});
