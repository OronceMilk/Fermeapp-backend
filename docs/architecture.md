

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

## Onboarding self-service (P14)

Depuis P14, la création d'une ferme et de son premier compte administrateur ne nécessite plus d'intervention manuelle via le shell Django — un visiteur peut créer son exploitation de façon autonome.
Visiteur
│
▼
Formulaire d'inscription (/accounts/inscription/)
│ InscriptionForm : données ferme + données admin en une seule saisie
▼
accounts/services.py::inscrire_nouvelle_ferme()
│ transaction.atomic() — Ferme et User créés ensemble ou pas du tout
▼
Connexion automatique + redirection vers le Dashboard


**Décision d'architecture — localisation de la logique** : comme pour `cheptel/services.py` et `stocks/services.py`, la logique métier vit dans une fonction de service (`inscrire_nouvelle_ferme`), pas dans la vue. La vue (`InscriptionView`, `FormView`) reste responsable uniquement du cycle requête/réponse et de la traduction des exceptions métier en erreurs de formulaire.

**Garantie transactionnelle** : `inscrire_nouvelle_ferme()` est décorée `@transaction.atomic`. Sans cette garantie, un échec de validation sur le `User` après la création de la `Ferme` laisserait une ferme orpheline en base — un état non récupérable depuis l'interface, puisqu'aucun flux ne permet de rattacher un administrateur à une ferme existante après coup. Testé explicitement (`test_rollback_si_validation_echoue`).

