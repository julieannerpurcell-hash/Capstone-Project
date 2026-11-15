from django import forms

from .models import Employee, EmployeeCertification


class EmployeeCertificationForm(forms.ModelForm):
    class Meta:
        model = EmployeeCertification
        fields = ["employee", "certification", "date_earned", "expiration_date"]
        widgets = {
            "date_earned": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "expiration_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
        help_texts = {
            "expiration_date": "Leave blank if this certification never expires.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = Employee.objects.filter(status="active").order_by("name")
        self.fields["certification"].queryset = self.fields["certification"].queryset.order_by("name")

    def clean(self):
        cleaned = super().clean()
        earned = cleaned.get("date_earned")
        expires = cleaned.get("expiration_date")
        if earned and expires and expires < earned:
            self.add_error("expiration_date", "The expiration date cannot be before the date earned.")
        return cleaned