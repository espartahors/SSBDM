from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Mixin to add timestamp fields to models."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CodeNameMixin(models.Model):
    """Mixin to add code and name fields to models."""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True
        
    def __str__(self):
        return f"{self.code} - {self.name}"


class StatusMixin(models.Model):
    """Mixin to add active status to models."""
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class NotesMixin(models.Model):
    """Mixin to add notes to models."""
    notes = models.TextField(blank=True)
    
    class Meta:
        abstract = True 