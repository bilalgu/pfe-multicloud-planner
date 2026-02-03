# BACKLOG - Multi-Cloud Planner

## P0

### Déploiement AWS réel

**1. Validation syntaxe Terraform générée**

- Exécuter `terraform validate` sur code généré avant déploiement
- Détecter erreurs syntaxe/configuration
- Retourner erreurs claires si invalide
- Fichiers : `backend/modules/terraform_gen.py`

**2. Pipeline déploiement AWS automatique**

- Terraform apply depuis backend Flask
- Gérer credentials AWS (IAM role ou variables environnement)
- Endpoint POST /api/deploy pour exécuter apply
- Logs déploiement temps réel (streaming vers frontend)
- Retourner IPs publiques, IDs ressources AWS, endpoints créés
- Confirmation utilisateur avant apply (bouton UI)
- Terraform destroy automatique en cas erreur (rollback)
- Fichiers : `backend/app.py`, `backend/modules/terraform_deploy.py` (nouveau)

### Corrections

**3. Gestion sécurisée des secrets**

- Actuellement : GEMINI_API_KEY dans `backend/.env` (local uniquement)
- Implémenter AWS Secrets Manager pour production
- Variables environnement sécurisées
- Fichiers : `backend/modules/nlp.py`, configuration déploiement

**4. Gestion quota Gemini**

- Monitoring limites API Gemini (https://aistudio.google.com/app/usage)
- Alertes si approche limite quota
- Fallback automatique vers mode mock si quota dépassé
- Rate limiting côté backend déjà implémenté
- Fichiers : `backend/modules/nlp.py`

**5. Load Balancer AWS - générer 2+ subnets**

- Problème actuel : ALB génère 1 seul subnet (erreur AWS minimum 2 AZ)
- Générer au minimum 2 subnets dans 2 Availability Zones différentes
- Fichiers : `backend/modules/terraform_gen.py`

### UI temps réel

**6. Affichage logs déploiement en temps réel**

- Streaming logs terraform apply vers frontend (WebSocket ou SSE)
- Afficher progression étape par étape
- Fichiers : `backend/app.py`, `frontend/app/page.tsx`

**7. Animation/spinner pendant déploiement**

- Indicateur visuel clair pendant terraform apply
- États : "Validating" → "Deploying" → "Success/Error"
- Composant LoadingSpinner déjà existant à enrichir
- Fichiers : `frontend/app/components/LoadingSpinner.tsx`

**8. Affichage ressources créées**

- IPs publiques des serveurs
- IDs ressources AWS (instance-id, vpc-id, etc.)
- Endpoints base de données, load balancers
- Carte visuelle des ressources déployées
- Fichiers : `frontend/app/page.tsx`

**9. État visuel clair**

- Statuts : "deploying" → "success" → "resources"
- Code couleur (bleu en cours, vert succès, rouge erreur)
- Timeline visuelle du déploiement
- Fichiers : `frontend/app/page.tsx`

---

## P1 - IMPORTANT

**10. Génération Ansible**

- Générer playbooks Ansible en plus de Terraform
- Configuration post-déploiement (packages, services, configs)
- Fichiers : `backend/modules/ansible_gen.py` (nouveau)

**11. Extension pipeline multi-cloud**

- Étendre déploiement automatique à Azure et GCP
- Après validation AWS fonctionnel
- Gérer credentials multi-cloud (Azure Service Principal, GCP Service Account)
- Fichiers : `backend/modules/terraform_deploy.py`

**12. Multi-cloud testé et validé**

- AWS et GCP : déjà testés
- Azure : corriger règles vérification trop strictes
- OpenStack : tester et valider
- Fichiers : `backend/modules/security_rules.py`, `backend/tests/`

### Robustesse

**13. Pipeline stable sans dépendance IA**

- Actuellement : fallback basique si Gemini fail
- Améliorer parser fallback avec règles regex/NLP
- Garantir disponibilité même si Gemini down
- Fichiers : `backend/modules/nlp.py`

**14. Améliorer système scoring sécurité**

- Problèmes actuels : pénalités arbitraires, seuil unique 70
- Score pondéré par nombre ressources
- Seuils adaptatifs selon provider
- Catégories risque plus granulaires
- Rapport détaillé avec recommandations actionnables
- Fichiers : `backend/modules/security_rules.py`, `backend/modules/security.py`

**15. Tests exhaustifs supplémentaires**

- Tests actuels : 23 tests passent
- Ajouter : combinaisons complexes (serveurs + DB + LB multi-provider)
- Nombres extrêmes (100 serveurs, 0 de tout)
- Phrases ambiguës ou contradictoires
- Performance/charge (requêtes simultanées)
- Gemini timeout/rate limit
- Fichiers : `backend/tests/test_integration.py` (nouveau)

### Fonctionnalités manquantes

**16. Spécificité type de BDD**

- Actuellement : détecte juste compteur databases: 1
- Détecter MySQL vs PostgreSQL vs MariaDB dans phrase
- Générer Terraform avec engine approprié
- Fichiers : `backend/modules/nlp.py`, `backend/modules/terraform_gen.py`

**17. Support plusieurs régions**

- Actuellement : région hardcodée par provider
- Détecter région dans phrase utilisateur ("us-east-1", "eu-west-1")
- Ou permettre sélection région dans UI
- Générer Terraform avec région appropriée
- Fichiers : `backend/modules/nlp.py`, `backend/modules/terraform_gen.py`

**18. Retirer flask-cors si inutile**

- CORS activé alors que proxy Next.js utilisé
- Supprimer dépendance une fois proxy validé
- Fichiers : `backend/app.py`, `backend/requirements.txt`

---

## P2/P3/P4 - À voir une fois P0/P1 terminés

Les priorités P2, P3 et P4 seront utiles uniquement si P0 et P1 sont validés.

Exemples d'items P2+ :

- Hébergement production (EC2, Vercel)
- UI/UX avancée (diagrammes architecture, éditeur Monaco)
- Documentation API (OpenAPI/Swagger)
- Dockerisation corrigée
- CI/CD Pipeline
- Cache réponses (Redis)
- Multi-utilisateurs + authentification
- Dashboard métriques
- Estimation coûts
