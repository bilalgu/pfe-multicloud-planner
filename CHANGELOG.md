# Changelog

Historique des changements du projet.

## [Unreleased]

### Ajouté
- Validation schéma JSON avec Pydantic
- Timeout 30s sur appels Gemini
- Rate limiting (10 req/min par IP)
- Mode mock AI pour développement sans API
- Génération Load Balancers (AWS/Azure/GCP)
- Règles de sécurité améliorées multi-cloud
- Tests unitaires automatisés (pytest)
- Journal des runs avec endpoint /api/history
- Composants UI améliorés (toasts, loading spinner)
- Logging structuré
- Dockerisation (Dockerfile + docker-compose)
- CI/CD Pipeline (GitHub Actions)
- Documentation améliorée

### Modifié
- Amélioration gestion d'erreurs backend
- Amélioration règles de vérification sécurité (spécifiques par provider)
- Frontend: remplacement alert() par composants visuels
- Configuration Next.js avec headers de sécurité

### Corrigé
- Problème timeout multiplateforme (signal.SIGALRM → threading.Timer)
- Règles sécurité Azure/GCP qui échouaient incorrectement

## [0.1.0] - Version initiale
- Génération Terraform multi-cloud (AWS/Azure/GCP/OpenStack)
- Validation sécurité avec 6 règles
- Interface Next.js basique
- API Flask avec endpoints /generate et /health
