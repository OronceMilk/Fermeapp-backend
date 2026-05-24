# FermeApp - Application de Gestion de Ferme

Application frontend moderne pour la gestion d'une ferme, développée avec Django Templates, Tailwind CSS, HTMX et Vanilla JS.

## 🚀 Vue d'ensemble

FermeApp est une application web complète pour gérer un cheptel d'animaux. Elle offre une interface moderne et responsive avec des fonctionnalités avancées comme les filtres dynamiques, les graphiques interactifs et les notifications en temps réel.

## 🛠️ Technologies utilisées

- **Backend**: Django (existante)
- **Frontend**: Django Templates + Tailwind CSS + HTMX + Vanilla JS + Chart.js
- **UI/UX**: Design responsive mobile-first
- **Interactivité**: HTMX pour éviter les rechargements de page

## 📦 Installation

### Prérequis

- Python 3.8+
- pip
- Virtualenv (recommandé)

### Installation

1. **Cloner ou copier le projet**
   ```bash
   cd /chemin/vers/votre/projet
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Appliquer les migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Application: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## 📁 Structure du projet

```
FermeApp/
├── fermeapp/
│   ├── settings.py              # Configuration Django
│   ├── urls.py                  # URLs principales
│   ├── wsgi.py                  # Configuration WSGI
│   ├── asgi.py                  # Configuration ASGI
│   └── fermeapp/
│       ├── __init__.py
│       ├── models.py            # Modèles Animal et Traitement
│       ├── views.py             # Vues Django
│       ├── urls.py              # URLs de l'app
│       ├── forms.py             # Formulaires
│       └── context_processors.py # Context processors
├── templates/
│   ├── base.html                # Layout principal
│   ├── accounts/
│   │   └── login.html           # Page de connexion
│   ├── dashboard/
│   │   └── dashboard.html       # Dashboard avec KPIs
│   └── cheptel/
│       ├── animal_list.html     # Liste des animaux
│       ├── animal_form.html     # Formulaire animal
│       ├── traitement_list.html # Historique traitements
│       └── partials/
│           ├── animal_table.html    # Tableau animaux (HTMX)
│           └── traitement_timeline.html # Timeline traitements
├── static/
│   ├── css/
│   │   └── tailwind.css         # Styles Tailwind
│   └── js/
│       ├── dashboard.js         # Graphiques Chart.js
│       ├── notifications.js     # Système de toasts
│       └── filters.js           # Gestion des filtres
├── manage.py                    # Commandes Django
├── requirements.txt             # Dépendances Python
├── guide_integration.html       # Guide d'intégration web
└── README.md                    # Documentation
```

## 🚀 Vue d'ensemble

FermeApp est une application web complète pour gérer un cheptel d'animaux. Elle offre une interface moderne et responsive avec des fonctionnalités avancées comme les filtres dynamiques, les graphiques interactifs et les notifications en temps réel.

## 🛠️ Technologies utilisées

- **Backend**: Django (existante)
- **Frontend**: Django Templates + Tailwind CSS + HTMX + Vanilla JS + Chart.js
- **UI/UX**: Design responsive mobile-first
- **Interactivité**: HTMX pour éviter les rechargements de page

## 📁 Structure du projet

```
FermeApp/
├── templates/
│   ├── base.html                    # Layout principal avec sidebar et topbar
│   ├── accounts/
│   │   └── login.html              # Page de connexion
│   ├── dashboard/
│   │   └── dashboard.html          # Dashboard admin avec KPIs et graphiques
│   └── cheptel/
│       ├── animal_list.html         # Liste des animaux avec filtres HTMX
│       ├── animal_form.html         # Formulaire ajout/modification animal
│       ├── traitement_list.html     # Historique sanitaire
│       └── partials/
│           ├── animal_table.html    # Tableau des animaux (HTMX)
│           └── traitement_timeline.html # Timeline traitements
├── static/
│   ├── css/
│   │   └── tailwind.css            # Styles Tailwind compilés
│   └── js/
│       ├── dashboard.js             # Graphiques Chart.js
│       ├── notifications.js         # Système de toasts
│       └── filters.js               # Gestion des filtres HTMX
└── README.md                        # Documentation complète
```

## ⚙️ Configuration Django

### settings.py
```python
INSTALLED_APPS = [
    # ... autres apps
    'fermeapp',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... autres context processors
                'fermeapp.context_processors.user_role',
            ],
        },
    },
]
```

### urls.py
```python
# urls.py (projet principal)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('fermeapp.urls')),
]

