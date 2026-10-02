from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from .models import Category, Transaction

User = get_user_model()


class CategoryCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("alice", password="Str0ng-pass-123")
        cls.other_user = User.objects.create_user("bob", password="Str0ng-pass-123")
        cls.category = Category.objects.create(user=cls.user, name="Food", type="expense")
        cls.other_category = Category.objects.create(
            user=cls.other_user, name="Secret", type="expense"
        )

    def setUp(self):
        self.client.force_login(self.user)

    # --- list ---
    def test_list_shows_only_own_categories(self):
        response = self.client.get(reverse("tracker:category_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food")
        self.assertNotContains(response, "Secret")

    # --- create ---
    def test_create_category(self):
        response = self.client.post(
            reverse("tracker:category_create"), {"name": "Salary", "type": "income"}
        )
        self.assertRedirects(response, reverse("tracker:category_list"))
        created = Category.objects.get(name="Salary")
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.type, "income")

    def test_create_duplicate_is_rejected(self):
        response = self.client.post(
            reverse("tracker:category_create"), {"name": "food", "type": "expense"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.filter(user=self.user).count(), 1)

    def test_create_with_invalid_type_is_rejected(self):
        response = self.client.post(
            reverse("tracker:category_create"), {"name": "X", "type": "other"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.filter(name="X").exists())

    # --- update ---
    def test_update_category(self):
        response = self.client.post(
            reverse("tracker:category_update", args=[self.category.pk]),
            {"name": "Groceries", "type": "expense"},
        )
        self.assertRedirects(response, reverse("tracker:category_list"))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Groceries")

    def test_cannot_change_type_when_category_has_transactions(self):
        Transaction.objects.create(
            user=self.user, category=self.category, type="expense",
            amount=Decimal("10.00"), date=date(2026, 1, 1),
        )
        response = self.client.post(
            reverse("tracker:category_update", args=[self.category.pk]),
            {"name": "Food", "type": "income"},
        )
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.type, "expense")

    # --- delete ---
    def test_delete_category(self):
        response = self.client.post(
            reverse("tracker:category_delete", args=[self.category.pk])
        )
        self.assertRedirects(response, reverse("tracker:category_list"))
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_cannot_delete_category_with_transactions(self):
        Transaction.objects.create(
            user=self.user, category=self.category, type="expense",
            amount=Decimal("10.00"), date=date(2026, 1, 1),
        )
        response = self.client.post(
            reverse("tracker:category_delete", args=[self.category.pk])
        )
        self.assertRedirects(response, reverse("tracker:category_list"))
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    # --- ownership ---
    def test_user_cannot_access_another_users_category(self):
        edit_url = reverse("tracker:category_update", args=[self.other_category.pk])
        delete_url = reverse("tracker:category_delete", args=[self.other_category.pk])

        self.assertEqual(self.client.get(edit_url).status_code, 404)
        self.assertEqual(self.client.get(delete_url).status_code, 404)
        self.assertEqual(
            self.client.post(edit_url, {"name": "Hacked", "type": "expense"}).status_code,
            404,
        )
        self.assertEqual(self.client.post(delete_url).status_code, 404)

        self.other_category.refresh_from_db()
        self.assertEqual(self.other_category.name, "Secret")


class CategoryLoginRequiredTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        user = User.objects.create_user("carol", password="Str0ng-pass-123")
        category = Category.objects.create(user=user, name="Food", type="expense")
        urls = [
            reverse("tracker:category_list"),
            reverse("tracker:category_create"),
            reverse("tracker:category_update", args=[category.pk]),
            reverse("tracker:category_delete", args=[category.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{resolve_url(settings.LOGIN_URL)}?next={url}",
                    fetch_redirect_response=False,
                )
