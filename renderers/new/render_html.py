# -*- coding: utf-8 -*-
"""
Moteur OMEGA - Traducteur AST vers DOM HTML (render_html.py)
Version : 3.3-Production (Fidélité historique absolue aux spécifications UMD)

Ce module traduit l'Arbre de Syntaxe Abstraite (AST) de ton langage d'origine
en structures HTML robustes, réactives et hautement conformes à ta grammaire.
"""

from renderers.devicon_map import LANG_ALIAS

def render_document(doc):
    """Traduit l'arbre AST complet en une chaîne de blocs HTML."""
    html_parts = []
    for node in doc.get("children", []):
        result = render_node(node)
        if result is None:
            html_parts.append("")
        else:
            html_parts.append(result)
    return "".join(html_parts)

def render_image(node):
    """Rendu d'une entité Image sémantique."""
    src = node.get("src", "")
    alt = node.get("alt", "")
    width = node.get("width", "auto")
    height = node.get("height", "auto")
    # Gestion adaptative des tailles
    w_style = f"width: {width}px;" if width != "auto" and width.isdigit() else ""
    h_style = f"height: {height}px;" if height != "auto" and height.isdigit() else ""
    style_str = f' style="display: inline-block; vertical-align: middle; {w_style} {h_style}"'
    return f'<img src="{src}" alt="{alt}"{style_str} />'

def render_node(node):
    """Routeur de rendu principal selon le type du nœud sémantique."""
    if not node or "type" not in node:
        return ""

    t = node["type"]

    if t == "empty":
        return "<br/>"
        
    elif t == "image":
        return render_image(node)

    # 1. Portée 1 : Le Sur-bloc technique (Super Block)
    elif t == "super_block":
        config_styles = []
        config = node.get("config", {})
        
        # Extraction de la police globale définie par l'auteur
        if "font" in config:
            config_styles.append(f"font-family: '{config['font']}', sans-serif;")
            
        style_attr = f' style="{" ".join(config_styles)}"' if config_styles else ""
        
        # Sérialisation des configurations de thèmes de titres UMD pour le DOM
        data_attrs = []
        for k, v in config.items():
            safe_key = k.replace("#", "heading-")
            data_attrs.append(f'data-config-{safe_key}="{v}"')
        
        data_attr_str = " " + " ".join(data_attrs) if data_attrs else ""
        
        # Rendu récursif des nœuds enfants du sur-bloc
        inner_html = []
        for child in node.get("nodes", []):
            inner_html.append(render_node(child))
            
        return f'<section class="umd-super-block"{style_attr}{data_attr_str}>{"".join(inner_html)}</section>'
        
    # 2. Portée 2 : Le Bloc multi-lignes unifié (Multi-line Block)
    elif t == "multi_line_block":
        # Résolution du tag (titre sémantique ou paragraphe de bloc)
        tag = f"h{node['level']}" if node.get("level") else "div"
        styles_css = []
        
        if node.get("align"):
            styles_css.append(f"text-align: {node['align']};")
            
        params = node.get("params", {})
        if params and "color" in params:
            styles_css.append(f"color: {params['color']};")
        if params and "font" in params:
            styles_css.append(f"font-family: '{params['font']}', sans-serif;")

        # Injection des décorations physiques d'origine du bloc (ex: bold, italic, strike...)
        styles = node.get("styles", [])
        styles_css.append(build_css_from_umd_styles(styles))

        classes = ["umd-multi-block"]
        if node.get("style"):
            classes.append(f"umd-{node['style']}")
            
        classes_str = " ".join(classes)
        style_attr = f' style="{" ".join([s for s in styles_css if s])}"' if styles_css else ""
        
        html_lines = []
        for inline_node in node.get("lines", []):
            line_html = render_node(inline_node)
            html_lines.append(line_html if line_html else "")
            
        content_html = "<br/>".join(html_lines)
        return f"<{tag} class=\"{classes_str}\"{style_attr}>{content_html}</{tag}>"

    # 3. Portée 3 : Les paragraphes simples et titres
    elif t == "block" or t == "heading":
        tag = f"h{node['level']}" if node.get("level") and node.get("level") > 0 else "p"
        styles_css = []
        
        if node.get("align"):
            styles_css.append(f"text-align: {node['align']};")
            
        params = node.get("params", {})
        if params and "color" in params:
            styles_css.append(f"color: {params['color']};")
        if params and "font" in params:
            styles_css.append(f"font-family: '{params['font']}', sans-serif;")
            
        styles = node.get("styles", [])
        styles_css.append(build_css_from_umd_styles(styles))
        
        style_attr = f' style="{" ".join([s for s in styles_css if s])}"' if styles_css else ""
        
        # Rendu avec segments de mots si l'arbre est découpé, sinon texte brut d'origine
        if "segments" in node:
            html_parts = [render_segment(seg) for seg in node["segments"]]
            content = "".join(html_parts)
        else:
            content = node.get("content", "")
            
        return f"<{tag} class=\"umd-line\"{style_attr}>{content}</{tag}>"

    elif t == "separator":
        kind = node.get("kind")
        if kind == "line":
            return "<hr style='border: none; border-top: 1px solid #ccc; margin: 1em 0;'/>"
        elif kind == "dotted":
            return "<hr style='border: none; border-top: 1px dotted #888; margin: 1em 0;'/>"
        elif kind == "double":
            return "<hr style='border: none; border-top: 3px double #888; margin: 1em 0;'/>"
        elif kind == "dashed":
            return "<hr style='border: none; border-top: 1px dashed #888; margin: 1em 0;'/>"
        elif kind == "repeat":
            pattern = node.get("pattern", "")
            return f"""
            <div style="overflow: hidden; white-space: nowrap; user-select: none; margin: 1em 0; color: #666; font-family: monospace;">
                {"".join([pattern] * 150)}
            </div>
            """
        return "<hr/>"

    # 4. Bloc de Code Technique complet avec gouttière de ligne
    elif t == "code":
        lang_raw = node.get("language", "text").strip().lower()
        lang_id = LANG_ALIAS.get(lang_raw, lang_raw)
        display_name = lang_raw.upper() if lang_raw != "cpp" else "C++"
        
        icon_html = ""
        if lang_id != "text":
            icon_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{lang_id}/{lang_id}-original.svg"
            icon_html = f'<img src="{icon_url}" width="20" height="20" alt="" style="margin-right: 8px; display: inline-block; vertical-align: middle;"/>'
        
        escaped_code = node.get('content', '').replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines = escaped_code.split('\n')
        formatted_lines = []
        for line in lines:
            line_content = line if line != "" else "&nbsp;"
            formatted_lines.append(f'<span class="code-line">{line_content}</span>')
        
        gutter_and_code = "".join(formatted_lines)

        return (
            f'<div class="code-block-container" style="margin: 1.5em 0; border: 1px solid #ccc; border-radius: 6px; overflow: hidden; font-family: sans-serif; background-color: #ffffff; width: 100%; box-sizing: border-box; white-space: normal;">'
            f'<div class="code-block-header" style="background-color: #f6f8fa; padding: 6px 12px; border-bottom: 1px solid #ccc; display: flex; align-items: center; font-size: 0.85em; color: #444; font-weight: bold;">'
            f'{icon_html}<span style="display: inline-block; vertical-align: middle;">{display_name}</span>'
            f'</div>'
            f'<pre class="code-container"><code>{gutter_and_code}</code></pre>'
            f'</div>'
        )

    elif t == "inline" or t == "line":
        return render_inline(node)

    return ""

