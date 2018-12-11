FROM python:3.7-alpine
MAINTAINER blue1616

COPY requirements /root/requirements

RUN apk upgrade --no-cache && \
  apk add --no-cache build-base && \
  apk add --no-cache libxml2-dev libxslt-dev && \
  pip install -r /root/requirements && \
  apk del build-base

RUN addgroup -g 1000 codescraper && \
  adduser -D -u 1000 -G codescraper codescraper && \
  mkdir -p /home/codescraper/

COPY ./master /home/codescraper/master
RUN chown -R codescraper:codescraper /home/codescraper && \
  chmod +x /home/codescraper/master/startbot.sh

USER codescraper
WORKDIR /home/codescraper/master

#CMD ["python", "/home/codescraper/master/run.py"]
CMD ["/home/codescraper/master/startbot.sh"]
