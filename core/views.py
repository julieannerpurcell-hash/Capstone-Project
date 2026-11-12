
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Employee


def redirect_by_role(user):
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        logout_user = True
        return redirect('login')

    if employee.role == 'employee':
        return redirect('employee_dashboard')

    elif employee.role == 'manager':
        return redirect('manager_dashboard')

    elif employee.role == 'admin':
        return redirect('admin_dashboard')

    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            try:
                employee = user.employee_profile
            except Employee.DoesNotExist:
                messages.error(request, 'Employee profile is not set up.')
                return render(request, 'core/login.html')

            if employee.status != 'active':
                messages.error(request, 'Account is inactive.')
                return render(request, 'core/login.html')

            login(request, user)
            return redirect_by_role(user)

        messages.error(request, 'Invalid username or password')

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect_by_role(request.user)


@login_required
def employee_dashboard(request):
    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)
    return HttpResponse("Employee Dashboard - Coming Soon")


@login_required
def manager_dashboard(request):
    if request.user.employee_profile.role != 'manager':
        return redirect_by_role(request.user)
    return HttpResponse("Manager Dashboard - Coming Soon")


@login_required
def admin_dashboard(request):
    if request.user.employee_profile.role != 'admin':
        return redirect_by_role(request.user)
    return HttpResponse("Administrator Dashboard - Coming Soon")
