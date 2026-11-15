import csv
from datetime import date

from django.http import HttpResponse
from django.shortcuts import render

from .access import role_required
from .cert_views import _status_q
from .models import Department, EmployeeCertification


def _csv_safe(value):
    """Stop spreadsheet programs from running text that starts with = + - or @ as a formula."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


@role_required("admin")
def admin_certification_expiration(request):
    """Report: certifications that are expired or expiring soon, with days left."""
    status = request.GET.get("status", "")
    department = request.GET.get("department", "")

    records = (
        EmployeeCertification.objects
        .filter(_status_q("Expired") | _status_q("Expiring soon"))
        .select_related("employee", "employee__department", "certification")
    )
    if department.isdigit():
        records = records.filter(employee__department_id=int(department))

    all_rows = list(records.order_by("expiration_date", "employee__name"))
    today = date.today()
    rows = []
    for item in all_rows:
        days_left = (item.expiration_date - today).days
        rows.append({
            "employee": item.employee.name,
            "department": item.employee.department.name if item.employee.department else "Not assigned",
            "certification": item.certification.name,
            "issuer": item.certification.issuer or "-",
            "expires": item.expiration_date,
            "days_left": days_left,
            "status": item.status,
        })

    expired = sum(r["status"] == "Expired" for r in rows)
    within_30 = sum(r["status"] == "Expiring soon" and r["days_left"] <= 30 for r in rows)
    within_90 = sum(r["status"] == "Expiring soon" and r["days_left"] > 30 for r in rows)

    if status in ("Expired", "Expiring soon"):
        rows = [r for r in rows if r["status"] == status]

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="certification_expiration_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Employee", "Department", "Certification", "Issuer", "Expires", "Days left", "Status"])
        for r in rows:
            writer.writerow([_csv_safe(r["employee"]), _csv_safe(r["department"]),
                             _csv_safe(r["certification"]), _csv_safe(r["issuer"]),
                             r["expires"].strftime("%m/%d/%Y"), r["days_left"], r["status"]])
        return response

    keep = request.GET.copy()
    keep.pop("export", None)
    keep["export"] = "csv"

    return render(request, "core/admin_certification_expiration.html", {
        "rows": rows,
        "expired_count": expired,
        "within_30_count": within_30,
        "within_90_count": within_90,
        "departments": Department.objects.order_by("name"),
        "status": status,
        "department": department,
        "export_query": keep.urlencode(),
    })