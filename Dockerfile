FROM ubuntu:latest

RUN apt update && apt upgrade -y

RUN apt install python3-pip git build-essential python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info fontconfig -y

COPY requirements/common.txt requirements/common.txt
RUN pip3 install -U pip && pip3 install -r requirements/common.txt

COPY ./api /app/api
COPY ./bin /app/bin
COPY ./jinja /app/jinja
COPY ./static /app/static
COPY wsgi.py /app/wsgi.py

WORKDIR /app

#RUN useradd demo
#USER demo

#ENV OSFONTDIR=/usr/share/fonts
#RUN fc-cache --really-force --verbose


EXPOSE 8080

ENTRYPOINT ["bash", "/app/bin/run.sh"]