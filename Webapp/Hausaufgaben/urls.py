from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('weekview', views.week_view, name='weekview'),
    path('entryview', views.entry_view, name='entryview'),
    path('dayview', views.day_view, name='dayview'),
    path('login', views.login, name='login'),
]
