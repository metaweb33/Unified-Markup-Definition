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

    # --- NOTRE MACHINE D'ÉTAT GLOBALE ---
    # Ces variables vont retenir la couleur, le gras, le souligné, etc.
    # tout au long de la lecture du document.
    active_styles = []
    active_params = {}

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

        # ---- PARAGRAPHE STANDARD (AVEC REFLOW ET PROPAGATION D'ÉTAT) ----
        # 1. On récupère les lignes consécutives du paragraphe (ton code actuel)
        lines_to_group = []
        while i < len(lines) and not is_special_block(lines[i]):
            lines_to_group.append(lines[i])
            i += 1
            
        paragraph_segments = []
        for index, text_line in enumerate(lines_to_group):
            if index > 0:
                paragraph_segments.append({"type": "break", "text": "\n"})
            
            # On parse la ligne brute via ton système inline
            line_node = parse_line(text_line)
            
            if line_node and "segments" in line_node:
                # 2. RESOLUTION DE L'ETAT POUR CHAQUE SEGMENT DE LA LIGNE
                for seg in line_node["segments"]:
                    
                    # CAS A : C'est une balise d'arrêt ({/}, {/c}, etc.)
                    if seg["type"] == "clear_style":
                        target = seg.get("target", "all")
                        
                        if target == "all":
                            active_styles.clear()
                            active_params.clear()
                        elif target == "color":
                            if "color" in active_params: del active_params["color"]
                        elif target == "underline":
                            active_styles = [s for s in active_styles if not s.startswith("underline")]
                            if "underline_color" in active_params: del active_params["underline_color"]
                        elif target == "highlight":
                            if "highlight" in active_styles: active_styles.remove("highlight")
                            if "highlight_color" in active_params: del active_params["highlight_color"]
                        elif target == "font":
                            active_styles = [s for s in active_styles if s not in ("bold", "italic")]
                        
                        # Astuce : On ne met PAS ce segment dans l'AST final, 
                        # son travail de nettoyage est fait !
                        continue
                    
                    # CAS B : C'est un segment de texte stylé
                    elif seg["type"] == "styled":
                        # On extrait ce que la ligne vient de découvrir localement (ex: **gras**)
                        local_styles = seg.get("styles", [])
                        local_params = seg.get("params", {})
                        
                        # Si le segment apporte une nouvelle couleur ou un nouveau style persistant,
                        # on met à jour notre mémoire globale
                        if "color" in local_params:
                            active_params["color"] = local_params["color"]
                        if "underline_color" in local_params:
                            active_params["underline_color"] = local_params["underline_color"]
                        if "highlight_color" in local_params:
                            active_params["highlight_color"] = local_params["highlight_color"]
                            
                        for s in local_styles:
                            if s not in active_styles:
                                active_styles.append(s)

                        # On applique TOUTE la mémoire accumulée sur le segment final
                        seg["styles"] = list(active_styles)
                        seg["params"] = dict(active_params)
                        
                        paragraph_segments.append(seg)
                    
                    # CAS C : Autres segments (emojis, images...)
                    else:
                        paragraph_segments.append(seg)
            
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