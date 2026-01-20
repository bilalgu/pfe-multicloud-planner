# BACKLOG - Améliorations futures

## P0 - Critique (robustesse backend actuel)

1. **Validation schema JSON généré**
   - Actuellement : aucune validation du JSON Gemini
   - Vérifier présence champs obligatoires (provider, servers, databases, etc.)
   - Si invalide → erreur claire "Invalid JSON schema from AI"
   - Éviter erreurs en cascade dans génération Terraform

2. **Timeouts et gestion erreurs robuste**
   - Actuellement : pas de timeout sur appels Gemini
   - Implémenter timeout 30s sur génération
   - Try/catch exhaustif autour de chaque étape
   - Messages d'erreur clairs pour l'utilisateur

3. **Pipeline stable sans dépendance IA**
   - Si Gemini fail/timeout/quota → fallback actuel basique
   - Améliorer fallback pour gérer plus de cas
   - Parser phrase avec règles simples (regex/NLP basique)
   - Garantir disponibilité même si Gemini down

4. **Rate limiting requêtes**
   - Éviter requêtes infinies vers Gemini
   - Limite simple : max 10 requêtes/minute par IP
   - Compteur in-memory (ou Redis si production)
   - Retourner 429 Too Many Requests si dépassé

5. **Gestion quota Gemini**
   - Quota gratuit : vérifier limites
   - URL monitoring : https://aistudio.google.com/app/usage
   - Implémenter rate limiting côté backend
   - Alertes si approche limite quota

---

## P1 - Important (après intégration frontend)

6. **Retirer flask-cors si inutile**
   - À supprimer une fois proxy Next.js validé

7. **Validation syntaxe Terraform générée**
   - Actuellement : aucune validation syntaxique automatique
   - À implémenter : `terraform validate` sur code généré
   - Permettrait de détecter erreurs syntaxe avant utilisateur

8. **Mode mock AI (dev sans API)**
   - Variable d'environnement AI_MODE=mock
   - Retourner JSON fixture au lieu d'appeler Gemini
   - Évite consommation quota pendant dev/tests
   - Accélère tests automatisés

9. **Tests unitaires automatisés**
   - Actuellement : tests manuels avec curl
   - Implémenter tests automatisés (pytest)
   - Couvrir :
     * Cas nominaux (serveur, DB, multi-cloud)
     * Cas erreurs (phrase vide, JSON invalide)
     * Cas blocages (DB publique, SSH ouvert)
   - CI/CD : exécuter tests avant merge

10. **Journal minimal des runs**
    - Sauvegarder derniers runs dans logs/history.json
    - Format : timestamp, phrase, json, security, terraform_status
    - Permet debugging et traçabilité
    - Optionnel : endpoint /api/history

11. **Gestion sécurisée des secrets**
    - Actuellement : GEMINI_API_KEY dans .env (local uniquement)
    - Solutions :
      * Secrets manager (AWS Secrets Manager, GCP Secret Manager)
      * Vault HashiCorp

---

## P2 - Nice to have (qualité)

12. **Améliorer règles de vérification security_rules.py**
    - Règles actuelles cherchent mots-clés AWS spécifiques
    - Azure/GCP échouent car termes différents (ex: pas "encrypted" dans Azure VM)
    - DB seule score 40 alors que sécurisée
    - Solutions possibles :
      * Règles spécifiques par provider
      * Ou vérification structurelle (pas juste mots-clés)
    - Exemple concret : Azure VM échoue encryption_at_rest (pas de mot "encrypted")

13. **Améliorer système de scoring sécurité**
    - Problèmes actuels :
      * Score basé sur pénalités arbitraires (CRITICAL=30, HIGH=20, MEDIUM=10)
      * Seuil unique 70 pour tous les cas
      * Pas de pondération par contexte (serveur seul vs infrastructure complète)
      * Règles cherchent mots-clés (pas robuste multi-cloud)
    - Améliorations possibles :
      * Score pondéré par nombre de ressources
      * Seuils adaptatifs selon provider
      * Vérification structurelle (AST Terraform) au lieu de mots-clés
      * Catégories de risque plus granulaires
      * Rapport détaillé avec recommandations actionnables
    - Objectif : score plus cohérent et informatif

14. **Tests exhaustifs supplémentaires**
    - 10 tests validés actuellement (`backend/TESTS.md`)
    - Tests manquants à explorer :
      * Combinaisons complexes (serveurs + DB + LB multi-provider)
      * Nombres extrêmes (100 serveurs, 0 de tout)
      * Phrases ambiguës ou contradictoires
      * Performance/charge (multiple requêtes simultanées)
      * Gemini timeout/rate limit
      * Validation syntaxe Terraform générée (terraform validate)
    - Découvrir comportements inattendus avant production

15. **Multi-cloud testé et validé**
    - Multi-cloud implémenté (AWS/Azure/GCP/OpenStack)
    - Seuls AWS et GCP testés et validés
    - Azure : syntaxe OK mais règles vérification trop strictes
    - OpenStack : non testé

16. **Ajouter génération Load Balancer**
    - Gemini détecte correctement load_balancers
    - Mais terraform_gen.py ne les génère pas
    - À implémenter : boucle génération LB AWS/Azure/GCP

17. **Spécificité type de BDD**
    - Détecter MySQL vs PostgreSQL vs MariaDB
    - Pour l'instant : juste compteur `databases: 1`
    - Pas bloquant pour sécurité

---

## P3 - Features avancées (hors scope PoC)

18. **Génération Ansible**
    - Dans PR de Mariam
    - Hors scope P0
    - Branche `feature/advanced-backend` à créer

19. **Déploiement sur cloud**
    - Actuellement : local uniquement (localhost:5000)
    - Options deployment :
      * AWS : EC2 + RDS ou ECS/Fargate
      * GCP : Cloud Run + Cloud SQL
      * Azure : App Service + Azure SQL
      * Vercel (frontend) + Railway/Render (backend)
    - CI/CD : GitHub Actions
    - Monitoring et logs production

20. **Features production**
    - Terraform apply automatique depuis UI
    - Hosting cloud (Vercel frontend + Lambda/EC2 backend)
    - Logs structurés et centralisés (CloudWatch/Datadog)
    - Alerting (échecs sécurité, dépassement coûts)
    - UI avancée (dashboard métriques, visualisation architecture)
    - Multi-utilisateurs avec authentification