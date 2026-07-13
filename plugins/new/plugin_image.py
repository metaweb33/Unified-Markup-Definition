# Plugin de parsing des images
# Pictures parser plugin

import re

def extract_image(text):
    """
    Analyse une chaîne pour y détecter une image au format Markdown étendu.
    Renvoie un tuple (image_node, new_text) ou (None, text) si aucune image.
    """
    pattern = r'!\[(.*?)\]\((.*?)\)(?:\{(.*?)\})?'
    
    match = re.search(pattern, text)
    if not match:
        # Retourne None pour le nœud, et le texte intact pour la suite du parsing
        return None, text
        
    alt = match.group(1)
    src = match.group(2)
    dimensions = match.group(3)
    
    width = "auto"
    height = "auto"
    
    if dimensions:
        dim_match = re.match(r'(\d+)x(\d+)', dimensions.strip().lower())
        if dim_match:
            width = dim_match.group(1)
            height = dim_match.group(2)
            
    node = {
        "type": "image",
        "src": src,
        "alt": alt,
        "width": width,
        "height": height
    }
    
    # On retire l'image du texte original pour ne pas ré-analyser ce segment
    # (ou pour isoler le reste du texte de la ligne)
    new_text = text[:match.start()] + text[match.endCustom():] if hasattr(match, 'endCustom') else text.replace(match.group(0), "")
    
    return node, new_text

