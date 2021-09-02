from django.shortcuts import loader, HttpResponse, redirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import django.contrib.auth as auth
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import datetime
from .models import Group, Entry
from enum import Enum


class Views(Enum):
    WEEK_VIEW = 0
    ENTRY_VIEW = 1
    DAY_VIEW = 2


def entry_type_to_str(entry_type):
    if entry_type == 0:
        return "Aufgabe"
    elif entry_type == 1:
        return "Erinnerung"
    return "Unknown"


def get_menu_context(request, group):
    user = request.user

    groups = user.group_set.all()

    group_info = []
    for group_ in groups:
        group_info.append({
            "id": group_.id,
            "title": group_.title,
            "members": [
                {
                    "id": member.id,
                    "username": member.username,
                    "role": group_.get_role(member)
                } for member in group_.members.all()
            ]
        })

    context = {
        "groups": groups if len(groups) != 0 else None,
        "group_info": json.dumps(group_info),
        "username": user.username,
        "userid": user.id,
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
@csrf_exempt
def index(request):

    if request.user.is_authenticated and request.method == "POST":
        user = request.user

        if request.POST["type"] == "getGroupData":
            groups = user.group_set.all()

            group_info = []
            for group_ in groups:
                group_info.append({
                    "id": group_.id,
                    "title": group_.title,
                    "members": [
                        {
                            "id": member.id,
                            "username": member.username,
                            "role": group_.get_role(member)
                        } for member in group_.members.all()
                    ]
                })
            data = {
                "groups": group_info
            }

            return JsonResponse(data, safe=True)
        elif request.POST["type"] == "createGroup":
            group_name = request.POST["groupName"]

            group_ = Group(title=group_name, admins=[user.id])
            group_.save()
            group_.members.add(user)
            group_.save()

            return JsonResponse({"value": "success"}, safe=True)
        elif request.POST["type"] == "deleteGroup":
            group_ = request.POST["groupId"]
            group_ = Group.objects.get(id=group_)
            if user.id in group_.admins:
                group_.delete()

            return JsonResponse({"value": "success"}, safe=True)
        elif request.POST["type"] == "groupAddMember":
            group_ = request.POST["groupId"]
            username = request.POST["username"]
            group_ = Group.objects.get(id=group_)

            if User.objects.filter(username=username):
                group_.add_member(User.objects.get(username=username))
                group_.save()
            else:
                return JsonResponse({"value": "failed", "message": "invalid username"}, safe=True)

            return JsonResponse({"value": "success"}, safe=True)

    return redirect("home" if request.user.is_authenticated else "login")


def home(request):

    return redirect("login" if not request.user.is_authenticated else f"weekview")


@csrf_exempt
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
        elif request.POST["type"] == "editEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            date = datetime.datetime.strptime(date, "%Y-%m-%d")

            entry.title = title
            entry.note = note
            entry.date = date
            if entry_type == "1":
                entry.type = entry.EntryType.TASK
            elif entry_type == "2":
                entry.type = entry.EntryType.REMINDER
            entry.save()
            request.session["weekview_week"] = request.POST["cur_week"]
            request.session["weekview_year"] = request.POST["cur_year"]
            http_redirect = True
        elif request.POST["type"] == "deleteEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            entry.delete()

            request.session["weekview_week"] = request.POST["cur_week"]
            request.session["weekview_year"] = request.POST["cur_year"]
            http_redirect = True
        elif request.POST["type"] == "createEntry":
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            if title and date and entry_type:

                date = datetime.datetime.strptime(date, "%Y-%m-%d")

                if entry_type == "1":
                    entry_type = Entry.EntryType.TASK
                elif entry_type == "2":
                    entry_type = Entry.EntryType.REMINDER

                entry = Entry(title=title, note=note, date=date, owner=user, type=entry_type)
                entry.save()

                if group == 0:
                    entry.privat_user = user
                    entry.save()
                else:
                    Group.objects.get(id=group).add_entry(entry)

                http_redirect = True
            else:
                http_redirect = True
        elif request.POST["type"] == "createGroup":
            group_name = request.POST["groupName"]

            group_ = Group(title=group_name, admins=[user.id])
            group_.save()
            group_.members.add(user)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "addUser":
            username = request.POST["username"]
            group_id = int(request.POST["group"])

            if User.objects.filter(username=username) and group_id != -1:
                group_ = Group.objects.get(id=group_id)
                group_.add_member(User.objects.get(username=username))
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "leaveGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=int(group_))
            group_.remove_member(user)
            group_.save()

            if len(group_.members.all()) == 0:
                group_.delete()
            elif len(group_.admins) == 0:
                group_.set_role(group_.members.all()[0], group_.Role.ADMIN)
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "setAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.ADMIN)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "removeAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.MEMBER)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "kickUser":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.remove_member(user_)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "deleteGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=group_)
            if user.id in group_.admins:
                group_.delete()

            http_redirect = True

    elif request.method == "GET":
        request.session["weekview_week"] = 0
        request.session["weekview_year"] = 0

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


