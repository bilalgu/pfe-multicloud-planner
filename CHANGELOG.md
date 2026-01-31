# Changelog

Historique des changements du projet.

## [0.4.2] - 2026-01-31 (Bilal)

### Ajouté
- **Limites pédagogiques sur ressources** : Maximum 50 serveurs, 10 databases, 5 load balancers par provider
- Messages d'erreur pédagogiques avec recommandations Terraform (count/for_each)
- Gestion intelligente des requêtes vagues : génère 1 serveur AWS minimum
- Validation Pydantic avec limites (`le=50`, `le=10`, `le=5`)

### Modifié
- `backend/modules/nlp.py` : Limites ajoutées dans ProviderConfig + gestion ValidationError
- `backend/app.py` : Encodage UTF-8 pour accents français (`JSON_AS_ASCII = False`)
- Prompt Gemini : Règle pour requêtes vagues

### Testé
- "1000 serveurs AWS" → Message pédagogique avec recommandation count
- "50 serveurs AWS" → Génération OK (limite exacte)
- "-5 serveurs AWS" → Gemini corrige automatiquement → 5 serveurs
- "5 serveurs DigitalOcean" → Fallback AWS
- "Je veux une infra" → Génère 1 serveur AWS minimum

---

## [0.4.1] - 2026-01-31 (Bilal)

### Ajouté
- **Support database_type** : Spécification du type de base de données (mysql, postgresql, mongodb, mariadb)
- Validation Pydantic pour database_type avec fallback MySQL
- Génération Terraform adaptée selon le type de database
- Mapping intelligent des engines par provider :
  - AWS : mysql, postgres, mariadb, docdb (MongoDB)
  - GCP : MYSQL_8_0, POSTGRES_16
  - Azure : azurerm_mysql_server, azurerm_postgresql_server, azurerm_mariadb_server

### Modifié
- `backend/modules/nlp.py` : Nouveau champ `database_type` dans ProviderConfig
- `backend/modules/terraform_gen.py` : Génération databases avec type dynamique
- Prompt Gemini AI : Instructions pour détecter MongoDB, PostgreSQL, MariaDB

### Testé
- "3 serveurs avec MongoDB" → AWS DocumentDB
- "5 serveurs avec PostgreSQL" → AWS RDS PostgreSQL
- "3 serveurs GCP avec MongoDB + 2 serveurs AWS avec PostgreSQL" → Multi-cloud + multi-database

---

## [0.4.0] - 2026-01-31 (Bilal)

### Ajouté
- **Support multi-provider dans une même requête** : Possibilité de combiner plusieurs providers (ex: "3 serveurs GCP + 2 serveurs AWS")
- Nouveau schéma Pydantic `ProviderConfig` pour validation par provider
- Agrégation automatique des statistiques multi-provider dans le frontend
- Génération Terraform multi-cloud avec sections séparées par provider
- Tests unitaires adaptés au format multi-provider (23 tests passent)

### Modifié
- `backend/modules/nlp.py` : Schéma `InfrastructureSchema` avec liste de `providers`
- `backend/modules/terraform_gen.py` : Fonction `generate_terraform()` boucle sur providers
- `frontend/app/page.tsx` : Affichage agrégé des ressources multi-cloud
- Prompt Gemini AI : Instructions pour extraire plusieurs providers
- Format API : `{"providers": [{"provider": "aws", ...}]}` au lieu de `{"provider": "aws", ...}`

### Rétro-compatible
- Mono-provider continue de fonctionner (liste avec 1 élément)
- Tous les tests existants adaptés sans régression

---

## [0.3.0] - 2026-01-27 (Sira)

### Ajouté
- Validation schéma JSON avec Pydantic
- Timeout 30s sur appels Gemini
- Rate limiting (10 req/min par IP)
- Mode mock AI pour développement sans API
- Génération Load Balancers (AWS/Azure/GCP)
- Règles de sécurité améliorées multi-cloud
- Tests unitaires automatisés (pytest, 23 tests)
- Journal des runs avec endpoint /api/history
- Composants UI améliorés (toasts, spinner, animations)
- Logging structuré avec timestamps
- Documentation complète (CONTRIBUTING.md, QUICKSTART.md)

### Modifié
- Amélioration gestion d'erreurs backend
- Règles de vérification sécurité spécifiques par provider
- Frontend: remplacement alert() par composants visuels
- Configuration Next.js avec headers de sécurité

### Corrigé
- Timeout multiplateforme (signal.SIGALRM → threading.Timer)
- Règles sécurité Azure/GCP qui échouaient incorrectement

### BACKLOG (non intégré)
- Docker (bugs identifiés: paths, ports)
- CI/CD GitHub Actions

## [0.2.0] - 2026-01-21 (Mariam)

### Ajouté
- Architecture Flask modulaire (modules/nlp.py, terraform_gen.py, security.py)
- Support multi-cloud complet (AWS/Azure/GCP/OpenStack)
- 6 règles de sécurité MVP (security_rules.py)
- Détection proactive des demandes dangereuses
- Injection automatique politiques de sécurité dans code généré
- Génération Ansible (retiré temporairement - BACKLOG P3)

### Modifié
- Migration des 3 scripts Python séparés vers architecture Flask unifiée
- Frontend Next.js : proxy vers Flask (route.ts)
- UI simplifiée (suppression Ansible, affichage dangerous_requests)

### Documentation
- backend/README.md (API complète, endpoints, exemples)
- backend/TESTS.md (10 scénarios validés)
- BACKLOG.md (20 améliorations priorisées P0-P3)
- README racine mis à jour (quickstart)

## [0.1.0] - 2026-01-10 (Toute l'équipe)

### Ajouté
- Génération Terraform multi-cloud (AWS/Azure/GCP/OpenStack)
- Validation sécurité avec 6 règles
- Interface Next.js basique
- API Flask avec endpoints /generate et /health