/**
 * SSBDM Redesigned UI Functionality
 * 
 * This file contains all the JavaScript functionality for the redesigned UI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize card toggles
    initCardToggles();
    
    // Initialize back to top button
    initBackToTop();
    
    // Initialize row action toggles for tables
    initRowActions();
    
    // Initialize form validation
    initFormValidation();
    
    // Fix dropdown menus in navigation
    fixDropdownMenus();
    
    // Hide loading screen after page is fully loaded
    setTimeout(function() {
        const loadingScreen = document.querySelector('.loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('fade-out');
            
            // Remove loading screen from DOM after transition completes
            loadingScreen.addEventListener('transitionend', function() {
                loadingScreen.remove();
            });
        }
    }, 500); // Short delay to ensure everything is ready
});

/**
 * Fix dropdown menus in the navigation bar to prevent them from closing too quickly
 */
function fixDropdownMenus() {
    // Get all dropdown toggles in the navbar
    const dropdownToggles = document.querySelectorAll('.navbar .dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        // Get the parent dropdown element
        const dropdown = toggle.closest('.dropdown');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        // Add mouseenter event to show dropdown
        dropdown.addEventListener('mouseenter', function() {
            menu.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
        });
        
        // Add mouseleave event with delay to hide dropdown
        dropdown.addEventListener('mouseleave', function() {
            // Use a timeout to prevent the menu from closing too quickly
            setTimeout(function() {
                // Check if we're still not hovering over the dropdown
                if (!dropdown.matches(':hover')) {
                    menu.classList.remove('show');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            }, 200);
        });
        
        // Add click event to prevent the default behavior 
        // (which is to toggle the dropdown) and make it stay open
        toggle.addEventListener('click', function(e) {
            // If menu is already open, allow it to close
            if (menu.classList.contains('show')) {
                return;
            }
            
            // Otherwise, prevent default and manually show the menu
            e.preventDefault();
            e.stopPropagation();
            menu.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
        });
    });
    
    // For dropdown menus inside row actions or elsewhere
    document.querySelectorAll('.row-actions-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent the click from propagating
            
            // Close all other open action menus
            document.querySelectorAll('.row-actions-menu.show').forEach(menu => {
                if (menu !== this.nextElementSibling) {
                    menu.classList.remove('show');
                }
            });
            
            // Toggle this menu
            const actionsMenu = this.nextElementSibling;
            actionsMenu.classList.toggle('show');
        });
    });
    
    // Close menus when clicking elsewhere
    document.addEventListener('click', function(e) {
        // Don't close if clicking inside a dropdown menu
        if (e.target.closest('.dropdown-menu')) {
            return;
        }
        
        // Close all dropdown menus
        document.querySelectorAll('.row-actions-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    });
}

/**
 * Initialize collapsible card functionality
 */
function initCardToggles() {
    document.querySelectorAll('.card-header .toggle-icon').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const card = this.closest('.card');
            const cardBody = card.querySelector('.card-body');
            
            if (cardBody.style.display === 'none') {
                // Expand card
                cardBody.style.display = '';
                this.classList.remove('collapsed');
            } else {
                // Collapse card
                cardBody.style.display = 'none';
                this.classList.add('collapsed');
            }
        });
    });
}

/**
 * Initialize back to top button functionality
 */
