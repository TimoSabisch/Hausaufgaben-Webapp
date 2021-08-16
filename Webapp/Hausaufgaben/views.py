from django.shortcuts import loader, HttpResponse, redirect
import django.contrib.auth as auth
from enum import Enum

DEFAULT_USER_ID = 1  # TODO: change to -1


class Views(Enum):
    WEEK_VIEW = 0
    ENTRY_VIEW = 1
    DAY_VIEW = 2


def get_menu_context(request, group):
    user = request.user

    groups = user.group_set.all()

    context = {
        "groups": groups if len(groups) != 0 else None,
        "username": user.username,
        "currently_viewed": request.session.get("currently_viewed", group if groups.filter(id=group) else 0)
    }

    return context


# Views
def index(request):

    return redirect("home" if request.user.is_authenticated else "login")


def home(request):

    return redirect("login" if not request.user.is_authenticated else f"weekview")


def page_not_found(request):
    return redirect("home")


def week_view(request, group=0):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/week_view.html")

    context = {
        "view": "weekview"
    }
    context.update(get_menu_context(request, group))

    return HttpResponse(template.render(context, request))


def entry_view(request, group=0):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/entry_view.html")

    context = {
        "view": "entryview"
    }
    context.update(get_menu_context(request, group))

    return HttpResponse(template.render(context))


def day_view(request, group=0):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/day_view.html")

    context = {
        "view": "dayview"
    }
    context.update(get_menu_context(request, group))

    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template("Hausaufgaben/login.html")

    # TODO: Add login check

    return HttpResponse(template.render())
