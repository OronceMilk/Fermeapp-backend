# FermeApp

Application web de gestion agro-pastorale pour exploitants béninois, développée en Django/PostgreSQL. Née d'observations de terrain à Tori-Bossito et Allada, FermeApp centralise la gestion du cheptel, des cultures, des stocks et des indicateurs de performance d'une exploitation.

## Stack technique

- **Backend** : Django 4.2, PostgreSQL
- **Frontend** : Django Templates, Tailwind CSS, HTMX, Chart.js
- **Cache** : Redis (`django-redis`)
- **Stockage médias** : Cloudinary
- **Monitoring** : Sentry
- **Hébergement** : Render (web service + PostgreSQL + Redis managés)
- **Tests** : pytest / pytest-django (76 tests)
- **CI/CD** : GitHub Actions

## Modules

| App | Rôle |
|---|---|
| `accounts` | Utilisateurs, fermes, authentification, isolation multi-tenant |
| `cheptel` | Animaux, lots, traitements, rapports journaliers, comptages d'œufs |
| `cultures` | Parcelles, cultures, activités agricoles |
| `stocks` | Produits, mouvements de stock, gestion de la concurrence |
| `dashboard` | KPIs, alertes, statistiques, agrégation multi-modules |

## Architecture

Voir [`docs/architecture.md`](docs/architecture.md) pour le détail de l'organisation `Views → Services → Models → PostgreSQL`.

## Installation locale

```bash
git clone https://github.com/OronceMilk/Fermeapp-backend.git
cd fermeApp_BINOME
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
# Éditer .env avec une SECRET_KEY générée (voir ci-dessous) et vos identifiants locaux

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate
python manage.py createsuperuser   # nécessite de créer une Ferme au préalable pour un compte non-superuser,
                                    # les superusers en sont exemptés (voir docs/architecture.md)
python manage.py runserver

Prérequis : PostgreSQL et Redis installés localement (voir .env.example pour le format des URLs de connexion attendues).

## Tests

```bash
pytest                                    # suite complète
pytest --cov=. --cov-report=term-missing  # avec couverture
76 tests couvrant : les règles métier (`cheptel`, `cultures`, `stocks`), l'isolation multi-ferme, la concurrence sur les mouvements de stock, et les services du dashboard.

Déploiement
Le projet est déployé sur Render. Variables d'environnement requises (voir .env.example) : DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS, DATABASE_URL, REDIS_URL, SENTRY_DSN, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET.

## Roadmap

Modules `finances`, `rapports` (transversal), `tâches` et `paramètres` sont au stade de maquette (templates non branchés) — prochaine étape de développement, hors du périmètre de consolidation technique actuel.

Licence
MIT

text

---

### 🔍 Adaptation à faire

- **URL du dépôt** : `https://github.com/OronceMilk/Fermeapp-backend.git` est déjà correct.
- **Licence** : J'ai mis `MIT` par défaut. Si tu préfères une autre licence (ex: `GPL` ou `Propriétaire`), adapte la dernière ligne.

---

**Sauvegarde (Ctrl+S), ferme Notepad, puis ajoute le fichier au commit :**

```bash
git add README.md