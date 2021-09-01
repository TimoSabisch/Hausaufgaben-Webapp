FROM python:3.9

RUN set -ex &&\
    DEBIAN_FRONTEND=noninteractive &&\
    apt update &&\
    apt install -y dumb-init &&\
    apt clean &&\
    rm -fr /var/lib/apt/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/Webapp

RUN set -ex &&\
    python -m compileall . &&\
    python manage.py collectstatic

EXPOSE 8000

# CMD ["python", "./Webapp/manage.py", "runserver", "0:8000"]
CMD ["dumb-init", "./run.sh"]
