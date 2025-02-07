FROM python:3.9 AS builder

ENV PYTHONUNBUFFERED=1

WORKDIR /AlumniProject

COPY . /AlumniProject

RUN python -m venv env
RUN . env/bin/activate
RUN python -m pip install --upgrade pip
RUN python -m pip install Django requests

EXPOSE 8000

CMD ["python", "AlumniProject/manage.py", "runserver", "0.0.0.0:8000", "--settings=AlumniProject.settings.dev"]
