#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python make_demo_images.py
python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_shop
echo "Admin login banayein:"
python manage.py createsuperuser
python manage.py runserver
