"""
Helper functions for common operations across the application.
"""
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg


def generate_unique_code(prefix='', length=8):
    """
    Generate a unique code with optional prefix.
    
    Args:
        prefix (str): Prefix for the code
        length (int): Length of the random part of the code
        
    Returns:
        str: Unique code
    """
    unique_id = uuid.uuid4().hex[:length].upper()
    return f"{prefix}{unique_id}"


def get_date_range(days=30):
    """
    Get date range from today to X days ago.
    
    Args:
        days (int): Number of days in the past
        
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def calculate_trends(queryset, date_field='created_at', days=30):
    """
    Calculate trends over time for a queryset.
    
    Args:
        queryset: The queryset to analyze
        date_field (str): The date field to use
        days (int): Number of days to analyze
        
    Returns:
        dict: Dictionary with trend data
    """
    start_date, end_date = get_date_range(days)
    
    # Filter queryset to date range
    filtered_qs = queryset.filter(**{
        f"{date_field}__gte": start_date,
        f"{date_field}__lte": end_date
    })
    
    # Group by date
    trends = filtered_qs.extra(
        select={'date': f"date({date_field})"}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'data': list(trends),
        'total': filtered_qs.count()
    } 