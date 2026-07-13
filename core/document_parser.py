from parser import parse_line
from plugins.plugin_code import parse_code

def parse_document(text):
    lines = text.splitlines()
    nodes = []
    i = 0

    # =================================================================
    # 1. PREMIER PASSAGE : Construction des blocs et lignes
    # =================================================================
    while i < len(lines):
        line = lines[i]
        clean_line = line.strip()

        # ---- LIGNE VIDE ----
        if not clean_line:
            nodes.append({"type": "empty"})
            i += 1
            continue

        # ---- BLOCK CODE ----
        if clean_line.startswith("```"):
            node, i = parse_code(lines, i)
            nodes.append(node)
            continue

        # ---- BLOCK UMD MULTI-LIGNES ----
        if line.rstrip().startswith("&&"):
            from plugins.plugin_block import parse_block
            node, i = parse_block(lines, i)
            nodes.append(node)
            continue

        # ---- PARAGRAPHE STANDARD (REFLOW) ----
        current_node = parse_line(line)
        
        if nodes and nodes[-1].get("type") == "inline" and current_node.get("type") == "inline":
            nodes[-1]["segments"].append({"type": "break", "text": "\n"})
            nodes[-1]["segments"].extend(current_node.get("segments", []))
        else:
            nodes.append(current_node)
            
        i += 1

# =================================================================
# 2. DEUXIÈME PASSAGE : Propagation et Nettoyage des Styles
# =================================================================
    for node in nodes:
        if node.get("type") == "inline":
            active_styles = []
            active_params = {}
            cleaned_segments = []
        
            for seg in node.get("segments", []):
    
                # ---- 1. INTERCEPTION DES BALISES DE RESET DE STYLE {/} ----
                if seg.get("type") == "clear_style":
                    target = seg.get("target", "all")
                    print(f"Debug: Clear effectué. Active styles est maintenant : {active_styles}")
        
                    if target == "all": # Reçoit True -> Ne correspond pas !
                        active_styles.clear()
                        active_params.clear()
                    elif target == "color":
                        active_params.pop("color", None)
                    elif target == "underline":
                        active_styles = [s for s in active_styles if "underline" not in s]
                        active_params.pop("underline_color", None)
                    elif target == "strike":
                        active_styles = [s for s in active_styles if s != "strike"]
                        active_params.pop("strike_color", None)
                    elif target == "highlight":
                        active_styles = [s for s in active_styles if s != "highlight"]
                        active_params.pop("highlight_color", None)
            
                    # On ne l'ajoute pas à cleaned_segments (sa commande est consommée)
                    continue

                # ---- 2. RESET SUR SAUT DE LIGNE VIRTUEL ----
                if seg.get("type") == "break":
                    active_styles = []
                    active_params = {}
                    cleaned_segments.append(seg)
                    continue

                # ---- 3. PROPAGATION SUR LE TEXTE ----
                if seg.get("type") in ["styled", "text"]:
                    # ... Reste de ton code de propagation inchangé ...
                    cleaned_segments.append(seg)
                else:
                # Laisse passer les images, emojis, etc.
                    cleaned_segments.append(seg)
        
            # Application des segments nettoyés au paragraphe
            node["segments"] = cleaned_segments

    return {
        "type": "document",
        "children": nodes
    }