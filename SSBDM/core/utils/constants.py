"""
Constant values and choices used throughout the application.
"""

# Status Choices
STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('pending', 'Pending'),
    ('archived', 'Archived'),
)

# Equipment Status Choices
EQUIPMENT_STATUS_CHOICES = (
    ('operational', 'Operational'),
    ('maintenance', 'Under Maintenance'),
    ('out_of_service', 'Out of Service'),
    ('retired', 'Retired'),
)

# Equipment Type Choices
EQUIPMENT_TYPE_CHOICES = (
    ('machine', 'Machine'),
    ('tool', 'Tool'),
    ('vehicle', 'Vehicle'),
    ('instrument', 'Instrument'),
    ('component', 'Component'),
    ('system', 'System'),
    ('assembly', 'Assembly'),
    ('other', 'Other'),
)

# Maintenance Types Choices
MAINTENANCE_TYPES = (
    ('preventive', 'Preventive Maintenance'),
    ('corrective', 'Corrective Maintenance'),
    ('predictive', 'Predictive Maintenance'),
    ('inspection', 'Inspection'),
    ('calibration', 'Calibration'),
    ('other', 'Other'),
)

# Maintenance Results Choices
MAINTENANCE_RESULTS = (
    ('successful', 'Successful'),
    ('partial', 'Partially Completed'),
    ('failed', 'Failed'),
    ('postponed', 'Postponed'),
)

# Task Status Choices
TASK_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
)

# Frequency Choices
FREQUENCY_CHOICES = (
    ('days', 'Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months'),
    ('years', 'Years'),
)

# Document Type Choices
DOCUMENT_TYPE_CHOICES = (
    ('manual', 'Operating Manual'),
    ('drawing', 'Technical Drawing'),
    ('certificate', 'Certificate'),
    ('procedure', 'Procedure'),
    ('other', 'Other'),
)

# Action Choices
ACTION_CHOICES = (
    ('create', 'Create'),
    ('update', 'Update'),
    ('delete', 'Delete'),
    ('view', 'View'),
)

# Inventory Status Choices
INVENTORY_STATUS_CHOICES = (
    ('in_stock', 'In Stock'),
    ('low_stock', 'Low Stock'),
    ('out_of_stock', 'Out of Stock'),
    ('ordered', 'Ordered'),
)

# Transaction Types
TRANSACTION_TYPES = (
    ('received', 'Received'),
    ('issued', 'Issued'),
    ('returned', 'Returned'),
    ('adjusted', 'Inventory Adjustment'),
)

# Currency Choices
CURRENCY_CHOICES = (
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
)

# Common Units
UNIT_CHOICES = (
    ('pcs', 'Pieces'),
    ('kg', 'Kilogram'),
    ('g', 'Gram'),
    ('l', 'Liter'),
    ('ml', 'Milliliter'),
    ('m', 'Meter'),
    ('cm', 'Centimeter'),
    ('mm', 'Millimeter'),
) 