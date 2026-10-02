from django.contrib import admin

from .models import Budget, Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user", "created_at")
    list_filter = ("type",)
    search_fields = ("name", "user__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "amount", "category", "user")
    list_filter = ("type", "date")
    search_fields = ("description", "user__username", "category__name")
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("month", "category", "amount", "user")
    list_filter = ("month",)
    search_fields = ("user__username", "category__name")
