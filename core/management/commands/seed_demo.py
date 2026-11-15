"""Fill the database with SIMULATED demo data (the RFP does not allow real employee data).

Run:  python manage.py seed_demo
Safe to run more than once: it skips anything that already exists.
All demo accounts share the password below. Never use this on a real deployment.
"""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import (
    Certification, Department, DevelopmentGoal, Employee, EmployeeCertification,
    EmployeeSkill, JobRole, JobRoleCertification, JobRoleSkill, Skill, Training,
    TrainingRecord,
)

DEMO_PASSWORD = "Demo!2026"

DEPARTMENTS = ["Security", "Cloud", "Network", "PMO", "Human Resources"]

# role title -> (department, [(skill, required level 1-3)], [required certifications])
ROLES = {
    "Security Analyst": ("Security", [("Network Security", 3), ("Incident Response", 2), ("Python", 2)], ["CompTIA Security+"]),
    "Cloud Engineer": ("Cloud", [("AWS", 3), ("Python", 2), ("Linux", 2)], ["AWS Cloud Practitioner"]),
    "Network Administrator": ("Network", [("Network Security", 2), ("Linux", 2), ("Cisco Routing", 3)], ["Cisco CCNA"]),
    "Project Manager": ("PMO", [("Project Planning", 3), ("Communication", 3)], ["PMP"]),
    "HR Specialist": ("Human Resources", [("Communication", 3), ("Data Analysis", 2)], []),
}

CERTS = {
    "CompTIA Security+": "CompTIA", "AWS Cloud Practitioner": "Amazon", "Cisco CCNA": "Cisco",
    "PMP": "PMI", "CISSP": "ISC2",
}

# username, full name, role title, portal role, manager username
PEOPLE = [
    ("adm.lee", "Jordan Lee", "HR Specialist", "admin", None),
    ("mgr.cole", "Taylor Cole", "Security Analyst", "manager", None),
    ("mgr.ortiz", "Casey Ortiz", "Cloud Engineer", "manager", None),
    ("alex.rivera", "Alex Rivera", "Security Analyst", "employee", "mgr.cole"),
    ("maya.chen", "Maya Chen", "Cloud Engineer", "employee", "mgr.ortiz"),
    ("priya.shah", "Priya Shah", "Project Manager", "employee", "mgr.ortiz"),
    ("sam.carter", "Sam Carter", "Network Administrator", "employee", "mgr.cole"),
    ("dana.brooks", "Dana Brooks", "Security Analyst", "employee", "mgr.cole"),
    ("riley.nguyen", "Riley Nguyen", "Cloud Engineer", "employee", "mgr.ortiz"),
    ("jamie.patel", "Jamie Patel", "HR Specialist", "employee", "mgr.ortiz"),
    ("morgan.reyes", "Morgan Reyes", "Network Administrator", "employee", "mgr.cole"),
]

# username -> [(skill, level)]
SKILLS = {
    "alex.rivera": [("Network Security", 3), ("Incident Response", 1), ("Python", 2)],
    "maya.chen": [("AWS", 2), ("Python", 3), ("Linux", 2)],
    "priya.shah": [("Project Planning", 3), ("Communication", 2)],
    "sam.carter": [("Network Security", 2), ("Linux", 1)],
    "dana.brooks": [("Network Security", 3), ("Incident Response", 2), ("Python", 1)],
    "riley.nguyen": [("AWS", 3), ("Python", 2)],
    "jamie.patel": [("Communication", 3), ("Data Analysis", 1)],
    "morgan.reyes": [("Network Security", 2), ("Linux", 2), ("Cisco Routing", 3)],
}

# username -> [(certification, earned days ago, expires in N days (negative = already expired))]
CERT_RECORDS = {
    "alex.rivera": [("CompTIA Security+", 950, 1095 - 950)],
    "maya.chen": [("AWS Cloud Practitioner", 1250, 20)],
    "priya.shah": [("PMP", 1400, 55)],
    "sam.carter": [("Cisco CCNA", 2000, -40)],
    "dana.brooks": [("CompTIA Security+", 200, 900), ("CISSP", 160, 1000)],
    "riley.nguyen": [("AWS Cloud Practitioner", 100, 600)],
    "morgan.reyes": [("Cisco CCNA", 1000, 80)],
}

