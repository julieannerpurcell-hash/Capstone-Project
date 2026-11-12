from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/', admin.site.urls),

    path('logout/', views.logout_view, name='logout'),

    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('administrator/', views.admin_dashboard, name='admin_dashboard'),
]
