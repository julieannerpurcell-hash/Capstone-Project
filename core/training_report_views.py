from datetime import date

from django.db.models import Q
from django.shortcuts import render

from .access import role_required
from .models import Department, TrainingRecord, DevelopmentGoal


def _label(record, today):
    """Plain-English status for one training record."""
    if record.status == "completed":
        return "Completed"
    if record.due_date and record.due_date < today:
        return "Overdue"
    if record.status == "in_progress":
        return "In Progress"
    return "Not Started"


@role_required("admin")
def admin_training_completion(request):
    """Report: training completion and employee development goals."""

    status = request.GET.get("status", "")
    department = request.GET.get("department", "")
    search = request.GET.get("search", "").strip()
    today = date.today()

    records = TrainingRecord.objects.select_related(
        "employee",
        "employee__department",
        "training"
    )

    # Department filter
    if department.isdigit():
        records = records.filter(
            employee__department_id=int(department)
        )

    # Search by employee name or training course
    if search:
        records = records.filter(
            Q(employee__name__icontains=search) |
            Q(training__course_name__icontains=search)
        )

    rows = []

    for item in records.order_by(
        "employee__name",
        "training__course_name"
    ):
        rows.append({
            "employee": item.employee.name,
            "department": (
                item.employee.department.name
                if item.employee.department else "Not assigned"
            ),
            "course": item.training.course_name,
            "provider": item.training.provider or "-",
            "due_date": item.due_date,
            "completion_date": item.completion_date,
            "status": _label(item, today),
        })

    # Status filter
    if status in ("Completed", "In Progress", "Not Started", "Overdue"):
        rows = [r for r in rows if r["status"] == status]

    total = len(rows)
    completed = sum(r["status"] == "Completed" for r in rows)
    in_progress = sum(r["status"] == "In Progress" for r in rows)
    overdue = sum(r["status"] == "Overdue" for r in rows)

    rate = round(completed * 100 / total) if total else 0

    # Professional Development Goals
    goals = DevelopmentGoal.objects.select_related(
        "employee",
        "employee__department",
        "skill"
    ).order_by("employee__name", "target_date")

    if department.isdigit():
        goals = goals.filter(
            employee__department_id=int(department)
        )

    return render(request, "core/admin_training_completion.html", {
        "rows": rows,
        "goals": goals,
        "total": total,
        "completed_count": completed,
        "in_progress_count": in_progress,
        "overdue_count": overdue,
        "rate": rate,
        "departments": Department.objects.order_by("name"),
        "status": status,
        "department": department,
        "search": search,
    })