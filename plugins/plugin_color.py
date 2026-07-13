# Plugin de parsing des couleurs
# Color parser plugin

def extract_param(text):
    if text.startswith("{") and "}" in text:
        end = text.find("}")
        content = text[1:end].strip()

        params = {}
        if not content:
            # Balise {} trouvée et consommée (on renvoie un dict vide, mais valide)
            return params, text[end+1:]

        # cas clé=valeur
        if "=" in content:
            key, value = content.split("=", 1)
            params[key.strip()] = value.strip()
        else:
            # cas simple => couleur
            params["color"] = content.strip()

        return params, text[end+1:]

    # IMPORTANT : On renvoie None si aucune accolade n'est présente au début
    return None, text