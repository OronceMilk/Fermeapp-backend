

\# Architecture technique — FermeApp



\## Vue d'ensemble



```

Navigateur (HTMX + Chart.js)

&#x20;       │

&#x20;       ▼

Views (Django CBV/FBV)

&#x20;       │

&#x20;       ▼

Services métier (cheptel/services.py, stocks/services.py, dashboard/services/\*.py)

&#x20;       │

&#x20;       ▼

Models Django (validations clean()/full\_clean())

&#x20;       │

&#x20;       ▼

PostgreSQL (Render, managé)



Cache      → Redis (partagé entre workers)

Médias     → Cloudinary

Monitoring → Sentry

```



\## Principe central : isolation multi-tenant



Chaque utilisateur appartient à une `Ferme` (`accounts.models.User.ferme`). Tous les querysets métier filtrent explicitement par `ferme=request.user.ferme` (ou équivalent via une relation), garantissant qu'aucune donnée d'une exploitation n'est visible par une autre. Ce principe est vérifié par des tests d'isolation dédiés sur `cheptel`, `stocks` et `cultures`.



\*\*Exception documentée\*\* : un superuser Django (compte plateforme) n'est rattaché à aucune ferme — voir `accounts/models.py::User.clean()`.



\## Couche services



Introduite progressivement (Sprints 8-11) sur les modules où elle apportait une vraie valeur :



\- \*\*`stocks/services.py`\*\* (`StockService`) : gestion transactionnelle des mouvements de stock, avec `select\_for\_update()` pour empêcher qu'un stock devienne négatif sous accès concurrent. Validé par un test de concurrence réel (deux threads, connexions séparées).

\- \*\*`cheptel/services.py`\*\* : filtrage/agrégation des animaux, lots, traitements et rapports journaliers. Introduit notamment pour corriger un problème de requêtes N+1 sur le listing des lots (`get\_lots\_avec\_comptage`, validé par un test `django\_assert\_max\_num\_queries`).

\- \*\*`dashboard/services/`\*\* : six services indépendants (KPIs, alertes, statistiques, activité récente, finances, score de santé), consommés par une seule vue agrégatrice.

\- \*\*`cultures`\*\* : après audit, jugé ne pas nécessiter de couche services dédiée (vues déjà courtes, sans duplication ni N+1) — un correctif ciblé (validation `full\_clean()` automatique) a suffi plutôt qu'un refactor complet, décision documentée pour éviter la complexité artificielle.



\## Validation des données



Deux mécanismes coexistent, avec un choix explicite documenté par module :

\- Modèles `cheptel` et (depuis Sprint 11) `cultures` : `save()` appelle systématiquement `full\_clean()` — défense en profondeur, protège même un accès direct à l'ORM (shell, script, future API).

\- `stocks.MouvementStock` : validation portée par le service (`StockService.creer\_mouvement`) plutôt que par le modèle — un gap documenté par test (`test\_creation\_orm\_directe\_quantite\_negative\_non\_bloquee`), accepté comme dette connue plutôt que corrigé, car le seul point d'entrée actuel passe par le service.



\## Concurrence et cohérence



\- \*\*Stock\*\* : `select\_for\_update()` dans une transaction atomique, seule protection efficace en PostgreSQL (elle ne l'était pas sous SQLite, d'où la priorité donnée à la migration PostgreSQL en tout début de plan).

\- \*\*Cache\*\* : Redis partagé entre workers, remplaçant le cache mémoire local par défaut qui aurait produit des incohérences dès qu'un déploiement tournerait à plusieurs workers gunicorn.



\## Tests



76 tests au total (`pytest`), organisés par app en packages (`cheptel/tests/`, `cultures/tests/`, `stocks/tests/`), avec un `conftest.py` racine pour les fixtures transversales (`ferme`, `ferme\_autre`, `admin\_user`) et des `conftest.py` locaux pour les fixtures spécifiques à chaque module. Un pipeline GitHub Actions (`.github/workflows/test.yml`) exécute la suite complète avec une base PostgreSQL de service à chaque push.



\## Infrastructure



| Composant | Choix | Justification |

|---|---|---|

| Hébergement | Render | Simplicité pour un projet de cette taille, add-ons PostgreSQL/Redis managés |

| Base de données | PostgreSQL (managé Render) | Nécessaire pour un vrai support de la concurrence (`select\_for\_update`) |

| Cache | Redis (managé Render) | Cohérence multi-worker |

| Médias | Cloudinary | Le filesystem Render est éphémère (perdu à chaque redéploiement) |

| Monitoring | Sentry | Visibilité sur les erreurs de production sans dépendre des retours utilisateurs |

| Secrets | Variables d'environnement (`django-environ`) | Aucun secret en dur dans le code versionné |



\## Ce qui reste hors du périmètre actuel



\- Pas d'API REST (DRF) — toute la restitution passe par des vues Django server-side rendues, HTMX pour les mises à jour partielles.

\- Pas de Docker — développement et déploiement s'appuient sur des installations natives (PostgreSQL, Redis) et le pipeline Render existant.

\- Modules `finances`, `rapports` transversaux, `tâches`, `paramètres` : maquettes frontend non connectées à une logique backend réelle.

```



\---





