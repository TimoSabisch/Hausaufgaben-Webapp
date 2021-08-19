from django.shortcuts import loader, HttpResponse, redirect, HttpResponseRedirect
from django.urls import reverse
import django.contrib.auth as auth
import json
from .models import Group, Entry
from enum import Enum

DEFAULT_USER_ID = 1  # TODO: change to -1


class Views(Enum):
    WEEK_VIEW = 0
    ENTRY_VIEW = 1
    DAY_VIEW = 2


def entry_type_to_str(entry_type):
    if entry_type == 0:
        return "Aufgabe"
    elif entry_type == 1:
        return "Erinnerung"
    elif entry_type == 2:
        return "Test"
    return "Unknown"


def get_menu_context(request, group):
    user = request.user

    groups = user.group_set.all()

    context = {
        "groups": groups if len(groups) != 0 else None,
        "username": user.username,
        "currently_viewed": request.session.get("currently_viewed", group if groups.filter(id=group) else 0)
    }

    return context


def get_view_data(request, group):
    user = request.user

    entries = []

    if group != 0:
        if Group.objects.filter(id=group):
            for entry in Group.objects.get(id=group).entries.all():
                entries.append({
                    "id": entry.id,
                    "title": entry.title,
                    "note": entry.note,
                    "date": entry.date.isoformat(),
                    "type": entry_type_to_str(entry.type),
                    "done": user.id in entry.done_by,
                    "creator": {
                        "id": entry.owner.id,
                        "username": entry.owner.username
                    }
                })
    else:
        for entry in user.entry_privat_set.all():
            entries.append({
                "id": entry.id,
                "title": entry.title,
                "note": entry.note,
                "date": entry.date.isoformat(),
                "type": entry_type_to_str(entry.type),
                "done": user.id in entry.done_by,
                "creator": {
                    "id": entry.owner.id,
                    "username": entry.owner.username
                }
            })

    context = {
        "entries": entries,
        "user": user.id,
        "weekview_week": request.session.get("weekview_week", 0),
        "weekview_year": request.session.get("weekview_year", 0)
    }

    return context


# Views
def index(request):

    return redirect("home" if request.user.is_authenticated else "login")


def home(request):

    return redirect("login" if not request.user.is_authenticated else f"weekview")


def week_view(request, group=0):
    if not request.user.is_authenticated:
        return redirect("login")

    http_redirect = False
    user = request.user
    if request.method == "POST":
        if request.POST["type"] == "changeEntryDone":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            if user.id in entry.done_by:
                entry.done_by.remove(user.id)
            else:
                entry.done_by.append(user.id)
            entry.save()

            request.session["weekview_week"] = request.POST["cur_week"]
            request.session["weekview_year"] = request.POST["cur_year"]
            http_redirect = True

    template = loader.get_template("Hausaufgaben/week_view.html")

    context = {
        "view": "weekview"
    }
    context.update(get_menu_context(request, group))
    context["view_data"] = json.dumps(get_view_data(request, group))

    if http_redirect:
        return HttpResponseRedirect(reverse("weekview", args=(context["currently_viewed"],)))
    else:
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
