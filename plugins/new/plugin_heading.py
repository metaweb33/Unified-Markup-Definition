# Plugins/plugin_heading.py
import re
from plugins.plugin_param import extract_param

def parse_simple_heading(line):
    level = 0
    # 1. Compter les # pour le niveau
    for c in line:
        if c == "#":
            level += 1
        else:
            break

    # On récupère tout ce qui suit les #
    content = line[level:].strip()

    # 2. Extraction de l'alignement (<<, ><, >>)
    align = None
    if "><" in content:
        align = "center"
        content = content.replace("><", "", 1)
    elif "<<" in content:
        align = "left"
        content = content.replace("<<", "", 1)
    elif ">>" in content:
        align = "right"
        content = content.replace(">>", "", 1)

    # 3. Extraction des styles de bloc (_, **, *, ~~)
    styles = []
    
    # On cherche les marqueurs en début de chaîne restante
    if content.startswith("~~"):
        styles.append("strikethrough")
        content = content[2:]
    
    if content.startswith("**"):
        styles.append("bold")
        content = content[2:]
    elif content.startswith("*"):
        styles.append("italic")
        content = content[1:]
        
    if content.startswith("_"):
        styles.append("underline")
        content = content[1:]

    # On ré-effectue une vérification au cas où ils seraient combinés dans un autre ordre (ex: _**)
    if content.startswith("**") and "bold" not in styles:
        styles.append("bold")
        content = content[2:]
    elif content.startswith("*") and "italic" not in styles:
        styles.append("italic")
        content = content[1:]

    content = content.strip()

    # 4. Extraction des paramètres (ex: {blue}) via votre plugin_param
    params = {}
    if content.startswith("{"):
        extracted_params, remaining_text = extract_param(content)
        if extracted_params and not extracted_params.get("clear"):
            params = extracted_params
            content = remaining_text.strip()

    return {
        "type": "block",
        "structure": "heading",
        "level": level,
        "styles": styles,
        "params": params,
        "align": align,
        "content": content,
        "raw": line
    }