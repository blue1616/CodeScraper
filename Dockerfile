FROM debian:latest

RUN apt-get update && apt-get install -y wget unzip python3 python3-dev python3-pip \
  --no-install-recommends  && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir -p /home/codescraper/ && \
  wget https://github.com/blue1616/CodeScraper/archive/master.zip -P /tmp && \
  unzip /tmp/master.zip -d /tmp && \
  mv /tmp/CodeScraper-master/master /home/codescraper/ && \
  rm -rf /tmp/*

ADD requirements /tmp/requirements
RUN pip3 install -i /tmp/requirements

RUN groupadd -r codescraper && useradd -r -g codescraper -G audio,video codescraper && \
  usermod -u 1000 codescraper && groupmod -g 1000 codescraper && \
  chsh -s /bin/bash codescraper && \
  chown -R codescraper:codescraper /home/codescraper

USER codescraper
WORKDIR /home/codescraper
CMD [python3, /home/codescraper/master/run.py]
