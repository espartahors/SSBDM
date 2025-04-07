from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from .models import EquipmentDocument, DocumentCategory
from equipment_new.models import Equipment

class EquipmentDocumentListView(LoginRequiredMixin, ListView):
    model = EquipmentDocument
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    ordering = ['-upload_date']

class EquipmentDocumentDetailView(LoginRequiredMixin, DetailView):
    model = EquipmentDocument
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

class EquipmentDocumentCreateView(LoginRequiredMixin, CreateView):
    model = EquipmentDocument
    template_name = 'documents/document_form.html'
    fields = ['equipment', 'title', 'document_type', 'file', 'description']
    success_url = reverse_lazy('documents:document_list')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

class EquipmentDocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = EquipmentDocument
    template_name = 'documents/document_form.html'
    fields = ['equipment', 'title', 'document_type', 'file', 'description']
    success_url = reverse_lazy('documents:document_list')

class EquipmentDocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = EquipmentDocument
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')

@login_required
def download_document(request, pk):
    document = get_object_or_404(EquipmentDocument, pk=pk)
    response = FileResponse(document.file, as_attachment=True)
    return response

class DocumentCategoryDetailView(LoginRequiredMixin, DetailView):
    model = DocumentCategory
    template_name = 'documents/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = EquipmentDocument.objects.filter(category=self.object)
        return context

class DocumentCategoryListView(LoginRequiredMixin, ListView):
    model = DocumentCategory
    template_name = 'documents/category_list.html'
    context_object_name = 'categories'

class DocumentCategoryCreateView(LoginRequiredMixin, CreateView):
    model = DocumentCategory
    template_name = 'documents/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('documents:category_list')

class DocumentCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentCategory
    template_name = 'documents/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('documents:category_list')

class DocumentCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentCategory
    template_name = 'documents/category_confirm_delete.html'
    success_url = reverse_lazy('documents:category_list') 