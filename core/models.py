from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class JobRole(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="job_roles")

    def __str__(self):
        return self.title


class Employee(models.Model):
    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("manager", "Manager"),
        ("admin", "Administrator"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name="employees")
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, related_name="employees")
    manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_reports")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="employee_skills")
    proficiency = models.IntegerField()

    class Meta:
        unique_together = ("employee", "skill")

    def __str__(self):
        return f"{self.employee} - {self.skill} ({self.proficiency})"


class JobRoleSkill(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name="required_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="job_roles_requiring")
    required_level = models.IntegerField()

    class Meta:
        unique_together = ("job_role", "skill")

    def __str__(self):
        return f"{self.job_role} needs {self.skill} (level {self.required_level})"


class Certification(models.Model):
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name


class EmployeeCertification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name="employee_certifications")
    date_earned = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.certification}"


class Training(models.Model):
    course_name = models.CharField(max_length=150)
    related_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="trainings")

    def __str__(self):
        return self.course_name


class TrainingRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="training_records")
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="training_records")
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.training}"


class DevelopmentGoal(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("complete", "Complete"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="development_goals")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="development_goals")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")

    def __str__(self):
        return f"{self.employee} goal: {self.skill}"