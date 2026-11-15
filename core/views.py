
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from .models import (
    Employee,
    JobRoleSkill,
    JobRoleCertification,
    Training,
)


def redirect_by_role(user):
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
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
                messages.error(
                    request,
                    'Employee profile is not set up.'
                )
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

    skills = employee.employee_skills.select_related(
        'skill'
    ).all()

    role_skills = {}

    if employee.job_role:
        role_skills = {
            item.skill_id: item.is_required
            for item in employee.job_role.required_skills.all()
        }

    for item in skills:
        item.is_required_for_role = role_skills.get(item.skill_id)

    return render(request, 'core/employee_skills.html', {
        'employee': employee,
        'skills': skills
    })


@login_required
def employee_skills_gap(request):

    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    skill_gaps = []
    certification_gaps = []

    employee_skills = {
        item.skill_id: item
        for item in employee.employee_skills.select_related(
            'skill'
        ).all()
    }

    if employee.job_role:

        required_skills = JobRoleSkill.objects.filter(
            job_role=employee.job_role,
            is_required=True
        ).select_related('skill')

        for requirement in required_skills:

            current_skill = employee_skills.get(
                requirement.skill_id
            )

            if current_skill is None:
                status = 'Missing'
                current_level = None

            elif current_skill.proficiency < requirement.required_level:
                status = 'Below requirement'
                current_level = current_skill.get_proficiency_display()

            else:
                status = 'Meets requirement'
                current_level = current_skill.get_proficiency_display()

            skill_gaps.append({
                'skill': requirement.skill,
                'current_level': current_level,
                'required_level': requirement.get_required_level_display(),
                'status': status,
            })

        employee_certifications = {
            item.certification_id: item
            for item in employee.certifications.select_related(
                'certification'
            ).all()
        }

        required_certifications = JobRoleCertification.objects.filter(
            job_role=employee.job_role,
            is_required=True
        ).select_related('certification')

        for requirement in required_certifications:

            current_certification = employee_certifications.get(
                requirement.certification_id
            )

            if current_certification is None:
                status = 'Missing'

            else:
                status = current_certification.status

            certification_gaps.append({
                'certification': requirement.certification,
                'status': status,
                'expiration_date': (
                    current_certification.expiration_date
                    if current_certification else None
                ),
            })

    development_goals = employee.development_goals.select_related(
        'skill'
    ).all().order_by('target_date')

    context = {
        'employee': employee,
        'skill_gaps': skill_gaps,
        'certification_gaps': certification_gaps,
        'development_goals': development_goals,

        'total_skills': len(skill_gaps),

        'missing_skills': sum(
            item['status'] == 'Missing'
            for item in skill_gaps
        ),

        'below_requirement': sum(
            item['status'] == 'Below requirement'
            for item in skill_gaps
        ),

        'meeting_requirements': sum(
            item['status'] == 'Meets requirement'
            for item in skill_gaps
        ),

        'missing_certifications': sum(
            item['status'] == 'Missing'
            for item in certification_gaps
        ),

        'expiring_certifications': sum(
            item['status'] == 'Expiring soon'
            for item in certification_gaps
        ),

        'expired_certifications': sum(
            item['status'] == 'Expired'
            for item in certification_gaps
        ),
    }

    return render(
        request,
        'core/employee_skills_gap.html',
        context
    )


@login_required
def employee_certifications(request):

    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    certifications = list(
        employee.certifications.select_related(
            'certification'
        ).all()
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
        'active_count': sum(
            item.status == 'Active'
            for item in certifications
        ),
        'expiring_count': sum(
            item.status == 'Expiring soon'
            for item in certifications
        ),
        'expired_count': sum(
            item.status == 'Expired'
            for item in certifications
        ),
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
def employee_development(request):

    if request.user.employee_profile.role != 'employee':
        return redirect_by_role(request.user)

    employee = request.user.employee_profile

    development_goals = employee.development_goals.select_related(
        'skill'
    ).all().order_by('target_date')

    if request.method == 'POST':

        for goal in development_goals:

            date_value = request.POST.get(
                f'target_date_{goal.id}'
            )

            goal.target_date = (
                parse_date(date_value)
                if date_value else None
            )

            goal.save(update_fields=['target_date'])

        messages.success(
            request,
            'Development goals updated successfully.'
        )

        return redirect('employee_development')

    completed_training_ids = employee.training_records.filter(
        status='completed'
    ).values_list('training_id', flat=True)

    for goal in development_goals:

        goal.recommended_training = Training.objects.filter(
            related_skill=goal.skill
        ).exclude(
            id__in=completed_training_ids
        ).distinct()

    context = {
        'employee': employee,
        'development_goals': development_goals,
    }

    return render(
        request,
        'core/developmental_goals.html',
        context
    )


@login_required
def manager_dashboard(request):

    if request.user.employee_profile.role != 'manager':
        return redirect_by_role(request.user)

    return HttpResponse("Manager Dashboard - Coming Soon")


@login_required
def admin_dashboard(request):

    if request.user.employee_profile.role != 'admin':
        return redirect_by_role(request.user)

    from .models import Department, JobRole, Skill

    context = {
        'total_employees': Employee.objects.count(),
        'total_departments': Department.objects.count(),
        'total_job_roles': JobRole.objects.count(),
        'total_skills': Skill.objects.count(),
    }

    return render(
        request,
        'core/admin_dashboard.html',
        context
    )
@login_required
def admin_reports(request):
    if request.user.employee_profile.role != "admin":
        return redirect_by_role(request.user)

    employees = (
        Employee.objects
        .filter(status="active", job_role__isnull=False)
        .select_related("department", "job_role")
        .prefetch_related(
            "employee_skills__skill",
            "job_role__required_skills__skill"
        )
        .order_by("department__name", "name")
    )

    report_rows = []

    total_gaps = 0
    employees_with_gaps = set()
    employees_evaluated = employees.count()

    for employee in employees:
        current_skills = {
            employee_skill.skill_id: employee_skill
            for employee_skill in employee.employee_skills.all()
        }

        for requirement in employee.job_role.required_skills.all():
            if not requirement.is_required:
                continue

            employee_skill = current_skills.get(requirement.skill_id)

            if employee_skill is None:
                current_level = "Not recorded"
                result = "Missing Skill"
                total_gaps += 1
                employees_with_gaps.add(employee.id)

            else:
                current_level = employee_skill.get_proficiency_display()

                if employee_skill.proficiency < requirement.required_level:
                    result = "Below Required Level"
                    total_gaps += 1
                    employees_with_gaps.add(employee.id)
                else:
                    result = "Meets Requirement"

            report_rows.append({
                "employee": employee.name,
                "department": employee.department.name if employee.department else "Not assigned",
                "job_role": employee.job_role.title,
                "skill": requirement.skill.name,
                "current_level": current_level,
                "required_level": requirement.get_required_level_display(),
                "result": result,
            })

    context = {
        "report_rows": report_rows,
        "employees_evaluated": employees_evaluated,
        "total_gaps": total_gaps,
        "employees_with_gaps": len(employees_with_gaps),
    }

    return render(request, "core/admin_reports.html", context)
