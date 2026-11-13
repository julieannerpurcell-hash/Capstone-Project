from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/', admin.site.urls),

    path('logout/', views.logout_view, name='logout'),

    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/profile/', views.employee_profile, name='employee_profile'),
    path('employee/skills/', views.employee_skills, name='employee_skills'),
    path('employee/certifications/', views.employee_certifications, name='employee_certifications'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('administrator/', views.admin_dashboard, name='admin_dashboard'),
]
