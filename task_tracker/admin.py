from django.contrib import admin
from .models import Department, CustomUser, Task, ProcessTemplate

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_name')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'department', 'is_active')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'deadline', 'assignee')
    list_filter = ('status', 'priority', 'department')

@admin.register(ProcessTemplate)
class ProcessTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'is_active')