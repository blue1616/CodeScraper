#!/bin/sh

if [ -z "$DB_HOST" ]; then
  echo "DB_HOST is empty"
  exit
fi

if [ -z "$DB_PORT" ]; then
  echo "DB_PORT is empty"
  exit
fi

if [ -z "$DB_NAME" ]; then
  DB_NAME=codescraper-database
fi

python3 run.py --db-host=$DB_HOST --db-port=$DB_PORT --db-name=$DB_NAME
