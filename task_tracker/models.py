from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    head_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'department'
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='users')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'role'
        verbose_name = 'Роль'

class ProcessTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='templates')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'process_template'
        verbose_name = 'Шаблон процесса'

class TemplateStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ProcessTemplate, on_delete=models.CASCADE, related_name='steps')
    step_order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    default_deadline_days = models.PositiveIntegerField(default=7)
    required_role_slug = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'template_step'
        ordering = ['template', 'step_order']
        unique_together = ('template', 'step_order')
        verbose_name = 'Этап шаблона'

class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        URGENT = 'urgent', 'Срочный'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    deadline = models.DateTimeField()
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='tasks')
    template_step = models.ForeignKey(TemplateStep, on_delete=models.SET_NULL, null=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'task'
        indexes = [
            models.Index(fields=['status', 'deadline'], name='idx_task_status_deadline'),
            models.Index(fields=['assignee', 'status'], name='idx_task_assignee_status'),
        ]
        verbose_name = 'Задача'

    def save(self, *args, **kwargs):
        if self.status == self.Status.DONE and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class Resource(models.Model):
    class Type(models.TextChoices):
        ROOM = 'room', 'Аудитория'
        EQUIPMENT = 'equipment', 'Оборудование'
        LICENSE = 'license', 'Лицензия ПО'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Доступно'
        MAINTENANCE = 'maintenance', 'На обслуживании'
        DECOMMISSIONED = 'decommissioned', 'Списано'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices)
    location = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='resources')

    class Meta:
        db_table = 'resource'
        verbose_name = 'Ресурс'

class TaskResource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='resource_assignments')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='task_assignments')
    reserved_qty = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = 'task_resource'
        constraints = [
            models.UniqueConstraint(
                fields=['resource', 'start_time', 'end_time'],
                name='unique_resource_reservation'
            )
        ]
        verbose_name = 'Бронирование ресурса'

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Создание'
        UPDATE = 'update', 'Обновление'
        DELETE = 'delete', 'Удаление'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_table = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=20, choices=Action.choices)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        indexes = [models.Index(fields=['entity_table', 'entity_id'])]
        verbose_name = 'Аудит изменений'

class Report(models.Model):
    class Type(models.TextChoices):
        PERFORMANCE = 'performance', 'Отчет по эффективности'
        DEADLINES = 'deadlines', 'Отчет по дедлайнам'
        LOAD = 'load', 'Отчет по нагрузке'

    class Status(models.TextChoices):
        PENDING = 'pending', 'В очереди'
        PROCESSING = 'processing', 'Генерируется'
        COMPLETED = 'completed', 'Готов'
        FAILED = 'failed', 'Ошибка'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=Type.choices)
    filters = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'report'
        verbose_name = 'Отчет'