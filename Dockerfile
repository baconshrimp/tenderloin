FROM ubuntu:14.04
MAINTAINER Michael Tom-Wing <mtomwing@gmail.com>

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python3-pip

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ADD tenderloin /opt/tenderloin

WORKDIR /opt
EXPOSE 8000
CMD python3 -m tenderloin.web --port=8000
