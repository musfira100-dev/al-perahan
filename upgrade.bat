@echo off
cd /d %~dp0
echo === Purani zip se upgrade ===
echo Ye purane products/categories hata kar naya dummy data (suits, parda, clothing, bed sheets) bharega.
echo Aap ke orders aur admin user safe rahenge. Band karne ke liye Ctrl+C dabayein.
pause
call venv\Scripts\activate
python -m pip install -r requirements.txt
python make_demo_images.py
python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_shop --reset
python manage.py runserver