@csrf_exempt
def entry_view(request, group=0):
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

            http_redirect = True
        elif request.POST["type"] == "editEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            date = datetime.datetime.strptime(date, "%Y-%m-%d")

            entry.title = title
            entry.note = note
            entry.date = date
            if entry_type == "1":
                entry.type = entry.EntryType.TASK
            elif entry_type == "2":
                entry.type = entry.EntryType.REMINDER
            entry.save()

            http_redirect = True
        elif request.POST["type"] == "deleteEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            entry.delete()

            http_redirect = True
        elif request.POST["type"] == "createEntry":
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            if title and date and entry_type:

                date = datetime.datetime.strptime(date, "%Y-%m-%d")

                if entry_type == "1":
                    entry_type = Entry.EntryType.TASK
                elif entry_type == "2":
                    entry_type = Entry.EntryType.REMINDER

                entry = Entry(title=title, note=note, date=date, owner=user, type=entry_type)
                entry.save()

                if group == 0:
                    entry.privat_user = user
                    entry.save()
                else:
                    Group.objects.get(id=group).add_entry(entry)

                http_redirect = True
            else:
                http_redirect = True
        elif request.POST["type"] == "createGroup":
            group_name = request.POST["groupName"]

            group_ = Group(title=group_name, admins=[user.id])
            group_.save()
            group_.members.add(user)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "addUser":
            username = request.POST["username"]
            group_id = int(request.POST["group"])

            if User.objects.filter(username=username) and group_id != -1:
                group_ = Group.objects.get(id=group_id)
                group_.add_member(User.objects.get(username=username))
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "leaveGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=int(group_))
            group_.remove_member(user)
            group_.save()

            if len(group_.members.all()) == 0:
                group_.delete()
            elif len(group_.admins) == 0:
                group_.set_role(group_.members.all()[0], group_.Role.ADMIN)
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "setAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.ADMIN)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "removeAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.MEMBER)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "kickUser":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.remove_member(user_)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "deleteGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=group_)
            if user.id in group_.admins:
                group_.delete()

            http_redirect = True

    template = loader.get_template("Hausaufgaben/entry_view.html")
    context = {
        "view": "entryview"
    }
    context.update(get_menu_context(request, group))
    context["view_data"] = json.dumps(get_view_data(request, group))

    if http_redirect:
        return HttpResponseRedirect(reverse("entryview", args=(context["currently_viewed"],)))
    else:
        return HttpResponse(template.render(context, request))