function initBackToTop() {
    const backToTopButton = document.querySelector('.back-to-top');
    
    if (backToTopButton) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        // Scroll to top when clicked
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Initialize table row action menus
 */
function initRowActions() {
    document.querySelectorAll('.row-actions-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Close any other open action menus
            document.querySelectorAll('.row-actions-menu.show').forEach(menu => {
                if (menu !== this.nextElementSibling) {
                    menu.classList.remove('show');
                }
            });
            
            // Toggle this menu
            const actionsMenu = this.nextElementSibling;
            actionsMenu.classList.toggle('show');
        });
    });
    
    // Close action menus when clicking elsewhere
    document.addEventListener('click', function() {
        document.querySelectorAll('.row-actions-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    });
}

/**
 * Initialize Bootstrap form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Tree View Functions
 */
function initTreeView(selector, options) {
    const defaultOptions = {
        core: {
            themes: {
                name: 'proton',
                responsive: true
            }
        },
        plugins: ['types', 'state', 'wholerow']
    };
    
    const mergedOptions = {...defaultOptions, ...options};
    return $(selector).jstree(mergedOptions);
}

/**
 * Custom Tree Builder - supports multiple tree view types
 */
function buildCustomTree(container, data, options = {}) {
    const treeType = options.treeType || 'default';
    const containerElement = document.querySelector(container);
    
    if (!containerElement || !data) return;
    
    // Clear container
    containerElement.innerHTML = '';
    
    if (treeType === 'default' || treeType === 'jsTree') {
        // Use jsTree (already handled elsewhere)
        return;
    } else if (treeType === 'custom-list') {
        // Build custom list-style tree
        buildListTree(containerElement, data);
    } else if (treeType === 'cards') {
        // Build card-style tree
        buildCardTree(containerElement, data);
    } else if (treeType === 'folder') {
        // Build folder-style tree
        buildFolderTree(containerElement, data);
    }
}

/**
 * Build a list-style tree view
 */
function buildListTree(container, data, level = 0) {
    const list = document.createElement('ul');
    list.className = 'custom-tree-list';
    
    if (level > 0) {
        list.classList.add('nested');
    }
    
    data.forEach(item => {
        const listItem = document.createElement('li');
        listItem.className = 'tree-item';
        
        const itemContent = document.createElement('div');
        itemContent.className = 'tree-item-content';
        
        // Add appropriate icon
        const icon = document.createElement('i');
        icon.className = item.icon || (item.children && item.children.length ? 'fas fa-folder' : 'fas fa-file');
        icon.classList.add('tree-item-icon');
        itemContent.appendChild(icon);
        
        // Add text
        const text = document.createElement('span');
        text.className = 'tree-item-text';
        text.textContent = item.text;
        itemContent.appendChild(text);
        
        listItem.appendChild(itemContent);
        
        // Add toggle if has children
        if (item.children && item.children.length) {
            // Add toggle button
            const toggle = document.createElement('span');
            toggle.className = 'tree-toggle';
            toggle.innerHTML = '<i class="fas fa-chevron-right"></i>';
            itemContent.insertBefore(toggle, itemContent.firstChild);
            
            // Add nested children
            buildListTree(listItem, item.children, level + 1);
            
            // Toggle functionality
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                this.classList.toggle('open');
                const nestedList = this.closest('.tree-item').querySelector('.nested');
                if (nestedList) {
                    nestedList.classList.toggle('active');
                }
            });
        }
        
        // Add click event to the entire item
        itemContent.addEventListener('click', function() {
            // Remove active class from all items
            document.querySelectorAll('.tree-item-content.active').forEach(el => {
                el.classList.remove('active');
            });
            
            // Add active class to this item
            this.classList.add('active');
            
            // Trigger item selected event
            const event = new CustomEvent('treeItemSelected', {
                detail: { id: item.id, text: item.text, data: item }
            });
            document.dispatchEvent(event);
        });
        
        list.appendChild(listItem);
    });
    
    container.appendChild(list);
}

/**
 * Build a card-style tree view
 */
