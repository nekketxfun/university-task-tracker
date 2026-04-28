from rest_framework import serializers
from django.utils import timezone
from models import (Department, CustomUser, Role, ProcessTemplate,
                    TemplateStep, Task, Resource, TaskResource,
                    AuditLog, Report)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head_name', 'created_at']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'description']

class CustomUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'position', 'department', 'department_name', 'is_active']

class TemplateStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateStep
        fields = ['id', 'step_order', 'title', 'description', 'default_deadline_days', 'required_role_slug']

class ProcessTemplateSerializer(serializers.ModelSerializer):
    steps = TemplateStepSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ProcessTemplate
        fields = ['id', 'name', 'description', 'department', 'department_name',
                  'created_by', 'created_by_name', 'is_active', 'created_at', 'steps']

class TaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    template_step_title = serializers.CharField(source='template_step.title', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline',
                  'creator', 'creator_name', 'assignee', 'assignee_name',
                  'department', 'department_name', 'template_step', 'template_step_title',
                  'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at', 'completed_at',
                            'creator_name', 'assignee_name', 'department_name', 'template_step_title']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creator'] = request.user
        if not validated_data.get('department') and getattr(request.user, 'department', None):
            validated_data['department'] = request.user.department
        return super().create(validated_data)

class ResourceSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'location', 'capacity', 'status', 'department', 'department_name']

class TaskResourceSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    resource_name = serializers.CharField(source='resource.name', read_only=True)

    class Meta:
        model = TaskResource
        fields = ['id', 'task', 'task_title', 'resource', 'resource_name', 'reserved_qty', 'start_time', 'end_time']

    def validate(self, data):
        overlapping = TaskResource.objects.filter(
            resource=data['resource'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exists()
        if overlapping:
            raise serializers.ValidationError("Ресурс уже забронирован на указанное время.")
        return data

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.full_name', read_only=True)
    class Meta:
        model = AuditLog
        fields = ['id', 'entity_table', 'entity_id', 'action', 'old_data', 'new_data', 'actor_name', 'timestamp']
        read_only_fields = fields

class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    class Meta:
        model = Report
        fields = ['id', 'title', 'report_type', 'filters', 'file_path', 'status', 'generated_by', 'generated_by_name', 'generated_at']
        read_only_fields = ['id', 'status', 'generated_by', 'generated_at', 'generated_by_name', 'generated_at']