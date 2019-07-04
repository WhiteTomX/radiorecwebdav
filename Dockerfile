FROM python:3.7

LABEL company="WhiteTom"
LABEL version="0.0.3"

RUN apt-get update && apt-get -y install cron


RUN pip3.7 install webdavclient3


COPY ./radiorecwebdav.py /radiorecwebdav.py
RUN chmod +x /radiorecwebdav.py
RUN mkdir /settings/
COPY ./settings.ini /settings/settings.ini

COPY example.cron /etc/cron.d/example
RUN chmod 0644 /etc/cron.d/example

CMD ["cron", "-f"]