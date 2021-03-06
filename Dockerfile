FROM python:3.6.6

# Generate Polish locale
RUN apt-get update && apt-get install -y locales
RUN echo pl_PL.UTF-8 UTF-8 >> /etc/locale.gen && locale-gen

COPY . /fail2ban-stats
WORKDIR /fail2ban-stats
RUN pip install -r requirements.txt


EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000 && python manage.py makemigrations && python manage.py migrate
