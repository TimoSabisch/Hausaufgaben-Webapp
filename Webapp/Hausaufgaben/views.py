from django.shortcuts import loader, HttpResponse, redirect
from django.contrib.auth import login, logout
from enum import Enum

DEFAULT_USER_ID = 1  # TODO: change to -1

class Views(Enum):
    WEEK_VIEW = 0
    ENTRY_VIEW = 1
    DAY_VIEW = 2


def index(request):

    return redirect("home" if request.user.is_authenticated else "login")


def home(request):

    return redirect("login" if request.user.is_authenticated else "weekview")


def week_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/week_view.html")

    groups = user.group_set.all()
    context = {
        "groups": groups if len(groups) != 0 else None,
        "username": user.username
    }

    return HttpResponse(template.render(context))


def entry_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/entry_view.html")

    groups = user.group_set.all()
    context = {
        "groups": groups if len(groups) != 0 else None,
        "username": user.username
    }

    return HttpResponse(template.render(context))


def day_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    template = loader.get_template("Hausaufgaben/day_view.html")

    groups = user.group_set.all()
    context = {
        "groups": groups if len(groups) != 0 else None,
        "username": user.username
    }

    return HttpResponse(template.render(context))


def login(request):
    template = loader.get_template("Hausaufgaben/login.html")

    # TODO: Add login check

    return HttpResponse(template.render())
