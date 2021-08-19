from django.db import models
from django_mysql import models as mysql
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Entry(models.Model):
    title = models.CharField(max_length=50)
    note = models.TextField()
    date = models.DateField()
    owner = models.ForeignKey(User, related_name="entry_owner_set", on_delete=models.CASCADE)
    privat_user = models.ForeignKey(User, related_name="entry_privat_set", on_delete=models.CASCADE, null=True, blank=True)
    done_by = mysql.ListCharField(base_field=models.IntegerField(),
                                  size=50,
                                  max_length=(50*8),
                                  default=[],
                                  blank=True)

    class EntryType(models.IntegerChoices):
        TASK = 0, _("Task")
        REMINDER = 1, _("Reminder")

    type = models.IntegerField(choices=EntryType.choices, default=EntryType.TASK)

    def set_done(self, user_id: int, done: bool):
        if done and user_id not in self.done_by:
            self.done_by.append(user_id)
        elif not done and user_id in self.done_by:
            self.done_by.remove(user_id)

    def get_done(self, user_id):
        return user_id in self.done_by

    def __str__(self):
        return self.title


class Group(models.Model):
    title = models.CharField(max_length=50, default="")

    class Role(models.IntegerChoices):
        MEMBER = 0, _("Member")
        ADMIN = 1, _("Admin")

    admins = mysql.ListCharField(base_field=models.IntegerField(),
                                 size=50,
                                 max_length=(50 * 8),
                                 default=[],
                                 blank=True)
    members = models.ManyToManyField(User)
    entries = models.ManyToManyField(Entry,
                                     blank=True)

    def add_member(self, user: int, admin: bool = False):
        user = User.objects.get(id=user.id)
        if admin:
            self.admins.append(user.id)
        else:
            self.members.add(user)

    def remove_member(self, user: int):
        user = User.objects.get(id=user.id)
        if user.id in self.admins:
            self.admins.remove(user.id)
        elif user.id in self.members:
            self.members.remove(User.objects.get(id=user.id))

    def add_entry(self, entry_id: int):
        if entry_id not in self.entries:
            self.entries.add(Entry.objects.get(id=entry_id))

    def remove_entry(self, entry_id: int):
        if entry_id in self.entries:
            self.entries.remove(Entry.objects.get(id=entry_id))

    def set_role(self, user: int, role: Role):
        user = User.objects.get(id=user.id)
        if role == self.Role.ADMIN and user.id in self.members:
            self.admins.append(user.id)
        elif role == self.Role.MEMBER and user.id in self.admins:
            self.admins.remove(user.id)

    def get_role(self, user: int):
        user = User.objects.get(id=user.id)
        if user in self.members.all():
            if user.id in self.admins:
                return self.Role.ADMIN
            else:
                return self.Role.MEMBER
        else:
            return self.Role.__empty__

    def __str__(self):
        return self.title
