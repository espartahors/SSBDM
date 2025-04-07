from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import UserProfile, Role, AuditLog, SecuritySettings
from .forms import UserCreateForm, UserUpdateForm, RoleForm, SecuritySettingsForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'security/user_list.html'
    permission_required = 'security.manage_users'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.select_related('profile').all()

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'security/user_form.html'
    permission_required = 'security.manage_users'
    success_url = reverse_lazy('security:user_list')

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('User created successfully'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error creating user'))
            return self.form_invalid(form)

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'security/user_form.html'
    permission_required = 'security.manage_users'
    success_url = reverse_lazy('security:user_list')

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('User updated successfully'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error updating user'))
            return self.form_invalid(form)

class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'security/user_confirm_delete.html'
    permission_required = 'security.manage_users'
    success_url = reverse_lazy('security:user_list')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, _('User deleted successfully'))
            return response
        except Exception as e:
            messages.error(request, _('Error deleting user'))
            return redirect(self.success_url)

class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Role
    template_name = 'security/role_list.html'
    permission_required = 'security.manage_roles'
    context_object_name = 'roles'

class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'security/role_form.html'
    permission_required = 'security.manage_roles'
    success_url = reverse_lazy('security:role_list')

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('Role created successfully'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error creating role'))
            return self.form_invalid(form)

class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'security/role_form.html'
    permission_required = 'security.manage_roles'
    success_url = reverse_lazy('security:role_list')

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('Role updated successfully'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error updating role'))
            return self.form_invalid(form)

class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Role
    template_name = 'security/role_confirm_delete.html'
    permission_required = 'security.manage_roles'
    success_url = reverse_lazy('security:role_list')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, _('Role deleted successfully'))
            return response
        except Exception as e:
            messages.error(request, _('Error deleting role'))
            return redirect(self.success_url)

class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AuditLog
    template_name = 'security/audit_log_list.html'
    permission_required = 'security.view_audit_logs'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        return AuditLog.objects.select_related('user').order_by('-timestamp')

class SecuritySettingsView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SecuritySettings
    form_class = SecuritySettingsForm
    template_name = 'security/settings_form.html'
    permission_required = 'security.manage_roles'
    success_url = reverse_lazy('security:settings')

    def get_object(self):
        return SecuritySettings.objects.first() or SecuritySettings.objects.create()

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('Security settings updated successfully'))
            return response
        except Exception as e:
            messages.error(self.request, _('Error updating security settings'))
            return self.form_invalid(form)

@login_required
@permission_required('security.view_audit_logs')
def audit_log_detail(request, pk):
    log = get_object_or_404(AuditLog, pk=pk)
    return render(request, 'security/audit_log_detail.html', {'log': log})

@login_required
@permission_required('security.manage_users')
def user_activity(request, pk):
    user = get_object_or_404(User, pk=pk)
    logs = AuditLog.objects.filter(user=user).order_by('-timestamp')[:50]
    return render(request, 'security/user_activity.html', {
        'user': user,
        'logs': logs
    }) 