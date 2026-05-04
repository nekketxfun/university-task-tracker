from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Task, CustomUser, ProcessTemplate, Resource, AuditLog, Report

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=identifier, password=password)

        if not user and '@' in identifier:
            try:
                user_obj = CustomUser.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

        if user:
            if not user.is_active:
                messages.error(request, 'Учётная запись заблокирована')
            else:
                login(request, user)
                return redirect('task_list')
        else:
            messages.error(request, 'Неверный логин/email или пароль')

    return render(request, 'login.html')

@login_required
def task_list_view(request):
    tasks = Task.objects.select_related('assignee', 'department').order_by('-created_at')
    paginator = Paginator(tasks, 20)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    return render(request, 'tasks/list.html', {'page_obj': page_obj})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    tasks = Task.objects.filter(assignee=request.user) | Task.objects.filter(department=request.user.department)
    ctx = {
        'total_tasks': tasks.count(),
        'on_time_tasks': tasks.filter(status='done').count(),
        'overdue_tasks': tasks.filter(status__in=['new','in_progress'], deadline__lt=timezone.now()).count(),
        'active_processes': ProcessTemplate.objects.filter(is_active=True).count(),
        'recent_tasks': tasks.order_by('-created_at')[:5]
    }
    return render(request, 'dashboard.html', ctx)

@login_required
def task_detail_view(request, pk):
    task = Task.objects.get(pk=pk)
    logs = AuditLog.objects.filter(entity_table='task', entity_id=pk).order_by('-timestamp')[:10]
    return render(request, 'tasks/detail.html', {'task': task, 'audit_logs': logs, 'task_statuses': Task.Status.choices})

@login_required
def template_list_view(request):
    return render(request, 'templates_list.html', {'templates': ProcessTemplate.objects.filter(is_active=True)})

@login_required
def resource_list_view(request):
    return render(request, 'resources/list.html', {'resources': Resource.objects.all()})

@login_required
def audit_list_view(request):
    logs = AuditLog.objects.select_related('actor').order_by('-timestamp')
    p = Paginator(logs, 20)
    return render(request, 'audit/list.html', {'page_obj': p.get_page(request.GET.get('page')), 'users': CustomUser.objects.all()})

@login_required
def report_list_view(request):
    return render(request, 'reports/list.html', {'reports': Report.objects.order_by('-generated_at')[:10]})