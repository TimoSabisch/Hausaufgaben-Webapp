FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/Webapp

# CMD ["python", "./Webapp/manage.py", "runserver", "0:8000"]
CMD ["bash", "./run.sh"]
