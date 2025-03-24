document.addEventListener('DOMContentLoaded', function() {
    // Get container and form elements
    const container = document.getElementById('container');
    const signInContainer = document.querySelector('.sign-in-container');
    const signUpContainer = document.querySelector('.sign-up-container');
    const mobileSwitchButton = document.getElementById('mobileSwitchButton');
    
    // Fix initialization issue - make sure form containers are visible
    signInContainer.style.display = 'flex';
    signUpContainer.style.display = 'flex';
    
    // Fix initial container class issue if present in the HTML
    if (container.getAttribute('class') === 'right-panel-active') {
        container.removeAttribute('class');
        container.classList.add('right-panel-active');
    }
    
    // Set initial state based on URL
    const currentPath = window.location.pathname;
    if (currentPath.includes('register')) {
        container.classList.add('right-panel-active');
        makeRegistrationFormVisible();
        
        if (mobileSwitchButton) {
            mobileSwitchButton.textContent = 'Đăng nhập';
            mobileSwitchButton.setAttribute('data-target', 'login');
        }
    } else {
        container.classList.remove('right-panel-active');
        makeLoginFormVisible();
        
        if (mobileSwitchButton) {
            mobileSwitchButton.textContent = 'Đăng ký';
            mobileSwitchButton.setAttribute('data-target', 'register');
        }
    }
    
    // Helper functions to ensure form visibility
    function makeRegistrationFormVisible() {
        signUpContainer.style.opacity = '1';
        signUpContainer.style.visibility = 'visible';
        signUpContainer.style.display = 'flex';
        signUpContainer.style.transform = window.innerWidth <= 768 ? 'translateY(0)' : 'translateX(100%)';
        signUpContainer.style.zIndex = '5';
        
        signInContainer.style.opacity = '0';
        signInContainer.style.visibility = 'hidden';
        signInContainer.style.transform = window.innerWidth <= 768 ? 'translateY(-100%)' : 'translateX(100%)';
        signInContainer.style.zIndex = '1';
    }
    
    function makeLoginFormVisible() {
        signInContainer.style.opacity = '1';
        signInContainer.style.visibility = 'visible';
        signInContainer.style.display = 'flex';
        signInContainer.style.transform = 'translateX(0)';
        signInContainer.style.zIndex = '2';
        
        signUpContainer.style.opacity = '0';
        signUpContainer.style.visibility = 'hidden';
        signUpContainer.style.transform = window.innerWidth <= 768 ? 'translateY(100%)' : 'translateX(-100%)';
        signUpContainer.style.zIndex = '1';
    }
    
    // Add event listeners to form switch buttons
    const switchButtons = document.querySelectorAll('.switch-form');
    switchButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetForm = this.getAttribute('data-target');
            switchForm(targetForm);
        });
    });
    
    // Mobile toggle button functionality
    if (mobileSwitchButton) {
        mobileSwitchButton.addEventListener('click', function() {
            const targetForm = this.getAttribute('data-target');
            switchForm(targetForm);
        });
    }
    
    // Handle browser back/forward events
    window.addEventListener('popstate', function(e) {
        const currentPath = window.location.pathname;
        if (currentPath.includes('register')) {
            switchForm('register', false);
        } else {
            switchForm('login', false);
        }
    });
    
    // Function to handle form switching
    function switchForm(targetForm, updateHistory = true) {
        if (targetForm === 'register') {
            // First fetch form data if needed
            fetchForm('register');
            
            // Update UI for registration
            container.classList.add('right-panel-active');
            makeRegistrationFormVisible();
            
            // Update mobile button
            if (mobileSwitchButton) {
                mobileSwitchButton.textContent = 'Đăng nhập';
                mobileSwitchButton.setAttribute('data-target', 'login');
            }
            
            // Update browser history
            if (updateHistory) {
                history.pushState({page: 'register'}, 'Đăng ký - Python Manager', '/register');
            }
            document.title = 'Đăng ký - Python Manager';
            
            // Ensure proper focus and display
            setTimeout(() => {
                const firstInput = signUpContainer.querySelector('input:not([type="hidden"])');
                if (firstInput) firstInput.focus();
            }, 700);
        } else {
            // First fetch form data if needed
            fetchForm('login');
            
            // Update UI for login
            container.classList.remove('right-panel-active');
            makeLoginFormVisible();
            
            // Update mobile button
            if (mobileSwitchButton) {
                mobileSwitchButton.textContent = 'Đăng ký';
                mobileSwitchButton.setAttribute('data-target', 'register');
            }
            
            // Update browser history
            if (updateHistory) {
                history.pushState({page: 'login'}, 'Đăng nhập - Python Manager', '/login');
            }
            document.title = 'Đăng nhập - Python Manager';
            
            // Ensure proper focus and display
            setTimeout(() => {
                const firstInput = signInContainer.querySelector('input:not([type="hidden"])');
                if (firstInput) firstInput.focus();
            }, 700);
        }
    }
    
    // Function to fetch form data via AJAX
    function fetchForm(formType) {
        fetch(`/get-form-data/${formType}`)
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Network response was not ok');
            })
            .then(data => {
                if (data.csrf_token) {
                    const form = document.getElementById(formType === 'login' ? 'login-form' : 'register-form');
                    const csrfInput = form.querySelector('input[name="csrf_token"]');
                    if (csrfInput) {
                        csrfInput.value = data.csrf_token;
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching form data:', error);
            });
    }
    
    // Force a reflow to ensure proper initial state
    void container.offsetWidth;
    
    // Improve animation performance with GPU acceleration
    container.style.willChange = 'transform';
    signInContainer.style.willChange = 'transform, opacity';
    signUpContainer.style.willChange = 'transform, opacity';
    
    if (document.querySelector('.overlay')) {
        document.querySelector('.overlay').style.willChange = 'transform';
    }
    
    // Ensure forms are properly displayed
    setTimeout(() => {
        signUpContainer.style.display = '';
        signInContainer.style.display = '';
    }, 100);
});