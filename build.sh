#!/bin/bash
echo "🗑️ Suppression de l'ancien dossier staticfiles..."
rm -rf staticfiles

pip install -r requirements.txt
pip install gunicorn  # 🔥 Installation explicite de gunicorn

python manage.py migrate
python manage.py collectstatic --noinput

echo "📋 Copie de secours des fichiers statiques (contournement collectstatic)..."
mkdir -p staticfiles

# Fichiers du projet
if [ -d "static" ]; then
    cp -rn static/. staticfiles/ 2>/dev/null || true
fi

# Assets Django admin
DJANGO_ADMIN_STATIC=$(python -c "import django, os; print(os.path.join(os.path.dirname(django.__file__), 'contrib', 'admin', 'static', 'admin'))" 2>/dev/null)
if [ -d "$DJANGO_ADMIN_STATIC" ]; then
    echo "Copie des assets de l'admin Django..."
    cp -rn "$DJANGO_ADMIN_STATIC" staticfiles/admin 2>/dev/null || true
fi

# Assets Cloudinary
CLOUDINARY_STATIC=$(python -c "import cloudinary, os; print(os.path.join(os.path.dirname(cloudinary.__file__), 'static', 'cloudinary'))" 2>/dev/null)
if [ -d "$CLOUDINARY_STATIC" ]; then
    echo "Copie des assets de Cloudinary..."
    cp -rn "$CLOUDINARY_STATIC" staticfiles/cloudinary 2>/dev/null || true
fi

echo "✅ Build terminé"