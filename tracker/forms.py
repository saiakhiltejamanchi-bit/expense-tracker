from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")
        category_type = cleaned_data.get("type")

        if not name or not category_type or not self.user:
            return cleaned_data

        # Remove unnecessary spaces from the category name.
        name = name.strip()
        cleaned_data["name"] = name

        # Check for duplicate category for this user,
        # ignoring upper/lower-case differences.
        duplicate_exists = Category.objects.filter(
            user=self.user,
            name__iexact=name,
            type=category_type,
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if duplicate_exists:
            raise forms.ValidationError(
                "You already have a category with this name and type."
            )

        # Prevent changing the category type when
        # the category already has transactions.
        if self.instance.pk:
            old_type = self.instance.type

            if old_type != category_type and self.instance.transactions.exists():
                raise forms.ValidationError(
                    "You cannot change the category type because this category "
                    "already has transactions."
                )

        return cleaned_data

    def save(self, commit=True):
        category = super().save(commit=False)
        category.user = self.user

        if commit:
            category.save()

        return category