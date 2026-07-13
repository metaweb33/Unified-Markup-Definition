from plugins.plugin_heading import parse_simple_heading
from plugins.plugin_inline import parse_inline

def parse_block(lines, current_index):
    header_line = lines[current_index].rstrip()
    
    # 1. On nettoie la tilde de début pour que ton heading extrait
    #  les styles
    clean_header = header_line[1:].lstrip()
    base_heading = parse_simple_heading(clean_header)
    
    lines_content = []
    i = current_index + 1  # On commence à la ligne juste après le header
    
    # 2. On parcourt les lignes jusqu'à trouver une tilde seule "~" 
    # ou la fin du fichier
    while i < len(lines):
        line = lines[i].rstrip()
        if line == "~":
            i += 1  # On consomme la tilde de fermeture
            break
        lines_content.append(lines[i])
        i += 1

    # 3. On enrichit le nœud AST
    base_heading["type"] = "multi_line_block"
    base_heading["lines"] = [parse_inline(l) for l in lines_content]
    base_heading["raw_lines"] = lines_content
    
    if "content" in base_heading:
        del base_heading["content"]

    # On renvoie le nœud généré ET le nouvel index pour la boucle principale
    return base_heading, i