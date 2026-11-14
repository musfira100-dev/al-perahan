@echo off
cd /d %~dp0
echo === Al Perahan Collection - first time setup ===
if not exist venv ( python -m venv venv )
call venv\Scripts\activate
python -m pip install -r requirements.txt
python make_demo_images.py
python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_shop
echo.
echo Ab admin login banayein (username + password):
python manage.py createsuperuser
echo.
echo Site: http://127.0.0.1:8000   Admin: http://127.0.0.1:8000/admin
python manage.py runserver
