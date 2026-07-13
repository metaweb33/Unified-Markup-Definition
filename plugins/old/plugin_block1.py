# Plugin de parsing des blocs UMD
# Block parser plugin

from plugins.plugin_style import extract_styles
from plugins.plugin_param import extract_param
from plugins.plugin_heading import parse_simple_heading
from plugins.plugin_inline import parse_inline

def parse_block(header_line, iterator):
    # 1. On extrait la configuration du bloc en simulant un heading/inline sur la ligne de modificateurs
    # On enlève la tilde de départ pour analyser les styles (~###... devient ###...)
    style_config = parse_simple_heading(header_line[1:]) 
    
    lines_content = []
    
    # 2. On consomme l'itérateur jusqu'à la balise de fermeture ~
    for line in iterator:
        clean_line = line.rstrip()
        if clean_line == "~":
            break
        lines_content.append(clean_line)
        
    # 3. On assemble le nœud AST final
    return {
        "type": "multi_line_block",
        "structure": style_config.get("structure", "paragraph"),
        "level": style_config.get("level"),
        "styles": style_config.get("styles", []),
        "params": style_config.get("params", {}),
        "align": style_config.get("align", "center"), # ex: "center" si "><" était présent
        "lines": [parse_inline(l) for l in lines_content], # Chaque ligne garde son parsing inline interne
        "raw_lines": lines_content
    }

def parse_block(line):
    """
    FR: Parse une ligne commençant par "~"
    EN: Parse a block line starting with "~"
    """

    # ---- INIT ----
    header = line[1:]  # retirer "~"

    structure = None
    styles = []
    params = {}
    align = None
    level = 0

    # ---- STRUCTURE (#) ----
    if header.startswith("#"):

        for c in header:
            if c == "#":
                level += 1
            else:
                break

        structure = "heading"
        header = header[level:]


    # ---- STYLES (_ ** etc.) ----
    styles, header = extract_styles(header)


    # ---- ALIGN (>< >> <<) ----
    if header.startswith("><"):
        align = "center"
        header = header[2:]

    elif header.startswith(">>"):
        align = "right"
        header = header[2:]

    elif header.startswith("<<"):
        align = "left"
        header = header[2:]


    # ✅ IMPORTANT : nettoyer après align
    header = header.strip()


    # ---- PARAMS ({...}) ----
    while True:
        new_params, new_header = extract_param(header)

        if not new_params:
            break

        params.update(new_params)
        header = new_header.strip()


    # ---- CONTENT ----
    content = header.strip()


    # ---- RESULT ----
    return {
        "type": "block",
        "structure": structure,
        "level": level,
        "styles": styles,
        "params": params,
        "align": align,
        "content": content,
        "raw": line
    }
