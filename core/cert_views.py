from datetime import date, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .access import role_required
from .forms import EmployeeCertificationForm
from .models import Certification, Department, EmployeeCertification

SOON_DAYS = EmployeeCertification.EXPIRING_SOON_DAYS
PAGE_SIZE = 10


def _status_q(status):
    """Same rules as EmployeeCertification.status, but usable in a database query."""
    today = date.today()
    soon = today + timedelta(days=SOON_DAYS)
    if status == "Expired":
        return Q(expiration_date__lt=today)
    if status == "Expiring soon":
        return Q(expiration_date__gte=today, expiration_date__lte=soon)
    if status == "Active":
        return Q(expiration_date__isnull=True) | Q(expiration_date__gt=soon)
    return Q()


@role_required("admin")
def admin_certifications(request):
    everything = EmployeeCertification.objects.all()

    q = request.GET.get("q", "").strip()
    department = request.GET.get("department", "")
    status = request.GET.get("status", "")
    certification = request.GET.get("certification", "")

    records = everything.select_related("employee", "employee__department", "certification")
    if q:
        records = records.filter(
            Q(employee__name__icontains=q)
            | Q(certification__name__icontains=q)
            | Q(certification__issuer__icontains=q)
        )
    if department.isdigit():
        records = records.filter(employee__department_id=int(department))
    if certification.isdigit():
        records = records.filter(certification_id=int(certification))
    if status in ("Active", "Expiring soon", "Expired"):
        records = records.filter(_status_q(status))
    records = records.order_by("expiration_date", "employee__name")

    page = Paginator(records, PAGE_SIZE).get_page(request.GET.get("page"))

    keep = request.GET.copy()
    keep.pop("page", None)

    return render(request, "core/admin_certifications.html", {
        "page": page,
        "total_count": everything.count(),
        "active_count": everything.filter(_status_q("Active")).count(),
        "expiring_count": everything.filter(_status_q("Expiring soon")).count(),
        "expired_count": everything.filter(_status_q("Expired")).count(),
        "soon_days": SOON_DAYS,
        "departments": Department.objects.order_by("name"),
        "certifications": Certification.objects.order_by("name"),
        "q": q,
        "department": department,
        "status": status,
        "certification": certification,
        "querystring": keep.urlencode(),
    })


@role_required("admin")
def admin_certification_add(request):
    form = EmployeeCertificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        record = form.save()
        messages.success(request, f"Added {record.certification} for {record.employee}.")
        return redirect("admin_certifications")
    return render(request, "core/admin_certification_form.html", {"form": form, "mode": "Add"})


@role_required("admin")
def admin_certification_edit(request, pk):
    record = get_object_or_404(EmployeeCertification, pk=pk)
    form = EmployeeCertificationForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Updated {record.certification} for {record.employee}.")
        return redirect("admin_certifications")
    return render(request, "core/admin_certification_form.html", {"form": form, "mode": "Edit"})


@role_required("admin")
def admin_certification_delete(request, pk):
    record = get_object_or_404(EmployeeCertification, pk=pk)
    if request.method == "POST":
        label = f"{record.certification} for {record.employee}"
        record.delete()
        messages.success(request, f"Deleted {label}.")
        return redirect("admin_certifications")
    return render(request, "core/admin_certification_confirm_delete.html", {"record": record})