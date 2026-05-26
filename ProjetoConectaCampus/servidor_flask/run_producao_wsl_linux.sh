#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