@csrf_exempt
def day_view(request, group=0):
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

            http_redirect = True
        elif request.POST["type"] == "editEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            date = datetime.datetime.strptime(date, "%Y-%m-%d")

            entry.title = title
            entry.note = note
            entry.date = date
            if entry_type == "1":
                entry.type = entry.EntryType.TASK
            elif entry_type == "2":
                entry.type = entry.EntryType.REMINDER
            entry.save()

            http_redirect = True
        elif request.POST["type"] == "deleteEntry":
            entry = request.POST["entry"]
            entry = Entry.objects.get(id=entry)
            entry.delete()

            http_redirect = True
        elif request.POST["type"] == "createEntry":
            title = request.POST["title"]
            note = request.POST["note"]
            date = request.POST["date"]
            entry_type = request.POST["entryType"]

            if title and date and entry_type:

                date = datetime.datetime.strptime(date, "%Y-%m-%d")

                if entry_type == "1":
                    entry_type = Entry.EntryType.TASK
                elif entry_type == "2":
                    entry_type = Entry.EntryType.REMINDER

                entry = Entry(title=title, note=note, date=date, owner=user, type=entry_type)
                entry.save()

                if group == 0:
                    entry.privat_user = user
                    entry.save()
                else:
                    Group.objects.get(id=group).add_entry(entry)

                http_redirect = True
            else:
                http_redirect = True
        elif request.POST["type"] == "createGroup":
            group_name = request.POST["groupName"]

            group_ = Group(title=group_name, admins=[user.id])
            group_.save()
            group_.members.add(user)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "addUser":
            username = request.POST["username"]
            group_id = int(request.POST["group"])

            if User.objects.filter(username=username) and group_id != -1:
                group_ = Group.objects.get(id=group_id)
                group_.add_member(User.objects.get(username=username))
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "leaveGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=int(group_))
            group_.remove_member(user)
            group_.save()

            if len(group_.members.all()) == 0:
                group_.delete()
            elif len(group_.admins) == 0:
                group_.set_role(group_.members.all()[0], group_.Role.ADMIN)
                group_.save()

            http_redirect = True
        elif request.POST["type"] == "setAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.ADMIN)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "removeAdmin":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.set_role(user_, group_.Role.MEMBER)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "kickUser":
            group_ = request.POST["group"]
            userid = request.POST["user"]
            group_ = Group.objects.get(id=group_)
            user_ = User.objects.get(id=userid)
            group_.remove_member(user_)
            group_.save()

            http_redirect = True
        elif request.POST["type"] == "deleteGroup":
            group_ = request.POST["group"]
            group_ = Group.objects.get(id=group_)
            if user.id in group_.admins:
                group_.delete()

            http_redirect = True

    template = loader.get_template("Hausaufgaben/day_view.html")
    context = {
        "view": "dayview"
    }
    context.update(get_menu_context(request, group))
    context["view_data"] = json.dumps(get_view_data(request, group))

    if http_redirect:
        return HttpResponseRedirect(reverse("dayview", args=(context["currently_viewed"],)))
    else:
        return HttpResponse(template.render(context, request))


@csrf_exempt
def login(request):
    template = loader.get_template("Hausaufgaben/login.html")

    if request.user.is_authenticated:
        return redirect("home")

    context = {
        "error": 0,
        "user": ""
    }

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect(reverse("weekview", args=(0,)))
            else:
                context["error"] = 1
                context["user"] = username
        else:
            context["error"] = 2
            context["user"] = username

    return HttpResponse(template.render(context))


def logout(request):

    if not request.user.is_authenticated:
        return redirect("login")

    auth.logout(request)
    return redirect("login")


@csrf_exempt
def register(request):
    template = loader.get_template("Hausaufgaben/register.html")

    if request.user.is_authenticated:
        return redirect("home")

    context = {
        "error": 0,
        "user": ""
    }

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            if not User.objects.filter(username=username):
                user = User.objects.create_user(username=username, password=password)
                auth.login(request, user)

                return HttpResponseRedirect(reverse("weekview", args=(0,)))
            else:
                context["error"] = 1
                context["user"] = username
        else:
            context["error"] = 2
            context["user"] = username

    return HttpResponse(template.render(context))
