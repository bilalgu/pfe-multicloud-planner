import json
import sys

# Recupere le chemin du fichier JSON passe en argument
path = sys.argv[1]

# Ouvre et lit le fichier JSON
with open(path,"r") as f:
    data = json.load(f)

# Récupère la valeur "publicly_accessible" dans resources.database
# Si la clé n'existe pas, on considere False par default
# === A mettre dans la pipeline du PoC aussi ===
is_public = data.get("resources", {}).get("database", {}).get("publicly_accessible", False)

# Affiche OK / NOT OK si if_public True or False
if is_public:
    print("NOT OK: la base de donnees est publique (interdit)")
else:
    print("OK : la base de donnees n'est pas publique")
