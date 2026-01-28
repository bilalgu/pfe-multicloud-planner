# Tests Backend

## Tests fonctionnels

### 1. Serveur AWS simple

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux un serveur AWS"}'
```

**Attendu** : `security=OK`, Terraform genere avec VPC + SG + serveur

---

### 2. Base de donnees privee

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux une base de donnees MySQL privee"}'
```

**Attendu** : `security=OK`, Terraform genere avec VPC + SG + DB

---

### 3. Base de donnees publique (bloquee)

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux une base de donnees MySQL publique"}'
```

**Attendu** : `security=NOT_OK`, `terraform=BLOCKED`, `dangerous_requests` present

---

### 4. Sans chiffrement (bloquee)

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux une base sans chiffrement"}'
```

**Attendu** : `security=NOT_OK`, `terraform=BLOCKED`, `dangerous_requests` present

---

### 5. SSH ouvert (bloquee)

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux un serveur avec SSH ouvert au public"}'
```

**Attendu** : `security=NOT_OK`, `terraform=BLOCKED`, `dangerous_requests` present

---

### 6. Infrastructure complete

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux 3 serveurs AWS avec une base de donnees MySQL privee"}'
```

**Attendu** : `security=OK`, Terraform avec 3 serveurs + DB + VPC + SG

---

### 7. Multi-cloud GCP

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux 2 serveurs GCP avec une base de donnees"}'
```

**Attendu** : `security=OK`, Terraform GCP genere

---

### 8. Multi-cloud Azure

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux un serveur Azure"}'
```

**Attendu** : `security=NOT_OK` (score 40), syntaxe Terraform valide

---

## Tests d'erreur

### 9. Phrase vide

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": ""}'
```

**Attendu** : `400 Bad Request`, message "Description vide"

---

### 10. JSON invalide

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

**Attendu** : `400 Bad Request`, message "JSON invalide"

---

## Providers supportes

| Provider  | Status        | Score typique | Note                                             |
| --------- | ------------- | ------------- | ------------------------------------------------ |
| AWS       | Teste       | 70-80         | Completement fonctionnel                         |
| GCP       | Teste       | 70            | Completement fonctionnel                         |
| Azure     | Syntaxe OK | 40            | Regles verification trop strictes (`BACKLOG.md`) |
| OpenStack | Non teste  | -             | Syntaxe implementee, non valide                  |
