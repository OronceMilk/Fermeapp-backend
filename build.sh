#!/bin/bash
echo "🗑️ Suppression de l'ancien dossier staticfiles..."
rm -rf staticfiles

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput