from django.shortcuts import render, HttpResponse, redirect


def index(request):
    user_id = request.session.get("user_id", 1)  # TODO: change default id to -1

    return redirect("home" if user_id != -1 else "login")


def home(request):

    return HttpResponse("HOME")


def login(request):

    return HttpResponse("LOGIN")
