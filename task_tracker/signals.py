from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from .context import get_current_request
from .models import AuditLog, Task

def _get_actor():
    req = get_current_request()
    if req and hasattr(req, 'user') and req.user.is_authenticated:
        return req.user
    return None

@receiver(pre_save, sender=Task)
def cache_task_old_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Task.objects.only('status', 'priority', 'deadline', 'assignee_id').get(pk=instance.pk)
            instance._old_state = {
                'status': old.status,
                'priority': old.priority,
                'deadline': old.deadline.isoformat() if old.deadline else None,
                'assignee_id': str(old.assignee_id) if old.assignee_id else None
            }
        except Task.DoesNotExist:
            instance._old_state = None
    else:
        instance._old_state = None

@receiver(post_save, sender=Task)
def audit_task_save(sender, instance, created, **kwargs):
    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    new_data = {
        'status': instance.status,
        'priority': instance.priority,
        'deadline': instance.deadline.isoformat() if instance.deadline else None,
        'assignee_id': str(instance.assignee_id) if instance.assignee_id else None
    }
    old_data = getattr(instance, '_old_state', None) if not created else None

    # Пропускаем лог, если изменения незначительны (например, только updated_at)
    if not created and old_data == new_data:
        return

    AuditLog.objects.create(
        entity_table='task',
        entity_id=instance.id,
        action=action,
        old_data=old_data,
        new_data=new_data,
        actor=_get_actor()
    )

@receiver(post_delete, sender=Task)
def audit_task_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        entity_table='task',
        entity_id=instance.id,
        action=AuditLog.Action.DELETE,
        new_data={'deleted_at': 'true'},
        actor=_get_actor()
    )