from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # App URLs - Legacy (disabled to prevent conflicts)
    # path('equipment/', include('equipment.urls')),
    # path('maintenance/', include('maintenance.urls')),
    # path('spare-parts/', include('spare_parts.urls')),
    
    # Keep documents and ssbom enabled
    path('documents/', include('documents.urls')),
    path('ssbom/', include('ssbom.urls')),
    
    # New API modules - Restructured
    path('api/equipment/', include('equipment_new.urls')),
    path('api/maintenance/', include('maintenance_new.urls')),
    path('api/spare-parts/', include('spare_parts_new.urls')),
    
    # Redesign examples
    path('redesign-examples/status-badges/', TemplateView.as_view(template_name='redesign_examples/status_badges.html'), name='redesign_status_badges'),
    
    # Home page - Update to use a new URL pattern
    path('', RedirectView.as_view(pattern_name='equipment_new:dashboard'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)