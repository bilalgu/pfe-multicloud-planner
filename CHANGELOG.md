# Changelog

Historique des changements du projet.

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