**Décision d'architecture — unicité de l'email `User`** : `email` est désormais `unique=True` sur le modèle `User` (auparavant hérité d'`AbstractUser` sans contrainte). Décision prise en anticipation d'un futur mécanisme de récupération de compte par email, et pour fermer la faille qu'une validation au seul niveau formulaire aurait laissée ouverte à tout autre point d'entrée (admin Django, scripts, future API). Vérifié avant migration : aucun doublon ni email vide en base (locale et production) au moment du changement.

**Défense en profondeur** : la vue catche à la fois `EmailDejaUtiliseException` (levée volontairement par le service) et `ValidationError` générique (filet de sécurité pour toute violation de contrainte modèle non anticipée par le formulaire — découvert en pratique avec la validation du format de `username`, qui n'était initialement vérifiée qu'au niveau du modèle, pas du formulaire).

\## Couche services



Introduite progressivement (Sprints 8-11) sur les modules où elle apportait une vraie valeur :



\- \*\*`stocks/services.py`\*\* (`StockService`) : gestion transactionnelle des mouvements de stock, avec `select\_for\_update()` pour empêcher qu'un stock devienne négatif sous accès concurrent. Validé par un test de concurrence réel (deux threads, connexions séparées).

\- \*\*`cheptel/services.py`\*\* : filtrage/agrégation des animaux, lots, traitements et rapports journaliers. Introduit notamment pour corriger un problème de requêtes N+1 sur le listing des lots (`get\_lots\_avec\_comptage`, validé par un test `django\_assert\_max\_num\_queries`).

\- \*\*`dashboard/services/`\*\* : six services indépendants (KPIs, alertes, statistiques, activité récente, finances, score de santé), consommés par une seule vue agrégatrice.

\- \*\*`cultures`\*\* : après audit, jugé ne pas nécessiter de couche services dédiée (vues déjà courtes, sans duplication ni N+1) — un correctif ciblé (validation `full\_clean()` automatique) a suffi plutôt qu'un refactor complet, décision documentée pour éviter la complexité artificielle.

## Verrouillage UX — décision de ne pas introduire Crispy Forms

**Décision prise** : FermeApp n'utilise pas Crispy Forms (ni aucune autre bibliothèque de rendu de formulaires tierce). Les formulaires sont stylés manuellement via une combinaison de :

- **CSS global** dans `base.html` pour les champs de base (`input[type="text"]`, `select`, `textarea`...), qui s'applique à tout formulaire sans effort supplémentaire.
- **Widgets Django personnalisés** pour les cas particuliers (`NumberInput` avec `inputmode`, `TextInput` avec `type="tel"`...).
- **Styles inline** uniquement sur `login.html` (en cours de migration vers le CSS global).

**Seuil de bascule** : si un jour un formulaire devient suffisamment complexe pour justifier un rendu conditionnel lourd (champs qui apparaissent/disparaissent selon le type de transaction, listes déroulantes dynamiques, etc.), la question sera réévaluée. Ce seuil n'est pas atteint aujourd'hui.


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

## P15 — Finances réelles : frontière avec `MouvementStock`

Le modèle `finances.Transaction` a été introduit pour couvrir tout mouvement financier qui n'a **aucune représentation ailleurs** dans le système : ventes (recettes) et dépenses hors-stock (salaires, vétérinaire, location, transport). Il ne couvre volontairement **pas** les achats de produits stockés (aliment, vaccins, semences) — ceux-ci restent exclusivement portés par `stocks.MouvementStock` (type `ENTREE`), pour éviter tout double-comptage dans `dashboard/services/finance_service.py::get_finances()`.

`get_finances()` calcule désormais : `dépenses = MouvementStock (achats de stock) + Transaction (dépenses hors-stock)`, `recettes = Transaction (ventes)`. L'ancienne estimation `recettes = dépenses * 1.3` (présente depuis le MVP initial) a été retirée à ce moment — elle n'existe plus nulle part dans le code depuis P15.

Une fonction séparée, `get_finances_mois()`, a été ajoutée pour la fenêtre mensuelle plutôt que de modifier la signature de `get_finances()` (cumul total, déjà consommée ailleurs) — décision prise pour ne pas risquer de régression sur le code existant.

## P16 — UX mobile et dérive de périmètre assumée

P16 a été planifié comme un chantier resserré : CSS global pour les champs de formulaire, `inputmode`/`type` adaptés au clavier mobile (`montant`, `téléphone`), vérification du défilement horizontal des tableaux. Cette portée a été délibérément resserrée après plusieurs itérations de revue d'architecture, en écartant consciemment des options plus lourdes (tag de template personnalisé, mixin de formulaire) jugées disproportionnées au nombre réel de formulaires du projet à ce stade (3).

En cours d'exécution, le sprint a débordé vers une refonte visuelle complète des pages `login`/`inscription` (fond dégradé, cartes glassmorphism, animations). Cette dérive a été identifiée et signalée en cours de route. Décision assumée : le résultat est conservé, car il apporte une amélioration UX réelle et cohérente avec le niveau de qualité déjà établi côté backend — mais la méthode (débordement non planifié plutôt que décision préalable) est documentée ici comme un écart au processus habituel du projet, pas comme un nouveau standard à reproduire.

**Seuil de bascule vers une bibliothèque de formulaire dédiée** (ex. Crispy Forms) : à reconsidérer si le nombre de formulaires dépasse largement 15-20 avec une diversité réelle de types de widgets (cases à cocher, fichiers, mises en page conditionnelles) — pas avant, conformément au principe YAGNI appliqué tout au long de ce projet.

## Dette technique connue — `collectstatic` ne copie aucun fichier

Découvert pendant P16 : `python manage.py collectstatic` rapporte systématiquement "0 static files copied", de façon reproductible sur deux environnements indépendants (Windows local, y compris un environnement virtuel entièrement reconstruit à neuf, et Render/Linux en production). Une investigation approfondie — vérification de `STATICFILES_DIRS`, `STATICFILES_FINDERS`, l'ordre d'`INSTALLED_APPS`, absence de commande `collectstatic` personnalisée, version de Django/Python, et enfin instrumentation directe du code source de la commande (`django/contrib/staticfiles/management/commands/collectstatic.py`) — a confirmé que les fichiers sont bien détectés par les finders (143 fichiers trouvés via `get_finders()`) et que les appels de copie s'exécutent sans erreur visible, mais qu'aucun fichier ne se retrouve physiquement sur le disque à la fin de l'exécution.

**La cause racine n'a pas été identifiée.** Un contournement a été mis en place dans `build.sh` : après l'appel (inefficace) à `collectstatic`, une copie manuelle (`cp -rn`) rapatrie les fichiers du projet (`static/`) ainsi que les assets de `django.contrib.admin` et `django-cloudinary-storage` (localisés dynamiquement via `python -c "import django/cloudinary; ..."`, pas de chemin en dur) directement dans `staticfiles/`.

**Limite connue de ce contournement** : `STATICFILES_STORAGE` reste sur `django.contrib.staticfiles.storage.StaticFilesStorage` (stockage plat, sans hash de cache-busting) plutôt que `whitenoise.storage.CompressedManifestStaticFilesStorage` (utilisé jusqu'à ce diagnostic) — un retour à ce dernier casserait le contournement, car les fichiers copiés manuellement n'auraient aucune entrée dans le manifeste `staticfiles.json` que seul un `collectstatic` fonctionnel peut générer. **Si le cache-busting par hash redevient nécessaire, ce point devra être réinvestigué en profondeur avant toute tentative de réactivation du manifeste.**


