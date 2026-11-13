from django.contrib import admin
from .models import (
    Department,
    JobRole,
    Employee,
    Skill,
    EmployeeSkill,
    JobRoleSkill,
    Certification,
    JobRoleCertification,
    EmployeeCertification,
    Training,
    TrainingRecord,
    DevelopmentGoal,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ("title", "department")
    list_filter = ("department",)
    search_fields = ("title",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "job_role", "manager", "role", "status")
    list_filter = ("department", "role", "status")
    search_fields = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ("employee", "skill", "proficiency")
    list_filter = ("proficiency", "skill")


@admin.register(JobRoleSkill)
class JobRoleSkillAdmin(admin.ModelAdmin):
    list_display = ("job_role", "skill", "required_level", "is_required")
    list_filter = ("is_required", "required_level")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer")
    search_fields = ("name", "issuer")


@admin.register(JobRoleCertification)
class JobRoleCertificationAdmin(admin.ModelAdmin):
    list_display = ("job_role", "certification", "is_required")
    list_filter = ("is_required",)


@admin.register(EmployeeCertification)
class EmployeeCertificationAdmin(admin.ModelAdmin):
    list_display = ("employee", "certification", "date_earned", "expiration_date", "status")
    list_filter = ("certification",)


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ("course_name", "provider", "delivery_method", "related_skill")
    list_filter = ("delivery_method",)
    search_fields = ("course_name", "provider")


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "training", "completion_date")


@admin.register(DevelopmentGoal)
class DevelopmentGoalAdmin(admin.ModelAdmin):
    list_display = ("employee", "skill", "status")
    list_filter = ("status",)
