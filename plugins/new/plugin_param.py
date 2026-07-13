# Plugin de parsing des couleurs
# Color and font and size parser plugin

def extract_param(text):
    if text.startswith("{") and "}" in text:
        end = text.find("}")
        content = text[1:end].strip()

        # Balise spécifique de fermeture/reset : {&}
        if content == "&":
            return {"clear": True}, text[end+1:]

        # Si c'est juste vide {}, on refuse l'extraction pour que ça reste du texte brut
        if not content:
            return {}, text

        # cas clé=valeur
        params = {}
        if "=" in content:
            key, value = content.split("=", 1)
            params[key.strip()] = value.strip()
        else:
            # cas simple => couleur
            params["color"] = content

        return params, text[end+1:]

    return {}, text