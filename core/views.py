
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

    employee = request.user.employee_profile

    return render(request, 'core/employee_dashboard.html', {
        'employee': employee
    })

@login_required
def employee_profile(request):
    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    return render(request, 'core/employee_profile.html', {
        'employee': employee
    })
@login_required
def employee_skills(request):
    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    skills = employee.employee_skills.select_related('skill').all()

    role_skills = {}

    if employee.job_role:
        role_skills = {
            role_skill.skill_id: role_skill.is_required
            for role_skill in employee.job_role.required_skills.all()
        }

    for item in skills:
        item.is_required_for_role = role_skills.get(item.skill_id)

    return render(request, 'core/employee_skills.html', {
        'employee': employee,
        'skills': skills
    })

@login_required
def employee_certifications(request):
    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    certifications = list(
        employee.certifications.select_related('certification').all()
    )

    role_certifications = {}

    if employee.job_role:
        role_certifications = {
            item.certification_id: item.is_required
            for item in employee.job_role.required_certifications.all()
        }

    for item in certifications:
        item.is_required_for_role = role_certifications.get(
            item.certification_id
        )

    return render(request, 'core/employee_certifications.html', {
        'employee': employee,
        'certifications': certifications,

        'total_count': len(certifications),
        'active_count': sum(item.status == 'Active' for item in certifications),
        'expiring_count': sum(item.status == 'Expiring soon' for item in certifications),
        'expired_count': sum(item.status == 'Expired' for item in certifications),
    })

@login_required
def employee_training(request):
    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    training_records = employee.training_records.select_related(
        'training',
        'training__related_skill',
        'training__related_certification'
    ).all().order_by('due_date')

    return render(request, 'core/employee_training.html', {
        'employee': employee,
        'training_records': training_records,
    })
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
