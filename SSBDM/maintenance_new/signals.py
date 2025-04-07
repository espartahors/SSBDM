from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MaintenanceLog, MaintenanceTask, EquipmentDocument, MaintenancePlan
from .services import AuditLogService


@receiver(post_save, sender=MaintenanceLog)
def log_maintenance_log_save(sender, instance, created, **kwargs):
    """Log maintenance log creation/update."""
    action = 'create' if created else 'update'
    user = instance.created_by if created else instance.updated_by
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action=action,
            model_name='MaintenanceLog',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_delete, sender=MaintenanceLog)
def log_maintenance_log_delete(sender, instance, **kwargs):
    """Log maintenance log deletion."""
    user = instance.updated_by  # Use updated_by as the user who likely deleted it
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action='delete',
            model_name='MaintenanceLog',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_save, sender=MaintenanceTask)
def log_maintenance_task_save(sender, instance, created, **kwargs):
    """Log maintenance task creation/update."""
    action = 'create' if created else 'update'
    user = instance.created_by if created else instance.updated_by
    
    if user:
        service = AuditLogService(user=user)
        details = f"Task for {instance.maintenance_log.title}"
        
        service.log_action(
            action=action,
            model_name='MaintenanceTask',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_delete, sender=MaintenanceTask)
def log_maintenance_task_delete(sender, instance, **kwargs):
    """Log maintenance task deletion."""
    user = instance.updated_by  # Use updated_by as the user who likely deleted it
    
    if user:
        service = AuditLogService(user=user)
        details = f"Task for {instance.maintenance_log.title}"
        
        service.log_action(
            action='delete',
            model_name='MaintenanceTask',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_save, sender=EquipmentDocument)
def log_equipment_document_save(sender, instance, created, **kwargs):
    """Log equipment document creation/update."""
    action = 'create' if created else 'update'
    user = instance.created_by if created else instance.updated_by
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action=action,
            model_name='EquipmentDocument',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_delete, sender=EquipmentDocument)
def log_equipment_document_delete(sender, instance, **kwargs):
    """Log equipment document deletion."""
    user = instance.updated_by  # Use updated_by as the user who likely deleted it
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action='delete',
            model_name='EquipmentDocument',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_save, sender=MaintenancePlan)
def log_maintenance_plan_save(sender, instance, created, **kwargs):
    """Log maintenance plan creation/update."""
    action = 'create' if created else 'update'
    user = instance.created_by if created else instance.updated_by
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action=action,
            model_name='MaintenancePlan',
            object_id=str(instance.id),
            details=details
        )


@receiver(post_delete, sender=MaintenancePlan)
def log_maintenance_plan_delete(sender, instance, **kwargs):
    """Log maintenance plan deletion."""
    user = instance.updated_by  # Use updated_by as the user who likely deleted it
    
    if user:
        service = AuditLogService(user=user)
        details = f"{instance.title} for {instance.equipment.code}"
        
        service.log_action(
            action='delete',
            model_name='MaintenancePlan',
            object_id=str(instance.id),
            details=details
        ) 