import csv
from datetime import date

from django.http import HttpResponse
from django.shortcuts import render

from .access import role_required
from .models import Department, TrainingRecord
from .report_views import _csv_safe


def _label(record, today):
    """Plain-English status for one training record."""
    if record.status == "completed":
        return "Completed"
    if record.due_date and record.due_date < today:
        return "Overdue"
    if record.status == "in_progress":
        return "In progress"
    return "Not started"


@role_required("admin")
def admin_training_completion(request):
    """Report: training assigned to employees and how much of it is finished."""
    status = request.GET.get("status", "")
    department = request.GET.get("department", "")
    today = date.today()

    records = TrainingRecord.objects.select_related(
        "employee", "employee__department", "training"
    )
    if department.isdigit():
        records = records.filter(employee__department_id=int(department))

    rows = []
    for item in records.order_by("employee__name", "training__course_name"):
        rows.append({
            "employee": item.employee.name,
            "department": item.employee.department.name if item.employee.department else "Not assigned",
            "course": item.training.course_name,
            "provider": item.training.provider or "-",
            "due_date": item.due_date,
            "completion_date": item.completion_date,
            "status": _label(item, today),
        })

    total = len(rows)
    completed = sum(r["status"] == "Completed" for r in rows)
    in_progress = sum(r["status"] == "In progress" for r in rows)
    overdue = sum(r["status"] == "Overdue" for r in rows)
    rate = round(completed * 100 / total) if total else 0

    if status in ("Completed", "In progress", "Not started", "Overdue"):
        rows = [r for r in rows if r["status"] == status]

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="training_completion_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Employee", "Department", "Course", "Provider", "Due date", "Completed on", "Status"])
        for r in rows:
            writer.writerow([
                _csv_safe(r["employee"]), _csv_safe(r["department"]),
                _csv_safe(r["course"]), _csv_safe(r["provider"]),
                r["due_date"].strftime("%m/%d/%Y") if r["due_date"] else "",
                r["completion_date"].strftime("%m/%d/%Y") if r["completion_date"] else "",
                r["status"],
            ])
        return response

    keep = request.GET.copy()
    keep.pop("export", None)
    keep["export"] = "csv"

    return render(request, "core/admin_training_completion.html", {
        "rows": rows,
        "total": total,
        "completed_count": completed,
        "in_progress_count": in_progress,
        "overdue_count": overdue,
        "rate": rate,
        "departments": Department.objects.order_by("name"),
        "status": status,
        "department": department,
        "export_query": keep.urlencode(),
    })