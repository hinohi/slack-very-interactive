#!/bin/sh

cd $(dirname $(dirname $0))

celery worker --app=very.core.tasks --config=very.very.conf --loglevel=info
