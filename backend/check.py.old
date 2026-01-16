import json
import sys

# Recupere le chemin du fichier JSON passe en argument
path = sys.argv[1]

# Ouvre et lit le fichier JSON
with open(path,"r") as f:
    data = json.load(f)

# Récupère la valeur "publicly_accessible" dans resources.database
# Si la clé n'existe pas, on considere False par default
is_public = data.get("resources", {}).get("database", {}).get("publicly_accessible", False)

# Affiche OK / NOT OK si if_public True or False
if is_public:
    print("NOT_OK")
    sys.exit(1)
else:
    print("OK")
    sys.exit(0)
