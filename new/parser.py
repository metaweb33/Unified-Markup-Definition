# Parser principal UMD

import logging

from plugins.plugin_block import parse_block
from plugins.plugin_code import parse_code
from plugins.plugin_inline import parse_inline
from plugins.plugin_heading import parse_simple_heading
from plugins.plugin_toc import extract_toc_item
from plugins.plugin_separator import parse_separator

def is_special_block(line):
    """Détermine si une ligne est le début d'un bloc structurel ou spécial."""
    clean = line.strip()
    if not clean:
        return True
    if clean.startswith("```"):
        return True
    if line.rstrip().startswith("&&"):
        return True
    if clean.startswith("++"):
        return True
    if clean.startswith("#"):
        return True
    if clean.startswith("!["):
        return True
    return False

def parse_document(text):
    lines = text.splitlines()
    nodes = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ---- LIGNE VIDE ----
        if not line.strip():
            nodes.append({"type": "empty"})
            i += 1
            continue

        # ---- BLOCK CODE ----
        if line.strip().startswith("```"):
            node, i = parse_code(lines, i)
            nodes.append(node)
            continue

        # ---- BLOCK UMD MULTI-LIGNES ----
        if line.rstrip().startswith("&&"):
            from plugins.plugin_block import parse_block
            node, i = parse_block(lines, i)
            nodes.append(node)
            continue

        # ---- ANALYSE DE LA LIGNE (Séparateurs, Titres, Paragraphes) ----
        # parse_line va router la ligne vers le bon plugin (ex: parse_separator)
        current_node = parse_line(line)
        
        if current_node:
            # GESTION DU REFLOW : On fusionne uniquement si le nœud actuel 
            # ET le précédent sont du texte de type "inline".
            # Si current_node est un "separator", il passe directement dans le else.
            if nodes and nodes[-1].get("type") == "inline" and current_node.get("type") == "inline":
                # On ajoute un saut de ligne virtuel avant d'injecter la suite
                nodes[-1]["segments"].append({"type": "break", "text": "\n"})
                nodes[-1]["segments"].extend(current_node.get("segments", []))
            else:
                # C'est un séparateur, un bloc spécifique ou un nouveau paragraphe
                nodes.append(current_node)

        i += 1

        # ---- SIMPLE HEADING (TITRE) ----
        if line.strip().startswith("#"):
            nodes.append(parse_simple_heading(line))
            i += 1
            continue

        # ---- SEPARATEUR OU IMAGE ISOLEE ----
        if line.strip().startswith("++") or line.strip().startswith("!["):
            nodes.append(parse_line(line))
            i += 1
            continue

        # ---- LIGNES NORMALES (FUSION CONTINU / REFLOW) ----
        lines_to_group = []
        
        while i < len(lines):
            # Dès qu'on croise n'importe quel bloc spécial, on arrête l'accumulation
            if is_special_block(lines[i]):
                break
            lines_to_group.append(lines[i])
            i += 1
            
        # Reconstruction sécurisée du paragraphe
        paragraph_segments = []
        for index, text_line in enumerate(lines_to_group):
            if index > 0:
                paragraph_segments.append({"type": "break", "text": "\n"})
            
            line_node = parse_line(text_line)
            
            if line_node and "segments" in line_node:
                paragraph_segments.extend(line_node["segments"])
            elif line_node:
                paragraph_segments.append(line_node)

        nodes.append({
            "type": "inline",
            "segments": paragraph_segments
        })

    return {
        "type": "document",
        "children": nodes
    }

def parse_line(line, iterator=None):
    line = line.rstrip()

    result = parse_separator(line)
    if result:
        return result
    
    try:
        if not line:
            return {"type": "empty"}

        if iterator is not None:
            from plugins.plugin_block import parse_block
            return parse_block(line, iterator)

        if line.startswith("#"):
            return parse_simple_heading(line)

        toc_item, _ = extract_toc_item(line)
        if toc_item:
            return toc_item
        
        return parse_inline(line)
    
    except Exception as e:
        logging.error("Parser error: %s", e)
        return {
            "type": "error",
            "value": line,
            "error": str(e)
        }