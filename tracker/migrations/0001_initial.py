# Hand-written to match tracker/models.py (Django was not available to run
# makemigrations). Run `python manage.py makemigrations --check` after setup;
# if it reports changes, delete this file and regenerate it.
import django.core.validators
import django.db.models.deletion
import django.db.models.functions.comparison
from decimal import Decimal

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("type", models.CharField(choices=[("income", "Income"), ("expense", "Expense")], max_length=7)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categories", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name_plural": "categories",
                "ordering": ["type", "name"],
                "constraints": [
                    models.UniqueConstraint(fields=("user", "name", "type"), name="unique_category_per_user_name_type"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("type", models.CharField(choices=[("income", "Income"), ("expense", "Expense")], max_length=7)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("date", models.DateField()),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="tracker.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date", "-id"],
                "indexes": [models.Index(fields=["user", "date"], name="txn_user_date_idx")],
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="transaction_amount_positive"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("month", models.DateField(help_text="Always the first day of the month.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to="tracker.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-month", "category"],
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="budget_amount_positive"),
                    models.UniqueConstraint(
                        models.F("user"),
                        django.db.models.functions.comparison.Coalesce(models.F("category"), models.Value(0)),
                        models.F("month"),
                        name="unique_budget_per_user_category_month",
                    ),
                ],
            },
        ),
    ]
