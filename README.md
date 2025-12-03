# PoC - Planificateurs multi-niveaux d’architectures

## Pipeline du PoC (version minimale)

```
Phrase → IA → JSON → (Sécurité) → Terraform → Deploy
```

Dans la V1, la sécurité intervient avant la génération Terraform.

Pourquoi ?
- plus simple
- rapide à valider
- testable immédiatement
- idéal pour assembler tous les blocs la semaine prochaine

La sécurité post-Terraform (analyse du code .tf) viendra plus tard, car plus réaliste mais plus complexe.

## Rôle de la sécurité

La règle de sécurité sert de garde-fou :

- empêche un JSON dangereux d’aller vers Terraform  
- évite de déployer une infrastructure risquée  
- valide l’idée du projet : génération d’infrastructure sécurisée  

## Objectif

Créer une règle de sécurité simple, testable, basée sur le JSON, avec un script Python qui renvoie :

- `OK` → JSON conforme  
- `NOT OK` → JSON dangereux  

## Scope

### Inclus

- 1 seule règle
- JSON comme entrée  
- Script Python minimal :
	- lire le JSON  
	- vérifier 1 condition  
	- afficher OK / NOT OK  
- 2 JSON de test : `good.json` et `bad.json`

## Règle de sécurité

1er règle :  La base de données ne doit pas être publique  
> (champ `publicly_accessible` interdit à `true`)

**Pourquoi ?**

Dans AWS une base de données publique est accessible depuis Internet, cela viole immédiatement les bonnes pratiques de sécurité 

## Test

```bash
python3 check.py bad.json  
python3 check.py good.json
```

## Références

- https://docs.python.org/3/library/json.html#json.load  
- https://docs.python.org/3/library/stdtypes.html#dict.get  
- https://docs.python.org/3/library/sys.html#sys.argv  
