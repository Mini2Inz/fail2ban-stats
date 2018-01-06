FROM python:3

COPY . /fail2ban-stats
WORKDIR /fail2ban-stats
RUN pip install -r requirements.txt
RUN pip install https://github.com/celery/django-celery-beat/zipball/master#egg=django-celery-beat
RUN python manage.py makemigrations
RUN python manage.py migrate


EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
CMD celery -A Fail2banNgStats  beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