function buildCardTree(container, data) {
    const cardContainer = document.createElement('div');
    cardContainer.className = 'tree-cards';
    
    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'tree-card';
        card.dataset.id = item.id;
        
        const cardIcon = document.createElement('div');
        cardIcon.className = 'tree-card-icon';
        
        const icon = document.createElement('i');
        icon.className = item.icon || 'fas fa-folder';
        cardIcon.appendChild(icon);
        
        const cardContent = document.createElement('div');
        cardContent.className = 'tree-card-content';
        
        const title = document.createElement('div');
        title.className = 'tree-card-title';
        title.textContent = item.text;
        
        cardContent.appendChild(title);
        
        if (item.description) {
            const desc = document.createElement('div');
            desc.className = 'tree-card-description';
            desc.textContent = item.description;
            cardContent.appendChild(desc);
        }
        
        card.appendChild(cardIcon);
        card.appendChild(cardContent);
        
        // Add click event
        card.addEventListener('click', function() {
            // Handle drill down if has children
            if (item.children && item.children.length) {
                // Clear container
                container.innerHTML = '';
                
                // Add back button
                const backBtn = document.createElement('button');
                backBtn.className = 'tree-back-btn';
                backBtn.innerHTML = '<i class="fas fa-arrow-left"></i> Back';
                backBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    // Rebuild original tree
                    container.innerHTML = '';
                    buildCardTree(container, data);
                });
                
                container.appendChild(backBtn);
                
                // Build children
                buildCardTree(container, item.children);
            } else {
                // Trigger item selected event
                const event = new CustomEvent('treeItemSelected', {
                    detail: { id: item.id, text: item.text, data: item }
                });
                document.dispatchEvent(event);
                
                // Visual selection
                document.querySelectorAll('.tree-card.active').forEach(el => {
                    el.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
        
        cardContainer.appendChild(card);
    });
    
    container.appendChild(cardContainer);
}

/**
 * Build a folder-style tree view
 */
function buildFolderTree(container, data) {
    const folderContainer = document.createElement('div');
    folderContainer.className = 'folder-tree';
    
    // Add navigation breadcrumb
    const breadcrumb = document.createElement('div');
    breadcrumb.className = 'folder-breadcrumb';
    
    // Root folder breadcrumb
    const rootCrumb = document.createElement('span');
    rootCrumb.className = 'breadcrumb-item active';
    rootCrumb.innerHTML = '<i class="fas fa-home"></i> Root';
    breadcrumb.appendChild(rootCrumb);
    
    folderContainer.appendChild(breadcrumb);
    
    // Create folder content
    const folderContent = document.createElement('div');
    folderContent.className = 'folder-content';
    
    data.forEach(item => {
        const folderItem = document.createElement('div');
        folderItem.className = item.children && item.children.length ? 'folder-item is-folder' : 'folder-item is-file';
        folderItem.dataset.id = item.id;
        
        const itemIcon = document.createElement('div');
        itemIcon.className = 'folder-item-icon';
        
        const icon = document.createElement('i');
        if (item.children && item.children.length) {
            icon.className = item.icon || 'fas fa-folder';
        } else {
            icon.className = item.icon || 'fas fa-file';
        }
        itemIcon.appendChild(icon);
        
        const itemName = document.createElement('div');
        itemName.className = 'folder-item-name';
        itemName.textContent = item.text;
        
        folderItem.appendChild(itemIcon);
        folderItem.appendChild(itemName);
        
        // Add click handler
        folderItem.addEventListener('click', function() {
            if (item.children && item.children.length) {
                // Navigate into folder
                navigateFolder(container, data, item, [{ id: 'root', text: 'Root' }]);
            } else {
                // Select file
                document.querySelectorAll('.folder-item.active').forEach(el => {
                    el.classList.remove('active');
                });
                this.classList.add('active');
                
                // Trigger item selected event
                const event = new CustomEvent('treeItemSelected', {
                    detail: { id: item.id, text: item.text, data: item }
                });
                document.dispatchEvent(event);
            }
        });
        
        folderContent.appendChild(folderItem);
    });
    
    folderContainer.appendChild(folderContent);
    container.appendChild(folderContainer);
}

/**
 * Navigate to a subfolder in the folder tree
 */
function navigateFolder(container, originalData, folder, breadcrumbPath) {
    // Update container
    container.innerHTML = '';
    
    const folderContainer = document.createElement('div');
    folderContainer.className = 'folder-tree';
    
    // Add navigation breadcrumb
    const breadcrumb = document.createElement('div');
    breadcrumb.className = 'folder-breadcrumb';
    
    // Add current path to breadcrumb
    breadcrumbPath.push({ id: folder.id, text: folder.text });
    
    breadcrumbPath.forEach((crumb, index) => {
        const crumbItem = document.createElement('span');
        crumbItem.className = index === breadcrumbPath.length - 1 ? 
            'breadcrumb-item active' : 'breadcrumb-item';
        
        if (index === 0) {
            crumbItem.innerHTML = '<i class="fas fa-home"></i> ' + crumb.text;
        } else {
            crumbItem.textContent = crumb.text;
        }
        
        // Add click handler for navigation
        if (index < breadcrumbPath.length - 1) {
            crumbItem.addEventListener('click', function() {
                // Navigate to this level
                if (index === 0) {
                    // Back to root
                    container.innerHTML = '';
                    buildFolderTree(container, originalData);
                } else {
                    // Find the folder data
                    const pathToHere = breadcrumbPath.slice(0, index + 1);
                    let currentData = originalData;
                    let currentFolder = null;
                    
                    // Skip root as it's the original data
                    for (let i = 1; i < pathToHere.length; i++) {
                        const targetId = pathToHere[i].id;
                        
                        // Find the folder with this ID
                        for (const item of currentData) {
                            if (item.id === targetId) {
                                currentFolder = item;
                                currentData = item.children || [];
                                break;
                            }
                        }
                    }
                    
                    if (currentFolder) {
                        navigateFolder(
                            container, 
                            originalData, 
                            currentFolder, 
                            breadcrumbPath.slice(0, index)
                        );
                    }
                }
            });
        }
        
        breadcrumb.appendChild(crumbItem);
        
        // Add separator
        if (index < breadcrumbPath.length - 1) {
            const separator = document.createElement('span');
            separator.className = 'breadcrumb-separator';
            separator.innerHTML = '<i class="fas fa-chevron-right"></i>';
            breadcrumb.appendChild(separator);
        }
    });
    
    folderContainer.appendChild(breadcrumb);
    
    // Create folder content
    const folderContent = document.createElement('div');
    folderContent.className = 'folder-content';
    
    // Get children of current folder
    const children = folder.children || [];
    
    children.forEach(item => {
        const folderItem = document.createElement('div');
        folderItem.className = item.children && item.children.length ? 'folder-item is-folder' : 'folder-item is-file';
        folderItem.dataset.id = item.id;
        
        const itemIcon = document.createElement('div');
        itemIcon.className = 'folder-item-icon';
        
        const icon = document.createElement('i');
        if (item.children && item.children.length) {
            icon.className = item.icon || 'fas fa-folder';
        } else {
            icon.className = item.icon || 'fas fa-file';
        }
        itemIcon.appendChild(icon);
        
        const itemName = document.createElement('div');
        itemName.className = 'folder-item-name';
        itemName.textContent = item.text;
        
        folderItem.appendChild(itemIcon);
        folderItem.appendChild(itemName);
        
        // Add click handler
        folderItem.addEventListener('click', function() {
            if (item.children && item.children.length) {
                // Navigate into folder
                navigateFolder(container, originalData, item, [...breadcrumbPath]);
            } else {
                // Select file
                document.querySelectorAll('.folder-item.active').forEach(el => {
                    el.classList.remove('active');
                });
                this.classList.add('active');
                
                // Trigger item selected event
                const event = new CustomEvent('treeItemSelected', {
                    detail: { id: item.id, text: item.text, data: item }
                });
                document.dispatchEvent(event);
            }
        });
        
        folderContent.appendChild(folderItem);
    });
    
    folderContainer.appendChild(folderContent);
    container.appendChild(folderContainer);
} 