"""Database models: Category, Transaction, Budget.

All money values use DecimalField (never float). Currency is INR.
Cross-field rules live in clean(); Django admin and ModelForms call clean()
automatically. Plain .save() does NOT call clean(), so later milestones must
validate in forms/serializers (or call full_clean()) before saving.
"""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Value
from django.db.models.functions import Coalesce


class TransactionType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=TransactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"], name="unique_category_per_user_name_type"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    # PROTECT: a category that still has transactions cannot be deleted.
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="transactions"
    )
    type = models.CharField(max_length=7, choices=TransactionType.choices)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [models.Index(fields=["user", "date"], name="txn_user_date_idx")]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0), name="transaction_amount_positive"
            ),
        ]

    def __str__(self):
        return f"{self.get_type_display()} ₹{self.amount} on {self.date}"

    def clean(self):
        super().clean()
        if self.category_id is None:
            return
        errors = {}
        if self.user_id is not None and self.category.user_id != self.user_id:
            errors["category"] = "This category belongs to another user."
        elif self.type and self.category.type != self.type:
            errors["category"] = "Category type must match the transaction type."
        if errors:
            raise ValidationError(errors)


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets"
    )
    # NULL category = the overall monthly budget.
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    month = models.DateField(help_text="Always the first day of the month.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month", "category"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0), name="budget_amount_positive"
            ),
            # Treat "no category" as 0 so NULLs compare as equal. Category ids
            # start at 1, so 0 never clashes with a real category.
            # This gives: one overall budget per user/month AND one budget per
            # user/category/month. See docs/database.md.
            models.UniqueConstraint(
                "user",
                Coalesce("category", Value(0)),
                "month",
                name="unique_budget_per_user_category_month",
            ),
        ]

    def __str__(self):
        scope = self.category.name if self.category_id else "Overall"
        return f"{scope} budget {self.month:%Y-%m}: ₹{self.amount}"

    def clean(self):
        super().clean()
        errors = {}
        if self.month and self.month.day != 1:
            errors["month"] = "Month must be the first day of the month."
        if self.category_id is not None:
            if self.user_id is not None and self.category.user_id != self.user_id:
                errors["category"] = "This category belongs to another user."
            elif self.category.type != TransactionType.EXPENSE:
                errors["category"] = "Budgets can only use expense categories."
        if errors:
            raise ValidationError(errors)
