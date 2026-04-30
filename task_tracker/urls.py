from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, RoleViewSet, CustomUserViewSet,
    ProcessTemplateViewSet, TaskViewSet, ResourceViewSet,
    TaskResourceViewSet, AuditLogViewSet, ReportViewSet
)

router = DefaultRouter()

router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'templates', ProcessTemplateViewSet, basename='template')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'task-resources', TaskResourceViewSet, basename='taskresource')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]