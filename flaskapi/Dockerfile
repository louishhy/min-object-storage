FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache -r requirements.txt

COPY . .

CMD [ "gunicorn", "--config", "gunicorn.conf.py", "wsgi:app" ]