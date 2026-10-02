from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm
from .models import Category


def home(request):
    """Placeholder page that proves URL -> view -> template works."""
    return render(request, "tracker/home.html")


def get_user_category_or_404(request, pk):
    """Only ever look categories up through the logged-in user."""
    return get_object_or_404(Category, pk=pk, user=request.user)


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, "tracker/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' was created.")
            return redirect("tracker:category_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm(user=request.user)

    return render(
        request,
        "tracker/category_form.html",
        {"form": form, "title": "Add category"},
    )


@login_required
def category_update(request, pk):
    category = get_user_category_or_404(request, pk)

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            instance=category,
            user=request.user,
        )
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' was updated.")
            return redirect("tracker:category_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm(
            instance=category,
            user=request.user,
        )

    return render(
        request,
        "tracker/category_form.html",
        {"form": form, "title": "Edit category"},
    )


@login_required
def category_delete(request, pk):
    category = get_user_category_or_404(request, pk)

    if request.method == "POST":
        name = category.name

        try:
            category.delete()
        except ProtectedError:
            messages.error(
                request,
                f"'{name}' cannot be deleted because it still has transactions.",
            )
        else:
            messages.success(request, f"Category '{name}' was deleted.")

        return redirect("tracker:category_list")

    return render(
        request,
        "tracker/category_confirm_delete.html",
        {"category": category},
    )