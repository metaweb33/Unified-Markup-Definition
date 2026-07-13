# Plugin de gestion des séparateurs
# Importation absolue depuis la racine du projet (Lecteur/)
from plugins.plugin_color import extract_param

# Plugin de gestion des séparateurs

def parse_separator(line):
    print("SEPARATOR:", repr(line))
    
    if not line.startswith("++"):
        return None

    raw_content = line[2:].strip()

    # Si c'est juste "++", c'est une ligne simple par défaut
    if not raw_content:
        return {
            "type": "separator",
            "kind": "line",
            "params": {}
        }

    # Extraction de tous les couples (caractère + couleur)
    tokens = []
    remaining = raw_content
    
    while remaining:
        if "{" in remaining:
            idx = remaining.find("{")
            char_part = remaining[:idx] # Ce qui est avant l'accolade (ex: "#")
            
            end_idx = remaining.find("}")
            if end_idx != -1 and end_idx > idx:
                param_content = remaining[idx+1:end_idx].strip()
                
                # Extraction propre de la couleur
                color = None
                if param_content:
                    if "=" in param_content:
                        parts = param_content.split("=")
                        if parts[0].strip() == "color":
                            color = parts[1].strip()
                    else:
                        color = param_content
                
                tokens.append({
                    "char": char_part,
                    "color": color
                })
                remaining = remaining[end_idx+1:]
            else:
                # Pas d'accolade de fermeture valide, on prend tout le reste en brut
                tokens.append({"char": remaining, "color": None})
                remaining = ""
        else:
            # Plus d'accolades, tout le reste est du motif brut
            tokens.append({"char": remaining, "color": None})
            remaining = ""

    # --- ANALYSE DES TOKENS POUR LE RENDU ---
    
    # Cas 1 : Un seul bloc (Garde la compatibilité avec l'existant : ++, ++{red}, ++=, ++#)
    if len(tokens) == 1:
        token = tokens[0]
        char_stripped = token["char"].strip()
        color = token["color"]
        
        if not char_stripped:
            return {"type": "separator", "kind": "line", "params": {"color": color}}
        elif char_stripped == ":":
            return {"type": "separator", "kind": "dotted", "params": {"color": color}}
        elif char_stripped == "=":
            return {"type": "separator", "kind": "double", "params": {"color": color}}
        elif char_stripped == "~":
            return {"type": "separator", "kind": "wave", "params": {"color": color}}
        elif char_stripped == "!":
            return {"type": "separator", "kind": "dashed", "params": {"color": color}}
        else:
            return {
                "type": "separator",
                "kind": "repeat",
                "pattern": token["char"], # On garde la chaîne brute (avec espaces volontaires)
                "params": {"color": color}
            }
            
    # Cas 2 : Plusieurs blocs détectés ! Alternance complexe (ex: ++#{red}#{blue})
    else:
        return {
            "type": "separator",
            "kind": "repeat",
            "pattern": tokens, # On passe directement la liste des motifs colorés
            "params": {}
        }