import uuid
from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """
    Base model for all models in the application.
    Provides common fields like created_at, updated_at, created_by, updated_by, and id.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="%(app_label)s_%(class)s_updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at'] 