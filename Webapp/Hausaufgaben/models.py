from django.db import models
from django_mysql import models as mysql
from django.utils.translation import gettext_lazy as _


class Entry(models.Model):
    title = models.CharField(max_length=50)
    note = models.TextField()
    date = models.DateField()
    owner = models.IntegerField()
    done_by = mysql.ListCharField(base_field=models.IntegerField(),
                                  size=50,
                                  max_length=(50*8),
                                  default=[],
                                  blank=True)

    class EntryType(models.IntegerChoices):
        TASK = 0, _("Task")
        REMINDER = 1, _("Reminder")
        TEST = 2, _("Test")

        __empty__ = _('(Unknown)')

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

        __empty__ = _('(Unknown)')

    admins = mysql.ListCharField(base_field=models.IntegerField(),
                                 size=50,
                                 max_length=(50*8),
                                 default=[],
                                 blank=True)
    members = mysql.ListCharField(base_field=models.IntegerField(),
                                  size=50,
                                  max_length=(50*8),
                                  default=[],
                                  blank=True)
    entries = mysql.ListCharField(base_field=models.IntegerField(),
                                  size=50,
                                  max_length=(50*8),
                                  default=[],
                                  blank=True)

    def add_member(self, user_id: int, admin: bool = False):
        if admin:
            self.admins.append(user_id)
        else:
            self.members.append(user_id)

    def remove_member(self, user_id: int):
        if user_id in self.admins:
            self.admins.remove(user_id)
        elif user_id in self.members:
            self.admins.remove(user_id)

    def add_entry(self, entry_id: int):
        if entry_id not in self.entries:
            self.entries.append(entry_id)

    def remove_entry(self, entry_id: int):
        if entry_id in self.entries:
            self.entries.remove(entry_id)

    def set_role(self, user_id: int, role: Role):
        if role == self.Role.ADMIN and user_id in self.members:
            self.admins.append(user_id)
            self.members.remove(user_id)
        elif role == self.Role.MEMBER and user_id in self.admins:
            self.members.append(user_id)
            self.admins.remove(user_id)

    def get_role(self, user_id: int):
        if user_id in self.admins:
            return self.Role.ADMIN
        elif user_id in self.members:
            return self.Role.MEMBER
        else:
            return self.Role.__empty__

    def __str__(self):
        return self.title
