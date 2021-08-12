from django.contrib import admin

from .models import Group, Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note', 'date', 'owner')


admin.site.register(Group)
admin.site.register(Entry, EntryAdmin)
