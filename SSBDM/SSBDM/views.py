from django.shortcuts import render
# This file can remain empty or be used for project-wide views if needed

def redesign_demo(request):
    """
    View to display the redesign demo page showcasing the new UI components
    """
    return render(request, 'redesign_demo.html')

def conversion_guide(request):
    """
    View to display the template conversion guide
    """
    return render(request, 'conversion_guide.html')

def redesigned_dashboard(request):
    """
    View to display a redesigned dashboard example
    """
    return render(request, 'redesign_examples/dashboard.html')

def tree_views_demo(request):
    """
    View to display the tree view design options demo
    """
    return render(request, 'tree_views_demo.html') 