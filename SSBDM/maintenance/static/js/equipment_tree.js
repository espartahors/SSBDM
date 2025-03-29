$(document).ready(function() {
    // Initialize JSTree with AJAX loading
    $('#jstree').jstree({
        'core': {
            'data': {
                'url': '/api/equipment-tree/',
                'dataType': 'json'
            },
            'themes': {
                'variant': 'large'
            }
        },
        'plugins': ['types', 'search'],
        'types': {
            'area': {
                'icon': 'fas fa-building'
            },
            'equipment': {
                'icon': 'fas fa-cog'
            }
        }
    });

    // Handle node selection
    $('#jstree').on('select_node.jstree', function(e, data) {
        const nodeId = data.node.id;
        
        // Extract entity type and ID from the node ID
        const [entityType, idStr] = nodeId.split('_');
        const id = parseInt(idStr);
        
        if (entityType === 'equipment') {
            window.location.href = `/equipment/${id}/`;
        } else if (entityType === 'area') {
            window.location.href = `/areas/${id}/`;
        }
    });

    // Setup search
    var searchTimeout;
    $('#equipmentSearch').keyup(function() {
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        searchTimeout = setTimeout(function() {
            var v = $('#equipmentSearch').val();
            $('#jstree').jstree(true).search(v);
        }, 250);
    });
});