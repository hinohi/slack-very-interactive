#!/bin/sh

cd $(dirname $(dirname $0))
gunicorn very.very.web:web --log-file=- --log-level=info
