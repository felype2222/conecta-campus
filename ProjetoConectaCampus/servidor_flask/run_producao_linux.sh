#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export SECRET_KEY="${SECRET_KEY:-troque-esta-chave}"
exec gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
