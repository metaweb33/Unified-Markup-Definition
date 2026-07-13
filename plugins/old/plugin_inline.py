# Plugin de parsing inline
# Inline parser plugin

from plugins.plugin_style import extract_styles
from plugins.plugin_param import extract_param
from plugins.plugin_emoji import extract_emoji
from plugins.plugin_image import extract_image  
from plugins.plugin_icon import extract_icon
from plugins.plugin_qrcode import parse_qrcode

def parse_inline(text):
    segments = [] 
    
    while text: 
        # ---- IMAGE (prioritaire) ----
        image, new_text = extract_image(text) 
        if image: 
            segments.append({ 
                "type": "image", 
                "src": image["src"], 
                "alt": image["alt"],
                "width": image["width"],
                "height": image["height"]
            })
            text = new_text 
            continue 

        # ---- EMOJI ----
        emoji, new_text = extract_emoji(text) 
        if emoji: 
            segments.append({ 
                "type": "emoji", 
                "value": emoji 
            })
            text = new_text 
            continue 

        # ---- ICON ----
        icon, new_text = extract_icon(text)
        if icon:
            segments.append({
                "type": "icon",
                "name": icon.get("icon")
            })
            text = new_text
            continue

        # ---- STYLES + PARAMS ----
        styles = []
        params = {}
        temp = text
        changed = True

        while changed:
            changed = False
            old_temp = temp

            # Extraction styles
            new_styles, new_temp = extract_styles(temp)
            if new_styles and new_temp != old_temp:
                styles.extend(new_styles)
                temp = new_temp
                changed = True

            # Extraction params
            new_params, new_temp = extract_param(temp)
            if new_params and new_temp != old_temp:
                params.update(new_params)
                temp = new_temp
                changed = True

        # ---- TRAITEMENT DU CONTENU DE LA BALISE OU DU TEXTE ----
        if temp != text:
            # Interception de la balise de fermeture {&}
            if params.get("clear") or "{&}" in text[:len(text)-len(temp)]:
                segments.append({
                    "type": "clear_style"
                })
                text = temp # On passe directement à la suite (' normal') au prochain tour
                continue

            # On a trouvé des styles ou des params valides (non vides)
            content = ""
            i = 0
            while i < len(temp) and temp[i] not in "{*[_":
                content += temp[i]
                i += 1

            if content:
                node = {
                    "type": "styled",
                    "text": content
                }
                if styles:
                    node["styles"] = styles
                if params:
                    node["params"] = params
                segments.append(node)
                text = temp[i:]
            else:
                # Sécurité : Si aucun texte ne suit mais qu'on a accumulé des modificateurs,
                # on avance text pour éviter de boucler sur place
                text = temp
        else:
            # Aucun style/param trouvé au début -> On consomme du texte brut
            content = ""
            i = 0
            while i < len(text) and text[i] not in "{*[_":
                content += text[i]
                i += 1

            if i == 0:
                # Sécurité anti-boucle : on force la consommation d'un caractère spécial
                segments.append({
                    "type": "text",
                    "text": text[0]
                })
                text = text[1:]
            else:
                segments.append({
                    "type": "text",
                    "text": content
                })
                text = text[i:]

    return {
        "type": "inline",
        "segments": segments
    }