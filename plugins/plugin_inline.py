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
        # ---- GESTION DES SAUTS DE LIGNE (\n) ----
        # Le saut de ligne hors bloc provoque un reset de style naturel
        # et injecte le segment virtuel de transition pour le reflow
        if text.startswith('\n'):
            segments.append({
                "type": "break",
                "text": "\n"
            })
            text = text[1:]
            continue

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

        # ---- STYLES + PARAMS SÉQUENTIELS (LIAISON DE COULEUR) ----
        styles = []
        params = {}
        temp = text
        
        last_color = None  # Garde en mémoire la couleur qui vient d'être lue

        while temp:
            old_temp = temp

            # 1. On tente d'extraire un paramètre ou une couleur {...}
            new_params, new_temp = extract_param(temp)
            if new_temp != old_temp:
                if "clear" in new_params:
                    params["clear"] = new_params["clear"]  # <-- MODIFIÉ : On préserve la cible ('all', 'color', etc.)
                elif "color" in new_params and len(new_params) == 1:
                    last_color = new_params["color"]
                else:
                    params.update(new_params)
                temp = new_temp
                continue

            # 2. On tente d'extraire un style (__, ~~, **, etc.)
            new_styles, new_temp = extract_styles(temp)
            if new_temp != old_temp:
                styles.extend(new_styles)
                
                # Si une couleur attendait juste avant ce style, on lui associe spécifiquement
                if last_color:
                    has_decoration = False
                    for s in new_styles:
                        if "strike" in s:
                            params["strike_color"] = last_color
                            has_decoration = True
                        elif "underline" in s or s.startswith("underline"):
                            params["underline_color"] = last_color
                            has_decoration = True
                        elif "highlight" in s:
                            params["highlight_color"] = last_color
                            has_decoration = True
                    
                    # Si ce n'est pas une décoration (ex: juste du gras {red}**),
                    # alors cela devient la couleur par défaut du texte.
                    if not has_decoration:
                        params["color"] = last_color
                    
                    last_color = None  # La couleur a été liée et consommée
                
                temp = new_temp
                continue
            
            # Si on n'a extrait ni paramètre ni style, on sort de la capture de l'en-tête
            break

        if "clear" in params:
            segments.append({
                "type": "clear_style",
                "target": params["clear"]
            })
            text = temp
            continue

        # Securité : Si une couleur a été déclarée seule sans style (ex: {red}Texte)
        if last_color:
            params["color"] = last_color

        # ---- TRAITEMENT DU CONTENU DE LA BALISE OU DU TEXTE ----
        if temp != text:
            # Interception des balises de fermeture / reset
            if "clear" in params or "{}" in text:
                segments.append({
                    "type": "clear_style",
                    "target": params.get("clear", "all")  # "all" par défaut si l'utilisateur écrit juste {}
                })
                text = temp # On passe directement à la suite au prochain tour
                continue

            # Extraction propre du texte : Ajout de \n aux caractères d'arrêt
            content = ""
            i = 0
            while i < len(temp) and temp[i] not in "{*[_\n":
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
                text = temp
        else:
            # Aucun style/param trouvé au début -> On consomme du texte brut courant
            # Ajout de \n aux caractères d'arrêt
            content = ""
            i = 0
            while i < len(text) and text[i] not in "{*[_\n":
                content += text[i]
                i += 1

            if i == 0:
                # Sécurité anti-boucle : on force la consommation du caractère spécial
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