def render_inline(node):
    """Prend un nœud de type inline ou line et traduit son tableau de segments."""
    segments = node.get("segments", [])
    html_parts = []
    for seg in segments:
        if seg.get("type") == "break" or seg.get("type") == "newline":
            html_parts.append("<br/>")
            continue
        html_parts.append(render_segment(seg))
    return f'<div class="umd-line">{"".join(html_parts)}</div>'

def render_segment(seg):
    """Prend un segment de mot individuel et applique ses mises en forme locales."""
    if not seg:
        return ""

    t = seg.get("type")
    
    # Résolution automatique pour la tolérance aux formats d'AST si type est absent
    if not t and "text" in seg:
        if seg.get("styles") or seg.get("params"):
            t = "styled"
        else:
            t = "text"

    if t == "text":
        return seg.get("text", "")

    elif t == "styled" or t == "styled_text":
        styles = seg.get("styles", [])
        params = seg.get("params", {})
        
        css_styles = []
        css_styles.append(build_css_from_umd_styles(styles))
            
        if "color" in params:
            css_styles.append(f"color: {params['color']};")
        if "font" in params:
            css_styles.append(f"font-family: '{params['font']}', sans-serif;")
        if "size" in params:
            css_styles.append(f"font-size: {params['size']}px;")

        style_attr = f' style="{" ".join([s for s in css_styles if s])}"' if css_styles else ""
        
        classes = ["umd-styled"]
        for st in styles:
            classes.append(f"umd-{st}")
        if "color" in params:
            classes.append(f"umd-{params['color']}")
            
        class_attr = f' class="{" ".join(classes)}"'
        
        return f'<span{class_attr}{style_attr}>{seg.get("text", "")}</span>'

    elif t == "code_inline":
        content = seg.get("content", seg.get("text", ""))
        escaped_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<code class="inline-code">{escaped_content}</code>'

    elif t == "clear_style":
        return ""

    elif t == "image":
        return render_image(seg)

    elif t == "emoji":
        return seg.get("value", "")

    elif t == "icon":
        return f"[{seg.get('name')}]"

    return ""

def build_css_from_umd_styles(styles):
    """Traduit fidèlement les jetons de styles d'origine en propriétés CSS standards."""
    css_parts = []
    
    if "bold" in styles:
        css_parts.append("font-weight: bold;")
    if "italic" in styles:
        css_parts.append("font-style: italic;")
    if "underline" in styles:
        css_parts.append("text-decoration: underline;")
    if "strike" in styles or "strikethrough" in styles:
        css_parts.append("text-decoration: line-through;")
    if "highlight" in styles:
        css_parts.append("background: yellow;")
        
    # Styles de soulignements complexes natifs de tes plug-ins d'origine
    if "underline_double" in styles:
        css_parts.append("text-decoration-line: underline; text-decoration-style: double;")
    if "underline_bold" in styles:
        css_parts.append("text-decoration-line: underline; text-decoration-thickness: 4px;")
    if "underline_wavy" in styles:
        css_parts.append("text-decoration-line: underline; text-decoration-style: wavy;")
    if "underline_dot" in styles:
        css_parts.append("text-decoration-line: underline; text-decoration-style: dotted;")
    if "underline_dashdot" in styles:
        css_parts.append("text-decoration-line: underline; text-decoration-style: dashed;")
        
    return " ".join(css_parts)