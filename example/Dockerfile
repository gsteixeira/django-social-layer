FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y build-essential python3-dev python3-pip \
                       ffmpeg libwebp-dev git
    
RUN pip3 install Django==4.0 \
                 uwsgi==2.0.20 \
                 Pillow==8.4.0 \
                 opencv-python==4.5.4.60 \
                 celery==5.2.3 \
                 django-infinite-scroll

COPY resources/uwsgi.ini /etc/

ADD app/ /opt/example/

RUN pip3 install --no-deps --upgrade \
        git+https://github.com/gsteixeira/django-social-layer.git

RUN cd /opt/example/ && \
    rm /opt/example/db/db.sqlite3 || true && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py migrate && \
    chown www-data.www-data -R /opt/example && \
    chown www-data.www-data db

WORKDIR /opt/example

ENTRYPOINT ["uwsgi", "--ini", "/etc/uwsgi.ini"]
