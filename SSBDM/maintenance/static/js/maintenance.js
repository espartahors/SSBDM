// Show loading spinner
function showSpinner() {
    $('#loading-spinner').show();
}

// Hide loading spinner
function hideSpinner() {
    $('#loading-spinner').hide();
}

// Initialize tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}

// Initialize popovers
function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
}

// Document ready handler
$(document).ready(function() {
    // Initialize tooltips and popovers
    initTooltips();
    initPopovers();
    
    // Hide loading spinner after initial page load
    hideSpinner();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
    
    // Add event listeners for AJAX form submission
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action');
        const formData = new FormData(this);
        
        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function() {
                showSpinner();
            },
            success: function(response) {
                if (response.success) {
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else {
                        // Show success message
                        const alert = `
                            <div class="alert alert-success alert-dismissible fade show" role="alert">
                                ${response.message}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;
                        $('#alerts-container').html(alert);
                        
                        // Reset form if needed
                        if (response.reset_form) {
                            form[0].reset();
                        }
                    }
                } else {
                    // Show error message
                    const alert = `
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            ${response.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    $('#alerts-container').html(alert);
                }
            },
            error: function(xhr, status, error) {
                // Show error message
                const alert = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        An error occurred: ${error}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                $('#alerts-container').html(alert);
            },
            complete: function() {
                hideSpinner();
            }
        });
    });
    
    // Equipment filter handling
    $('#equipment-filter-form select').change(function() {
        $('#equipment-filter-form').submit();
    });
});