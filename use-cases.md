# Use cases

| Input                                | Résultat attendu                       |
| ------------------------------------ | -------------------------------------- |
| "Créer une base de données privée"   | `security=OK`, `terraform=GENERATED`   |
| "Créer une base de données publique" | `security=NOT_OK`, `terraform=BLOCKED` |
| "" (phrase vide)                     | `400 Empty phrase`                     |
| Gemini indisponible                  | `502 AI generation failed`             |
| ==JSON invalide (en cours)==         | `422 Invalid JSON schema`              |

---

## Tests

### 1. Base privée → autorisée

```bash
curl -i --get "http://localhost:3001/api/gen" \
  --data-urlencode "phrase=Créer une base de données privée"
```

### 2. Base publique → bloquée

```bash
curl -i --get "http://localhost:3001/api/gen" \
  --data-urlencode "phrase=Créer une base de données publique"
```

### 3. Phrase vide

```bash
curl -i "http://localhost:3001/api/gen?phrase="
```

### 4. Gemini indisponible

Mettre une mauvaise clé dans `.env` puis :

```bash
curl -i --get "http://localhost:3001/api/gen" \
  --data-urlencode "phrase=test"
```
