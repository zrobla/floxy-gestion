# Floxy Made Management

## Presentation

Ce projet fournit une base Django pour la gestion Floxy Made. Toutes les interfaces
et la documentation sont en francais, tandis que les identifiants de code restent
en anglais.

## Pre-requis

- Python 3.11+
- SQLite 3 (inclus avec Python)
- Docker et Docker Compose (optionnel)

## Installation locale

1. Creez un environnement virtuel :
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   ```
2. Installez les dependances :
   ```bash
   pip install -r requirements.txt
   ```
3. Copiez `.env.example` vers `.env` et mettez a jour les valeurs.
4. Appliquez les migrations :
   ```bash
   python manage.py migrate
   ```
5. (Optionnel) Lancez les seeds utiles :
   ```bash
   python manage.py seed_initial_users
   python manage.py seed_social_tasks
   python manage.py seed_content_examples
   ```
6. Lancez le serveur :
   ```bash
   python manage.py runserver
   ```

## Lancer avec Docker

```bash
docker compose up --build
```

Dans un autre terminal, appliquez les migrations :

```bash
docker compose exec web python manage.py migrate
```

## Variables d'environnement

Les variables principales sont detaillees dans `.env.example`.

- `DJANGO_SECRET_KEY` : cle secrete Django
- `DJANGO_DEBUG` : mode debug (True/False)
- `DJANGO_ALLOWED_HOSTS` : liste separee par des virgules
- `DJANGO_RUNSERVER_HIDE_WARNING` : masque l'avertissement du serveur de developpement
- `SQLITE_PATH` : chemin vers le fichier SQLite

Astuce : pour activer le debug en local, mettez `DJANGO_DEBUG=True` dans `.env`.

Formats dates : l'application et l'admin utilisent `jj/mm/aaaa` (et `jj/mm/aaaa hh:mm` pour les dates/heures).

## Utilisateurs initiaux

Pour creer les comptes de demarrage (OWNER, MANAGER, ADMIN, STAFF, CASHIER), lancez :

```bash
python manage.py seed_initial_users
```

Les identifiants et mots de passe sont affiches dans la console.

## Rôles

- OWNER : accès complet + validations + dashboard.
- ADMIN : gestion avancée + intégrations Loyverse.
- MANAGER : gestion des opérations, tâches et contenus.
- STAFF : accès limité à ses tâches.
- CASHIER : profil dédié caisse (à étendre selon besoins).

## Workflows clés

- Activités : création > statut > paiement (manuel ou Loyverse).
- Perruques entretien : création > impression étiquette.
- Tâches : modèles récurrents + checklists.
- Contenus : idée > validation > publication > métriques.
- Inventaire : articles + mouvements de stock.

## Endpoints perruques

Exemples pour tester l'API des perruques :

- Liste des perruques en stock :
  ```bash
  curl "http://localhost:8000/api/wigs/products/?status=IN_STOCK"
  ```
- Recherche par code :
  ```bash
  curl "http://localhost:8000/api/wigs/products/?code=WIG-"
  ```
- Filtre par periode :
  ```bash
  curl "http://localhost:8000/api/wigs/care/?start_date=2024-01-01&end_date=2024-12-31"
  ```

## Endpoints inventaire

Exemples pour l'inventaire :

- Créer un article :
  ```bash
  curl -X POST "http://localhost:8000/api/inventory/items/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Shampoing", "category": "CONSUMABLE", "min_stock": 5}'
  ```
- Enregistrer une entrée :
  ```bash
  curl -X POST "http://localhost:8000/api/inventory/moves/" \
    -H "Content-Type: application/json" \
    -d '{"item": 1, "qty": 10, "type": "IN", "reference": "Achat"}'
  ```

## Endpoints tâches

Exemples pour les tâches :

- Créer une tâche :
  ```bash
  curl -X POST "http://localhost:8000/api/tasks/tasks/" \
    -H "Content-Type: application/json" \
    -d '{"title": "Nettoyer la cabine", "assigned_to": 2}'
  ```
- Mettre à jour le statut :
  ```bash
  curl -X POST "http://localhost:8000/api/tasks/tasks/1/set_status/" \
    -H "Content-Type: application/json" \
    -d '{"status": "DONE"}'
  ```

## LMS (API)

Authentification : JWT ou session Django (mêmes endpoints API).

Schéma OpenAPI :
```bash
curl "http://localhost:8000/api/schema/"
```

Endpoints principaux :
- Cours/modules/leçons : `GET /api/lms/courses/`, `GET /api/lms/modules/`, `GET /api/lms/lessons/`
- Inscriptions : `POST /api/lms/enrollments/`
- Progression leçon : `POST /api/lms/lessons/{id}/mark_viewed/`
- Quiz : `POST /api/lms/quizzes/{id}/submit/`
- Devoirs : `POST /api/lms/assignments/{id}/submit/`
- Badges : `GET /api/lms/badges/`
- Certificats : `GET /api/lms/certificates/`, `GET /api/lms/certificates/{id}/download/`

Exemple (JWT) :
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/lms/courses/"
```

## Tâches récurrentes

Pour créer les modèles réseaux sociaux standards :

```bash
python manage.py seed_social_tasks
```

Pour générer les tâches du jour (idempotent) :

```bash
python manage.py generate_recurring_tasks
```

## Planner social media

Créer des exemples de contenu :

```bash
python manage.py seed_content_examples
```

Actions principales :

