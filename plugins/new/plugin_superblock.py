# -*- coding: utf-8 -*-
"""
Moteur OMEGA - Plug-in Super-bloc de Portée 1 (plugin_superblock.py)
Version : 3.0-Production

Gère le cycle de vie de la section globale du document (&&&[config] ... &&&).
"""

from plugins.plugin_font import extract_font_config

def parse_superblock(lines, current_index, parse_line_fn, parse_block_fn):
    """
    Parcourt le fichier depuis l'ouverture du sur-bloc &&&[config]
    jusqu'à sa fermeture &&& ou la fin du document.
    """
    header_line = lines[current_index].rstrip()
    
    # Extraction de la configuration technique dans les crochets [config]
    clean_header = header_line[3:].lstrip() # On ignore '&&&'
    config, _ = extract_font_config(clean_header)
    
    nodes = []
    i = current_index + 1
    
    while i < len(lines):
        line = lines[i].rstrip()
        trimmed = line.strip()
        
        # Arrêt à la fermeture du sur-bloc
        if trimmed == "&&&":
            i += 1 # On consomme le marqueur de fin
            break
            
        # Si on rencontre un bloc multi-lignes interne (Niveau 2)
        if trimmed.startswith("&&") and not trimmed.startswith("&&&"):
            block_node, next_index = parse_block_fn(lines, i)
            nodes.append(block_node)
            i = next_index
            continue
            
        # Ligne de texte classique
        if trimmed:
            nodes.append(parse_line_fn(line))
        i += 1
        
    return {
        "type": "super_block",
        "config": config,
        "nodes": nodes
    }, i