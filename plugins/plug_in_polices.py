# -*- coding: utf-8 -*-
"""
Moteur OMEGA - Plug-in de Gestion des Polices et Crochets Techniques (plugin_font.py)
Version : 3.0-Production

Ce plug-in extrait et valide la configuration de police et les directives d'affichage
déclarées à l'intérieur de crochets [...] (ex: [font:arial h1:red_uu_><]).
"""

import re

def extract_font_config(text):
    """
    Extrait les propriétés techniques contenues dans des crochets [] en début de chaîne.
    Retourne un dictionnaire de configuration et le texte restant.
    """
    if text.startswith("[") and "]" in text:
        end = text.find("]")
        raw_content = text[1:end].strip()
        
        if not raw_content:
            return {}, text
            
        config = {}
        tokens = raw_content.split()
        
        for token in tokens:
            if ":" in token:
                key, val = token.split(":", 1)
                config[key.strip()] = val.strip()
            else:
                # S'il s'agit d'un mot seul (ex: [arial]), on le traite comme la police par défaut
                config["font"] = token
                
        return config, text[end+1:]
        
    return {}, text