FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-dev python3-pip && \
  rm -rf /var/lib/apt/lists/*

ADD requirements /tmp/requirements
RUN pip3 install -r /tmp/requirements

RUN groupadd -r codescraper && useradd -r -g codescraper -G audio,video codescraper && \
  mkdir -p /home/codescraper/ && \
  usermod -u 1000 codescraper && groupmod -g 1000 codescraper && \
  chsh -s /bin/bash codescraper

ADD ./master /home/codescraper/master
RUN chown -R codescraper:codescraper /home/codescraper

USER codescraper
WORKDIR /home/codescraper/master

CMD ["python3", "/home/codescraper/master/run.py"]