TRAININGS = [
    ("Incident Response Fundamentals", "Incident Response", "SANS Institute", "online", 16, 0),
    ("Python for Security Automation", "Python", "Coursera", "online", 20, 49),
    ("AWS Solutions Workshop", "AWS", "Amazon Training", "hybrid", 24, 0),
    ("Linux Administration Basics", "Linux", "Linux Foundation", "online", 30, 99),
    ("Data Analysis with Excel and SQL", "Data Analysis", "LinkedIn Learning", "online", 12, 0),
    ("Leading Effective Teams", "Communication", "Dale Carnegie", "in_person", 16, 300),
]

TODAY = date.today()


class Command(BaseCommand):
    help = "Create simulated demo data (departments, roles, skills, employees, certifications, training)."

    def handle(self, *args, **options):
        depts = {n: Department.objects.get_or_create(name=n)[0] for n in DEPARTMENTS}
        certs = {n: Certification.objects.get_or_create(name=n, defaults={"issuer": i})[0] for n, i in CERTS.items()}

        skills = {}
        for _, (_, req_skills, _) in ROLES.items():
            for name, _ in req_skills:
                skills.setdefault(name, Skill.objects.get_or_create(name=name)[0])
        for name in {s for lst in SKILLS.values() for s, _ in lst}:
            skills.setdefault(name, Skill.objects.get_or_create(name=name)[0])

        roles = {}
        for title, (dept, req_skills, req_certs) in ROLES.items():
            role = roles[title] = JobRole.objects.get_or_create(title=title, defaults={"department": depts[dept]})[0]
            for name, level in req_skills:
                JobRoleSkill.objects.get_or_create(job_role=role, skill=skills[name], defaults={"required_level": level})
            for c in req_certs:
                JobRoleCertification.objects.get_or_create(job_role=role, certification=certs[c])

        people = {}
        next_id = 1001
        for username, name, title, portal_role, _ in PEOPLE:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(DEMO_PASSWORD)
                user.first_name, user.last_name = name.split(" ", 1)
                user.save()
            role = roles[title]
            people[username] = Employee.objects.get_or_create(
                user=user,
                defaults={"name": name, "department": role.department, "job_role": role,
                          "role": portal_role, "status": "active", "employee_id": next_id},
            )[0]
            next_id += 1
        for username, _, _, _, mgr in PEOPLE:
            if mgr and people[username].manager_id is None:
                people[username].manager = people[mgr]
                people[username].save()

        for username, lst in SKILLS.items():
            for sk, level in lst:
                EmployeeSkill.objects.get_or_create(employee=people[username], skill=skills[sk], defaults={"proficiency": level})

        for username, lst in CERT_RECORDS.items():
            for cert, earned_ago, expires_in in lst:
                EmployeeCertification.objects.get_or_create(
                    employee=people[username], certification=certs[cert],
                    defaults={"date_earned": TODAY - timedelta(days=earned_ago),
                              "expiration_date": TODAY + timedelta(days=expires_in)},
                )

        trainings = {}
        for course, skill, provider, method, hours, cost in TRAININGS:
            trainings[course] = Training.objects.get_or_create(
                course_name=course,
                defaults={"related_skill": skills[skill], "provider": provider,
                          "delivery_method": method, "duration_hours": hours, "cost": cost},
            )[0]

        records = [
            ("alex.rivera", "Incident Response Fundamentals", "in_progress", 30, None),
            ("dana.brooks", "Python for Security Automation", "completed", -10, -20),
            ("maya.chen", "AWS Solutions Workshop", "not_started", 45, None),
            ("sam.carter", "Linux Administration Basics", "not_started", 20, None),
            ("jamie.patel", "Data Analysis with Excel and SQL", "in_progress", 25, None),
        ]
        for username, course, status, due_in, done_ago in records:
            TrainingRecord.objects.get_or_create(
                employee=people[username], training=trainings[course],
                defaults={"status": status, "due_date": TODAY + timedelta(days=due_in),
                          "completion_date": TODAY + timedelta(days=done_ago) if done_ago is not None else None},
            )

        for username, skill, status, due_in in [
            ("alex.rivera", "Incident Response", "in_progress", 60),
            ("sam.carter", "Linux", "not_started", 90),
            ("jamie.patel", "Data Analysis", "in_progress", 45),
        ]:
            DevelopmentGoal.objects.get_or_create(
                employee=people[username], skill=skills[skill],
                defaults={"status": status, "target_date": TODAY + timedelta(days=due_in)},
            )

        self.stdout.write(self.style.SUCCESS("Simulated demo data is ready."))
        self.stdout.write(f"Demo password for every account: {DEMO_PASSWORD}")
        self.stdout.write("Admin: adm.lee | Managers: mgr.cole, mgr.ortiz | Employees: alex.rivera, maya.chen, ...")