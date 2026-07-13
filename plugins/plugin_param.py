def extract_param(text):
    # Sécurité : Si ça ne commence pas par '{' ou s'il n'y a pas de '}', on s'arrête
    if not (text.startswith("{") and "}" in text):
        return {}, text

    end = text.find("}")
    content = text[1:end].strip()

    # ---- CAS 1 : BALISES DE FERMETURE / RESET (ex: {/}, {/~}) ----
    if content.startswith('/'):
        target_char = content[1:]  # On récupère le caractère après le '/'
        
        mapping = {
            "": "all",          # {/}
            "&": "all",         # {/&}
            "c": "color",       # {/c}
            "_": "underline",   # {/_}
            "~": "strike",      # {/~}
            "= ": "highlight",   # {/=}
            "*": "font"         # {/*}
        }
        
        target = mapping.get(target_char, "all")
        return {"clear": target}, text[end+1:]

    # ---- CAS 2 : BALISE VIDE (ex: {}) ----
    # On la refuse pour qu'elle reste affichée en texte brut
    if not content:
        return {}, text

    # ---- CAS 3 : BALISES DE STYLE / OUVERTURE (ex: {red}, {highlight=pink}) ----
    params = {}
    if "=" in content:
        # cas clé=valeur
        key, value = content.split("=", 1)
        params[key.strip()] = value.strip()
    else:
        # cas simple => couleur
        params["color"] = content

    return params, text[end+1:]