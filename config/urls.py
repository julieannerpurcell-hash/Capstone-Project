from django.contrib import admin
from django.urls import path
from core import views, cert_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/', admin.site.urls),

    path('logout/', views.logout_view, name='logout'),

    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/profile/', views.employee_profile, name='employee_profile'),
    path('employee/skills/', views.employee_skills, name='employee_skills'),
    path('employee/skills-gap/', views.employee_skills_gap, name='employee_skills_gap'),
    path('employee/certifications/', views.employee_certifications, name='employee_certifications'),
    path('employee/training/',views.employee_training, name='employee_training'),
    path('employee/development/', views.employee_development, name='employee_development'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('administrator/', views.admin_dashboard, name='admin_dashboard'),
    path('administrator/reports/', views.admin_reports, name='admin_reports'),
        path('administrator/certifications/', cert_views.admin_certifications, name='admin_certifications'),
    path('administrator/certifications/add/', cert_views.admin_certification_add, name='admin_certification_add'),
    path('administrator/certifications/<int:pk>/edit/', cert_views.admin_certification_edit, name='admin_certification_edit'),
    path('administrator/certifications/<int:pk>/delete/', cert_views.admin_certification_delete, name='admin_certification_delete'),
]
