# Hausaufgaben-Webapp

Die **Hausaufgaben-Webapp** ist wie der name es schon sagt ein Digitales *Hausaufgabenheft*.

In der Webapp kann man ganz einfach Einträge erstellen und ansehen. Außerdem kann man auch Gruppen erstellen und diese auch Verwalten (Mitglieder hinzufügen/entfernen). Wenn du Mitglied einer Gruppe bist, siehst du alle Einträge, die in dieser Gruppe erstellt wurden.

Es gibt auch mehrere Ansichten:

- Wochen-Ansicht
- Eintrags-Ansicht
- Tages-Ansicht

## Installation
### Datenbank verbinden

#### WICHTIG: die Datenbank muss eine MySQL datenbank sein.

In der Datei `./Webapp/Webapp/settings.py` unter `Databases.default` deine Datenbank-Informationen eintragen.

Dass sollte dann ungefähr so aussehen:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'datenbank',
        'USER': 'admin',
        'PASSWORD': 'passwort123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Jetzt muss der Server nur noch gestartet werden. Dafür musst du in dem `Webapp` Ordner in dem die `manage.py` datei ist folgenden befehl ausführen:
```shell
python manage.py runserver
```
