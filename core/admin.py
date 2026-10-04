from django.contrib import admin
from .models import (
    Department, JobRole, Employee, Skill, EmployeeSkill,
    JobRoleSkill, Certification, EmployeeCertification,
    Training, TrainingRecord, DevelopmentGoal,
)

admin.site.register(Department)
admin.site.register(JobRole)
admin.site.register(Employee)
admin.site.register(Skill)
admin.site.register(EmployeeSkill)
admin.site.register(JobRoleSkill)
admin.site.register(Certification)
admin.site.register(EmployeeCertification)
admin.site.register(Training)
admin.site.register(TrainingRecord)
admin.site.register(DevelopmentGoal)