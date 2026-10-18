import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ("core", "0001_initial"),
    ]
 
    operations = [
        migrations.AddField(
            model_name="jobrole",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="jobroleskill",
            name="is_required",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="skill",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="skill",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="training",
            name="cost",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="training",
            name="delivery_method",
            field=models.CharField(
                choices=[
                    ("online", "Online"),
                    ("in_person", "In person"),
                    ("hybrid", "Hybrid"),
                ],
                default="online",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="training",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="training",
            name="duration_hours",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="training",
            name="provider",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="training",
            name="related_certification",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trainings",
                to="core.certification",
            ),
        ),
        migrations.AlterField(
            model_name="employeeskill",
            name="proficiency",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="jobroleskill",
            name="required_level",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4),
                ]
            ),
        ),
    ]
 
