@echo off
echo Suppression de l'ancien dossier staticfiles...
rmdir /s /q staticfiles 2>nul

echo Installation des dépendances...
pip install -r requirements.txt

echo Migrations...
python manage.py migrate

echo Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo Copie de secours des fichiers statiques...
mkdir staticfiles 2>nul

if exist static (
    echo Copie des fichiers du projet...
    xcopy /E /I /Y static\* staticfiles\
)

if exist .venv_binome\Lib\site-packages\django\contrib\admin\static\admin (
    echo Copie des assets de l'admin Django...
    mkdir staticfiles\admin 2>nul
    xcopy /E /I /Y .venv_binome\Lib\site-packages\django\contrib\admin\static\admin\* staticfiles\admin\
)

if exist .venv_binome\Lib\site-packages\cloudinary\static\cloudinary (
    echo Copie des assets de Cloudinary...
    mkdir staticfiles\cloudinary 2>nul
    xcopy /E /I /Y .venv_binome\Lib\site-packages\cloudinary\static\cloudinary\* staticfiles\cloudinary\
)

echo Build termine