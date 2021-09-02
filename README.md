# Hausaufgaben-Webapp

Die **Hausaufgaben-Webapp** ist wie der name es schon sagt ein Digitales *Hausaufgabenheft*.

In der Webapp kann man ganz einfach Einträge erstellen und ansehen. Außerdem kann man auch Gruppen erstellen und diese auch Verwalten (Mitglieder hinzufügen/entfernen). Wenn du Mitglied einer Gruppe bist, siehst du alle Einträge, die in dieser Gruppe erstellt wurden.

Es gibt auch mehrere Ansichten:

- Wochen-Ansicht
- Eintrags-Ansicht
- Tages-Ansicht

## Installation mit Docker

Als Erstes musst du das Projekt herunterladen:
```shell
git pull https://github.com/TimoSabisch/Hausaufgaben-Webapp
```

Der Server muss jetzt noch konfiguriert werden. Dafür musst du die `_env` datei, in `.env` umbenennen
und die Variablen darin anpassen.

Mit einem `*` markierte Variablen sollten geändert werden (zumindest bei der production).
Mit zwei `*` markierte Variablen müssen geändert werden.
```dotenv
MYSQL_ROOT_PASSWORD=*ROOTPWD                # Das Admin-Passwort der Datenbank
MYSQL_PASSWORD=*DJANGOPWD                   # Das Passwort für den Datenbank zugriff vom Server
MYSQL_HOST=mysql                            # Der name des MySQL container. Standar 'mysql'
HOST_FQDN=**WEBSITE                         # Die URL der Website
DJANGO_SETTINGS_MODULE=Webapp.settings_prod # Django Settings-Modul (Dev='Webapp.settings', Production='Webapp.settings_prod')
```

Jetzt muss der Container noch gebaut werden:
```shell
docker-compose build
```

Und jetzt müssen die Container nur noch gestartet werden:
```shell
docker-compose up
```

Der Server ist jetzt erreichbar.

### Server Aktualisieren

Um den Server zu aktualisieren, musst du folgendes machen:

Den Server stoppen:
```shell
docker-compose down   # Den server Stoppen
git pull              # Neue/Geänderte Dateien laden
docker-compose build  # Den Container bauen
docker-compose up     # Den Server wieder Starten
```
