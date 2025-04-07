/**
 * SSBDM - Main Application JavaScript
 * Handles loading screen, navigation enhancements, and UI interactions
 */

// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Loading screen functionality
    const loadingScreen = document.querySelector('.loading-screen');
    
    if (loadingScreen) {
        // Force loading screen to be visible for at least 1.5 seconds
        setTimeout(function() {
            loadingScreen.classList.add('fade-out');
            
            // Remove from DOM after transition completes
            setTimeout(function() {
                loadingScreen.style.display = 'none';
            }, 500);
        }, 1500);
    }
    
    // Dropdown hover effect for desktop
    const dropdowns = document.querySelectorAll('.navbar .dropdown');
    
    if (window.innerWidth >= 992) {
        dropdowns.forEach(function(dropdown) {
            dropdown.addEventListener('mouseenter', function() {
                this.querySelector('.dropdown-toggle').click();
            });
            
            dropdown.addEventListener('mouseleave', function() {
                this.querySelector('.dropdown-toggle').click();
            });
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Make tables responsive with horizontal scroll on small screens
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
    
    // Add animation to dashboard widgets
    const widgets = document.querySelectorAll('.dashboard-widget');
    if (widgets.length) {
        widgets.forEach(function(widget, index) {
            widget.style.opacity = '0';
            widget.style.transform = 'translateY(20px)';
            widget.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(function() {
                widget.style.opacity = '1';
                widget.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
        });
    }
    
    // Add animation to alerts
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length) {
        alerts.forEach(function(alert) {
            // Auto-dismiss alerts after 5 seconds
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }
    
    // Enhanced form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Handle filter panel toggle
    const filterToggleButtons = document.querySelectorAll('.filter-toggle');
    
    filterToggleButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const filterPanel = document.querySelector(targetId);
            
            if (filterPanel) {
                if (filterPanel.style.display === 'none') {
                    filterPanel.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-times"></i> Hide Filters';
                } else {
                    filterPanel.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-filter"></i> Show Filters';
                }
            }
        });
    });
    
    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Initialize mobile menu close on click (for better UX on mobile)
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                const navbarToggler = document.querySelector('.navbar-toggler');
                navbarToggler.click();
            }
        });
    });
    
    // Add active class to nav items based on current URL
    const currentPath = window.location.pathname;
    const navbarLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navbarLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
            
            // If inside dropdown, also mark dropdown toggle as active
            const parentDropdown = link.closest('.dropdown');
            if (parentDropdown) {
                const dropdownToggle = parentDropdown.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
}); 