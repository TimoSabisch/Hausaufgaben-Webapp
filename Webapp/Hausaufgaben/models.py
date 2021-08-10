from django.db import models


class Entry(models.Model):
    title = models.CharField(max_length=50)
    note = models.CharField(max_length=255)
    date = models.DateField()
    owner = models.IntegerField()

    class EntryType(models.enums.IntegerChoices):
        TASK = 0
        REMINDER = 1
        TEST = 2

    type = models.IntegerField(choices=EntryType, default=EntryType.TASK)


class Group(models.Model):
    class Role(models.enums.IntegerChoices):
        MEMBER = 0
        ADMIN = 1
