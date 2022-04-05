FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y build-essential python3-dev python3-pip \
                       ffmpeg libwebp-dev git
    
RUN pip3 install uwsgi

COPY resources/uwsgi.ini /etc/

ADD app/ /opt/example/

RUN pip3 install --upgrade \
        git+https://github.com/gsteixeira/django-social-layer.git

RUN cd /opt/example/ && \
    rm /opt/example/db/db.sqlite3 || true && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py migrate && \
    chown www-data.www-data -R /opt/example && \
    chown www-data.www-data db

WORKDIR /opt/example

ENTRYPOINT ["uwsgi", "--ini", "/etc/uwsgi.ini"]
