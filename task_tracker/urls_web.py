from django.urls import path
from . import views_web

urlpatterns = [
    path('login/', views_web.login_view, name='login'),
    path('logout/', views_web.logout_view, name='logout'),
    path('dashboard/', views_web.dashboard_view, name='dashboard'),
    path('tasks/', views_web.task_list_view, name='task_list'),
    path('tasks/<uuid:pk>/', views_web.task_detail_view, name='task_detail'),
    path('templates/', views_web.template_list_view, name='template_list'),
    path('resources/', views_web.resource_list_view, name='resource_list'),
    path('audit/', views_web.audit_list_view, name='audit_list'),
    path('reports/', views_web.report_list_view, name='report_list'),
]