# fermeapp/urls.py
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('cheptel/', views.animal_list, name='animal_list'),
    path('cheptel/ajouter/', views.animal_form, name='animal_form'),
    path('cheptel/<int:pk>/modifier/', views.animal_form, name='animal_edit'),
    path('cheptel/<int:pk>/supprimer/', views.animal_delete, name='animal_delete'),
    # HTMX endpoints
    path('api/cheptel/filtrer/', views.filter_animals, name='filter_animals'),
    path('api/traitements/', views.traitement_list, name='traitement_list'),
]
```

## 🔄 Patterns HTMX

### 1. Filtres dynamiques
```html
<select name="statut"
        hx-get="/api/cheptel/filtrer/"
        hx-target="#animal-table"
        hx-include="[name='espece'],[name='lot'],[name='recherche']"
        hx-indicator="#loading-indicator">
```

### 2. Détection HTMX dans les vues Django
```python
def filter_animals(request):
    animaux = Animal.objects.filter(...)

    if request.headers.get('HX-Request'):
        return render(request, 'cheptel/partials/animal_table.html', {
            'animaux': animaux
        })

    return render(request, 'cheptel/animal_list.html', {
        'animaux': animaux
    })
```

### 3. Toasts via headers HTTP
```python
def animal_form(request, pk=None):
    if request.method == 'POST':
        if form.is_valid():
            animal = form.save()
            response = HttpResponse()
            response['HX-Toast'] = f'Animal "{animal.nom}" créé ✅'
            response['HX-Toast-Type'] = 'success'
            response['HX-Redirect'] = reverse('animal_list')
            return response
```

## 📋 Référence HTMX

| Attribut | Description | Exemple |
|----------|-------------|---------|
| `hx-get` | Requête GET | `hx-get="/api/data/"` |
| `hx-post` | Requête POST | `hx-post="/api/save/"` |
| `hx-target` | Cible d'injection | `hx-target="#content"` |
| `hx-include` | Inclure des éléments | `hx-include="[name='filter']"` |
| `hx-indicator` | Indicateur de chargement | `hx-indicator="#spinner"` |
| `hx-swap` | Méthode de remplacement | `hx-swap="innerHTML"` |

## 🎨 États UI

### Loading State
```html
<div id="loading-indicator" class="htmx-indicator">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    Chargement...
</div>
```

### Success State
```html
<div class="text-green-600 p-4 bg-green-50 rounded">
    Opération réussie !
</div>
```

### Error State
```html
<div class="text-red-600 p-4 bg-red-50 rounded">
    {% if form.errors %}
        <ul>
        {% for field, errors in form.errors.items %}
            <li>{{ field }}: {{ errors|join:", " }}</li>
        {% endfor %}
        </ul>
    {% endif %}
</div>
```

### Empty State
```html
<div class="text-center py-12">
    <div class="text-gray-400 text-6xl mb-4">🐄</div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">Aucun animal</h3>
    <p class="text-gray-500">Commencez par ajouter votre premier animal.</p>
    <a href="{% url 'animal_form' %}" class="btn btn-primary">Ajouter un animal</a>
</div>
```

## 🛠️ API JavaScript

### dashboard.js
- `initCharts()`: Initialisation des graphiques Chart.js
- `updateChartData(period)`: Mise à jour des données (7j/30j)
- `animateKPICards()`: Animation des cartes KPI

### notifications.js
- `showToast(message, type)`: Afficher un toast
- `showSuccessToast(message)`: Toast de succès
- `showErrorToast(message)`: Toast d'erreur

### filters.js
- `syncFiltersWithURL()`: Synchronisation URL avec les filtres
- `updateActiveFiltersCount()`: Comptage des filtres actifs
- `highlightActiveFilters()`: Mise en évidence des filtres actifs

## 🚀 Installation et déploiement

1. **Créer la structure des dossiers**
2. **Copier les templates HTML**
3. **Ajouter les fichiers JavaScript**
4. **Configurer Django (settings.py, urls.py)**
5. **Créer les vues Django**
6. **Intégrer Tailwind CSS**
7. **Tester les endpoints HTMX**
8. **Configurer les modèles Django**
9. **Ajouter la gestion des rôles**
10. **Déploiement et tests finaux**

## 📱 Fonctionnalités

- ✅ Dashboard avec KPIs et graphiques
- ✅ Gestion complète du cheptel
- ✅ Filtres dynamiques HTMX
- ✅ Système de notifications toasts
- ✅ Formulaires avec validation
- ✅ États de chargement et d'erreur
- ✅ Interface responsive mobile-first
- ✅ Gestion des rôles (Admin/Employé)

## 🤝 Contribution

Ce projet est développé dans le cadre d'un projet de mémoire. Pour toute question ou suggestion, n'hésitez pas à contacter l'équipe de développement.

---

**Développé avec ❤️ pour la gestion moderne des fermes**