- Soumettre à validation :
  ```bash
  curl -X POST "http://localhost:8000/api/content/items/1/submit_for_approval/"
  ```
- Valider (OWNER) :
  ```bash
  curl -X POST "http://localhost:8000/api/content/items/1/approve/" \
    -H "Content-Type: application/json" \
    -d '{"comment": "Validé"}'
  ```
- Refuser (OWNER) :
  ```bash
  curl -X POST "http://localhost:8000/api/content/items/1/reject/" \
    -H "Content-Type: application/json" \
    -d '{"comment": "À revoir"}'
  ```
- Publier :
  ```bash
  curl -X POST "http://localhost:8000/api/content/items/1/publish/"
  ```
- Ajouter des métriques :
  ```bash
  curl -X POST "http://localhost:8000/api/content/items/1/add_metrics/" \
    -H "Content-Type: application/json" \
    -d '{"likes": 120, "comments": 10, "shares": 5, "saves": 8, "reach": 1200, "clicks": 30}'
  ```

## Dashboard rendement

Endpoint (OWNER/ADMIN) :

```bash
curl "http://localhost:8000/reporting/dashboard/rendement"
```

Exemple de réponse :

```json
{
  "taches": {
    "terminees": 12,
    "en_retard": 3
  },
  "contenus_par_plateforme": {
    "Instagram": 5,
    "TikTok": 2
  },
  "taux_validation": {
    "approuves": 4,
    "soumis": 6,
    "taux": 66.67
  },
  "score_moyen_contenu": 12.5
}
```

## Intégration Loyverse

Configurer le jeton (ADMIN) :

```bash
curl -X POST "http://localhost:8000/api/integrations/loyverse-stores/" \
  -H "Content-Type: application/json" \
  -d '{"token": "votre_jeton"}'
```

Lier un paiement à une activité (MANAGER/ADMIN) :

```bash
curl -X POST "http://localhost:8000/api/activities/1/link_payment/" \
  -H "Content-Type: application/json" \
  -d '{"manual_reference": "Paiement caisse", "final_amount": "150.00"}'
```

Synchroniser les reçus Loyverse :

```bash
python manage.py sync_loyverse_receipts
```

Synchroniser depuis une date précise :

```bash
python manage.py sync_loyverse_receipts --since "2024-01-01T00:00:00"
```

## Qualité & outillage

- Lint : `ruff check .`
- Format : `black .`
- Pré-commit (optionnel) : `pre-commit install`
- Si `black` est lent, ciblez des dossiers ou fichiers spécifiques.

## Dépannage

- Migrations en erreur : `python manage.py makemigrations` puis `python manage.py migrate`.
- Réinitialiser SQLite : supprimez `db.sqlite3` puis relancez les migrations.
- Tests : `python manage.py test` ou `pytest`.
- Docker : `docker compose up --build` puis `docker compose exec web python manage.py migrate`.
- Compte admin local (si besoin) : utilisateur `floxy` / mot de passe `walid`.
- Prestations & formation : relancez `python manage.py migrate` pour rejouer les seeds.

## Étiquette d'entretien

Pour imprimer une étiquette PDF pour une perruque en entretien :

```bash
curl -o etiquette.pdf "http://localhost:8000/wigs/care-wigs/1/label.pdf"
```

Imprimez le fichier puis attachez-le à la perruque avant remise en atelier.

Le format est optimisé pour une étiquette 80x50 mm. Le logo par défaut utilise
`logo_floxymade_small.png` à la racine du projet. Vous pouvez le remplacer en
définissant `FLOXY_LOGO_PATH` dans les paramètres Django (chemin local PNG/JPG).

## Prestations

Les prestations (services) Floxy Made alimentent :

- La création d'activités (sélection + calcul automatique du montant attendu).
- Les tableaux du dashboard (mix, CA, ticket moyen).
- Les visuels d'appui dans les écrans activités et formation.
- Le volet POS : `http://localhost:8000/prestations/`

Après un `python manage.py migrate`, les prestations principales sont seedées.

Filtres dashboard (exemples) :

- Filtrer par catégorie :
  ```bash
  http://localhost:8000/dashboard/?sector=Coiffure%20%26%20tresses
  ```
- Filtrer par prestation :
  ```bash
  http://localhost:8000/dashboard/?service=1
  ```

## Formation & reporting

Pages utiles :

- Accueil formation : `http://localhost:8000/formation/`
- Programme : `http://localhost:8000/formation/programme/1/`
- Reporting : `http://localhost:8000/formation/reporting/`

Exports PDF :

- Plan de formation : `http://localhost:8000/formation/programme/1/plan.pdf`
- Rapport global : `http://localhost:8000/formation/reporting/global.pdf`
- Progression d'un participant : `http://localhost:8000/formation/reporting/enrollment/1/progress.pdf`

Accès : le reporting global et les PDF d'équipe sont réservés aux rôles OWNER/ADMIN/MANAGER.

## Captures d'écran

Pour réaliser des captures :

1. Lancez le serveur : `python manage.py runserver`.
2. Ouvrez les pages :
   - `http://localhost:8000/dashboard/`
   - `http://localhost:8000/activites/`
   - `http://localhost:8000/perruques-entretien/`
   - `http://localhost:8000/taches/`
   - `http://localhost:8000/contenus/`
3. Utilisez l'outil de capture de votre système.

## Applications

- accounts
- crm
- operations
- wigs
- inventory
- tasks
- content
- integrations
- reporting
