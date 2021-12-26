FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y build-essential python3-dev python3-pip \
                       ffmpeg libwebp-dev 
    
RUN pip3 install Django==3.2.10 \
                 uwsgi==2.0.20 \
                 Pillow==8.4.0 \
                 opencv-python==4.5.4.60 \
                 django-infinite-scroll==0.1.7

COPY resources/uwsgi.ini /etc/

ADD app/ /opt/example/

RUN pip3 install --no-deps --upgrade django-social-layer

RUN cd /opt/example/ && \
    rm /opt/example/db/db.sqlite3 || true && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py migrate && \
    chown www-data.www-data -R /opt/example && \
    chown www-data.www-data db

WORKDIR /opt/example

ENTRYPOINT ["uwsgi", "--ini", "/etc/uwsgi.ini"]
