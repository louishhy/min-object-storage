FROM python:3.9

WORKDIR /flaskapi

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app" ]