import csv
import io
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter


from .models import (Department, CustomUser, Role, ProcessTemplate,
                    TemplateStep, Task, Resource, TaskResource,
                    AuditLog, Report)
from .serializers import (DepartmentSerializer, CustomUserSerializer, RoleSerializer,
                         ProcessTemplateSerializer, TemplateStepSerializer,
                         TaskSerializer, ResourceSerializer, TaskResourceSerializer,
                         AuditLogSerializer, ReportSerializer)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'code']

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'is_active']

class ProcessTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProcessTemplate.objects.filter(is_active=True)
    serializer_class = ProcessTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['post'])
    def instantiate(self, request, pk=None):
        """Разворачивает задачи из шаблона (ключевая фича оптимизации)"""
        template = self.get_object()
        created_tasks = []
        base_date = timezone.now()
        for step in template.steps.all():
            deadline = base_date + timezone.timedelta(days=step.default_deadline_days)
            task = Task.objects.create(
                title=f"{template.name} - {step.title}",
                description=step.description,
                deadline=deadline,
                creator=request.user,
                department=template.department,
                template_step=step,
                status=Task.Status.NEW
            )
            created_tasks.append(task.id)
            base_date = deadline
        return Response({'status': 'created', 'task_ids': created_tasks}, status=status.HTTP_201_CREATED)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'department']
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'priority', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.select_related('creator', 'assignee', 'department').all()
        return Task.objects.select_related('creator', 'assignee', 'department').filter(
            assignee=user
        ) | Task.objects.filter(creator=user)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Экспорт задач в CSV с учётом фильтров пользователя"""
        tasks = self.filter_queryset(self.get_queryset())[:5000]  # Лимит безопасности
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="tasks_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Название', 'Статус', 'Приоритет', 'Дедлайн', 'Исполнитель', 'Подразделение'])
        for t in tasks:
            writer.writerow([
                t.id, t.title, t.get_status_display(), t.get_priority_display(),
                t.deadline.strftime('%Y-%m-%d %H:%M') if t.deadline else '',
                t.assignee.full_name if t.assignee else '—',
                t.department.name if t.department else '—'
            ])
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def import_csv(self, request):
        """Импорт задач из CSV. Пропускает пустые строки, логирует ошибки"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'detail': 'Файл не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = file_obj.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(content))
            created, errors = 0, []

            for idx, row in enumerate(reader, start=2):
                try:
                    title = row.get('Название') or row.get('title')
                    if not title: raise ValueError("Отсутствует поле 'Название'")

                    deadline_str = row.get('Дедлайн') or row.get('deadline')
                    deadline = timezone.datetime.strptime(deadline_str, '%Y-%m-%d %H:%M') if deadline_str else None

                    Task.objects.create(
                        title=title,
                        status=row.get('Статус', Task.Status.NEW),
                        priority=row.get('Приоритет', Task.Priority.MEDIUM),
                        deadline=deadline,
                        creator=request.user,
                        department=request.user.department
                    )
                    created += 1
                except Exception as e:
                    errors.append(f"Строка {idx}: {str(e)}")

            return Response({
                'created': created,
                'errors_count': len(errors),
                'first_errors': errors[:5]
            }, status=status.HTTP_201_CREATED)
        except UnicodeDecodeError:
            return Response({'detail': 'Неверная кодировка файла. Требуется UTF-8'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'status', 'department']

class TaskResourceViewSet(viewsets.ModelViewSet):
    queryset = TaskResource.objects.select_related('task', 'resource').all()
    serializer_class = TaskResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['entity_table', 'action']
    ordering_fields = ['timestamp']

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]